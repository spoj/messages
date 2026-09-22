import json
import runpy
import tempfile
import unittest
import uuid
from pathlib import Path

module = runpy.run_path(Path(__file__).with_name("chat"))
Chat = module["Chat"]
curses = module["curses"]


def message_id(number):
    return str(uuid.UUID(int=number))


class ChatViewTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.identity = message_id(100)
        self.sender = message_id(101)
        self.other = message_id(102)
        self.write(message_id(1), "public")
        self.write(message_id(2), "direct", to=self.identity)
        self.write(message_id(3), "other", to=self.other)
        self.chat = Chat(self.directory, self.identity)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, identifier, content, **fields):
        message = {
            "from": self.sender,
            "after": [],
            "content": content,
            **fields,
        }
        (self.directory / f"{identifier}.json").write_text(
            json.dumps(message), encoding="utf-8"
        )

    def test_view_commands_filter_messages(self):
        self.assertEqual(sum(map(self.chat.visible, self.chat.messages.values())), 3)

        self.chat.command("/view direct")

        self.assertTrue(self.chat.direct_only)
        self.assertEqual(sum(map(self.chat.visible, self.chat.messages.values())), 1)
        rendered = "\n".join(line for line, _ in self.chat.body_lines(80))
        self.assertIn("direct", rendered)
        self.assertNotIn("public", rendered)
        self.assertNotIn("other", rendered)
        self.chat.command("/view all")
        self.assertFalse(self.chat.direct_only)
        self.chat.command("/view")
        self.assertTrue(self.chat.direct_only)
        with self.assertRaisesRegex(ValueError, "usage"):
            self.chat.command("/view unknown")

    def test_f2_toggles_without_changing_input(self):
        self.chat.input = "draft"
        self.chat.cursor = len(self.chat.input)
        self.chat.panel = ("Panel", [])

        self.chat.key(curses.KEY_F2, 20)

        self.assertTrue(self.chat.direct_only)
        self.assertEqual(self.chat.input, "draft")
        self.assertEqual(self.chat.cursor, len("draft"))
        self.assertIsNone(self.chat.panel)

    def test_scan_counts_only_visible_messages(self):
        self.chat.command("/view direct")
        self.chat.status = "unchanged"
        self.write(message_id(4), "new public")
        self.chat.scan()
        self.assertEqual(self.chat.status, "unchanged")

        self.write(message_id(5), "new direct", to=self.identity)
        self.chat.scan()
        self.assertEqual(self.chat.status, "1 new message")


if __name__ == "__main__":
    unittest.main()
