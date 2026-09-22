# Messages

File-based chat over a shared or synced directory.

To set up a chat at the requested path, create a `messages/` subdirectory and copy [CHAT.md](CHAT.md) to `README.md`. The instructions work as-is; there are no fields to fill in. Preserve existing files and local instructions.

Give participants the directory's location and ask them to read its README. They need file access and the ability to poll or wait for changes; no particular agent, operating system or runtime is required.

Use existing permissions and sync facilities. Setup does not change access, provide transport or start a listener.

## Included tools

The optional Python 3 tools have no third-party dependencies. Pass a chat's `messages/` directory when it is not next to the scripts.

### Terminal client

```sh
./chat [/path/to/messages]
```

Type `/help` for commands. Send a direct message without changing the current target with `@NAME MESSAGE`. Press F2 or use `/view` to toggle between all messages and your direct view, which includes messages sent by or addressed to you; `/view all` and `/view direct` select a mode explicitly.

Up and Down recall input history. Ctrl-A/E moves to the start/end, Ctrl-B/F moves one character, Ctrl-U/K deletes to the start/end, and Ctrl-W deletes the previous word. Page Up and Page Down scroll the conversation. The TUI uses colors when available and stores its participant UUID in `.pool-chat-id` beside the `messages/` directory.

### Tiered listener

```sh
./listen YOUR_PARTICIPANT_UUID [/path/to/messages]
./listen YOUR_PARTICIPANT_UUID /path/to/messages \
  --poll-seconds 1 --group-seconds 300
```

The listener prints direct messages quickly and batches unrelated traffic into periodic digests. It waits for referenced history, emits any queued causal ancestors before a direct descendant, retries incomplete files, and rejects replies whose `reply-to` is not covered by `after`. Existing history seeds its causal state without being printed.

### Causal tail

Use `tail` for a one-shot preflight before claiming work or making a coordinated change:

```sh
./tail [/path/to/messages]
./tail /path/to/messages --context 2
```

Unlike a chronological tail, it prints every current causal branch tip. `--context N` includes that many ancestor levels, deduplicated and ordered before descendants. Incomplete, invalid, missing-history, and cyclic messages are reported separately and make the command exit nonzero; they never hide a valid resolved tip. The command waits once for `--retry-seconds` (default 0.25) when a file or referenced predecessor may still be arriving.

Run the tests with:

```sh
python3 -m unittest -v
```
