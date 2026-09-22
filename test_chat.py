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
        self.write(message_id(4), "sent public", sender=self.identity)
        self.write(message_id(5), "sent direct", sender=self.identity, to=self.other)
        self.chat = Chat(self.directory, self.identity)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, identifier, content, sender=None, **fields):
        message = {
            "from": sender or self.sender,
            "after": [],
            "content": content,
            **fields,
        }
        (self.directory / f"{identifier}.json").write_text(
            json.dumps(message), encoding="utf-8"
        )

    def test_view_commands_filter_messages(self):
        self.assertEqual(sum(map(self.chat.visible, self.chat.messages.values())), 5)

        self.chat.command("/view direct")

        self.assertTrue(self.chat.direct_only)
        self.assertEqual(sum(map(self.chat.visible, self.chat.messages.values())), 3)
        rendered = "\n".join(line for line, _ in self.chat.body_lines(80))
        self.assertIn("direct", rendered)
        self.assertIn("sent public", rendered)
        self.assertIn("sent direct", rendered)
        self.assertNotIn("    public", rendered)
        self.assertNotIn("    other", rendered)
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
        self.write(message_id(6), "new public")
        self.chat.scan()
        self.assertEqual(self.chat.status, "unchanged")

        self.write(message_id(7), "new direct", to=self.identity)
        self.chat.scan()
        self.assertEqual(self.chat.status, "1 new message")

    def test_at_name_sends_direct_without_switching_target(self):
        name = self.chat.names()[self.sender]
        self.chat.input = f"@{name} hello there"
        self.chat.cursor = len(self.chat.input)

        self.chat.submit()

        sent = [
            message
            for message in self.chat.messages.values()
            if message["from"] == self.identity and message["content"] == "hello there"
        ]
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0]["to"], self.sender)
        self.assertIsNone(self.chat.target)

    def test_history_and_readline_keys(self):
        for line in ("first", "second"):
            self.chat.input = line
            self.chat.cursor = len(line)
            self.chat.submit()
        self.chat.input = "draft"
        self.chat.cursor = len(self.chat.input)

        self.chat.key(curses.KEY_UP, 20)
        self.assertEqual(self.chat.input, "second")
        self.chat.key("\x10", 20)
        self.assertEqual(self.chat.input, "first")
        self.chat.key(curses.KEY_DOWN, 20)
        self.assertEqual(self.chat.input, "second")
        self.chat.key("\x0e", 20)
        self.assertEqual(self.chat.input, "draft")

        self.chat.input = "hello brave world"
        self.chat.cursor = len(self.chat.input)
        self.chat.key("\x17", 20)
        self.assertEqual(self.chat.input, "hello brave ")
        self.chat.key("\x01", 20)
        self.chat.key("\x0b", 20)
        self.assertEqual(self.chat.input, "")


if __name__ == "__main__":
    unittest.main()
