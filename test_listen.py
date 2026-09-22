import contextlib
import io
import json
import runpy
import tempfile
import unittest
import uuid
from pathlib import Path

Listener = runpy.run_path(Path(__file__).with_name("listen"))["Listener"]


def message_id(number):
    return str(uuid.UUID(int=number))


class ListenerTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.identity = message_id(100)
        self.sender = message_id(101)
        self.root = message_id(1)
        self.write(self.root, [], "baseline")
        self.listener = Listener(self.directory, self.identity)
        with contextlib.redirect_stdout(io.StringIO()):
            self.listener.seed()

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, identifier, after, content, **fields):
        message = {
            "from": self.sender,
            "after": after,
            "content": content,
            **fields,
        }
        path = self.directory / f"{identifier}.json"
        path.write_text(json.dumps(message), encoding="utf-8")

    def scan(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.listener.scan()
        return output.getvalue()

    def test_direct_includes_queued_causal_context(self):
        parent = message_id(2)
        direct = message_id(3)
        self.write(parent, [self.root], "parent")
        self.assertEqual(self.scan(), "")
        self.write(direct, [parent], "child", to=self.identity)

        output = self.scan()

        self.assertLess(output.index(f"[context {parent}.json]"), output.index(f"[direct {direct}.json]"))
        self.assertEqual(self.listener.group, [])

    def test_missing_and_incomplete_predecessor_is_retried(self):
        predecessor = message_id(4)
        direct = message_id(5)
        self.write(direct, [predecessor], "child", to=self.identity)
        self.assertEqual(self.scan(), "")
        (self.directory / f"{predecessor}.json").write_text("{", encoding="utf-8")
        self.assertEqual(self.scan(), "")
        self.write(predecessor, [self.root], "late parent")

        output = self.scan()

        self.assertLess(
            output.index(f"[context {predecessor}.json]"),
            output.index(f"[direct {direct}.json]"),
        )

    def test_seed_suppresses_invalid_history(self):
        unrelated = message_id(6)
        invalid = message_id(7)
        self.write(unrelated, [], "unrelated")
        self.write(
            invalid,
            [self.root],
            "bad reply",
            **{"reply-to": unrelated},
        )
        listener = Listener(self.directory, self.identity)
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            listener.seed()

        self.assertEqual(output.getvalue(), "")
        self.assertIn(invalid, listener.rejected)

    def test_group_digest_and_invalid_reply_ancestry(self):
        unrelated = message_id(6)
        group = message_id(7)
        invalid = message_id(8)
        self.write(unrelated, [], "unrelated")
        self.assertEqual(self.scan(), "")
        self.write(group, [self.root], "group")
        self.assertEqual(self.scan(), "")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.listener.flush_group()
        self.assertIn("group digest: 2 causally ready messages", output.getvalue())
        self.write(
            invalid,
            [self.root],
            "bad reply",
            to=self.identity,
            **{"reply-to": unrelated},
        )
        self.assertIn(f"[invalid {invalid}.json]", self.scan())


if __name__ == "__main__":
    unittest.main()
