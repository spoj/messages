import contextlib
import io
import json
import runpy
import tempfile
import unittest
import uuid
from pathlib import Path

module = runpy.run_path(Path(__file__).with_name("tail"))
Snapshot = module["Snapshot"]
report = module["report"]


def message_id(number):
    return str(uuid.UUID(int=number))


class TailTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.sender = message_id(100)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, identifier, after, content, **fields):
        message = {
            "from": self.sender,
            "after": after,
            "content": content,
            **fields,
        }
        (self.directory / f"{identifier}.json").write_text(
            json.dumps(message), encoding="utf-8"
        )

    def snapshot(self):
        snapshot = Snapshot(self.directory)
        snapshot.load()
        snapshot.resolve()
        return snapshot

    def test_parallel_tips_and_context(self):
        root = message_id(1)
        left = message_id(2)
        right = message_id(3)
        self.write(root, [], "root")
        self.write(left, [root], "left")
        self.write(right, [root], "right")

        snapshot = self.snapshot()
        tips, selected = snapshot.selected(1)

        self.assertEqual(tips, {left, right})
        self.assertEqual(selected, [root, left, right])
        self.assertEqual(snapshot.unresolved, {})

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            report(snapshot, 1)
        text = output.getvalue()
        self.assertIn("[causal tips: 2]", text)
        self.assertLess(text.index(f"[context {root}.json]"), text.index(f"[tip {left}.json]"))

    def test_missing_and_cyclic_history_is_unresolved(self):
        root = message_id(1)
        child = message_id(2)
        missing = message_id(3)
        cycle_a = message_id(4)
        cycle_b = message_id(5)
        self.write(root, [], "root")
        self.write(child, [missing], "missing parent")
        self.write(cycle_a, [cycle_b], "cycle a")
        self.write(cycle_b, [cycle_a], "cycle b")

        snapshot = self.snapshot()

        self.assertEqual(snapshot.tips(), {root})
        self.assertIn(missing, snapshot.unresolved[child])
        self.assertEqual(snapshot.unresolved[cycle_a], "causal cycle")
        self.assertEqual(snapshot.unresolved[cycle_b], "causal cycle")
        self.assertEqual(snapshot.missing_references(), {missing})

    def test_invalid_reply_blocks_descendants_without_hiding_valid_tips(self):
        root = message_id(1)
        unrelated = message_id(2)
        invalid_reply = message_id(3)
        descendant = message_id(4)
        self.write(root, [], "root")
        self.write(unrelated, [], "unrelated")
        self.write(
            invalid_reply,
            [root],
            "invalid reply",
            **{"reply-to": unrelated},
        )
        self.write(descendant, [invalid_reply, root], "descendant")

        snapshot = self.snapshot()

        self.assertEqual(
            snapshot.rejected[invalid_reply],
            "reply-to is not covered by after",
        )
        self.assertEqual(snapshot.tips(), {root, unrelated})
        self.assertNotIn(descendant, snapshot.resolved)
        self.assertEqual(snapshot.unresolved[descendant], f"waiting for {invalid_reply}")
        self.assertTrue(snapshot.has_problems())

    def test_invalid_and_incomplete_files_are_reported(self):
        invalid = message_id(1)
        incomplete = message_id(2)
        (self.directory / f"{invalid}.json").write_text("{}", encoding="utf-8")
        (self.directory / f"{incomplete}.json").write_text("{", encoding="utf-8")
        (self.directory / "not-a-uuid.json").write_text("{}", encoding="utf-8")

        snapshot = self.snapshot()

        self.assertIn(invalid, snapshot.invalid)
        self.assertIn(incomplete, snapshot.incomplete)
        self.assertNotIn("not-a-uuid", snapshot.invalid)


if __name__ == "__main__":
    unittest.main()
