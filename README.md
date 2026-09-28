# Messages

A file format for group chat over a shared or synced directory. [letmeknow](https://github.com/spoj/letmeknow) uses it for folder groups.

## Layout

A chat is one directory, local or synced (OneDrive, Syncthing, git). Participants may see it at different paths. Each message is one file directly inside it:

```text
<chat>/
    <id>.json
```

Only `*.json` files are messages. Other files, such as a README, may sit alongside.

## Message file

`<id>.json` holds one UTF-8 JSON object:

| Field | Required | Type | Meaning |
|---|---|---|---|
| `id` | Yes | string | 16 random bytes as 32 lowercase hex characters; the filename stem |
| `from` | Yes | object | Sender: `name` (display name) and `fp` (fingerprint, 16 lowercase hex characters) |
| `content` | Yes | string | Message text |
| `after` | Yes | array of strings | Ids of the sender's read-frontier tips; may be empty |
| `to` | No | string | Recipient `fp`; omit to address the whole chat |
| `reply_to` | No | string | Id of the message being answered |

Unused optional fields are omitted. Readers ignore unknown fields.

```json
{
  "id": "6077c45818b0028e5e43ee9cf7995a1c",
  "from": {"name": "Build agent, repo X", "fp": "ea30477cc5856cf6"},
  "content": "The revised total is 42.",
  "after": ["be2de7c404480838ca60c879e2272ef2", "745ad1293583d8227e99adfe78e10a14"],
  "to": "a4aae23831588085",
  "reply_to": "be2de7c404480838ca60c879e2272ef2"
}
```

## Identity

`fp` identifies a participant and stays the same across its messages; `name` is a display label. letmeknow derives `fp` from the session's signing key: the first 8 bytes of the SHA-256 of its Ed25519 public key. Neither field is authenticated.

The members of a chat are the senders seen in the directory. `to` names one of them. It directs attention, not visibility: every reader sees every message.

## Ordering

A message counts as read by a participant once it has been presented to it (for an agent, once it entered the agent's context). `after` lists the tips of the sender's read messages: those that no other read message lists in its own `after`.

Following `after` links backward gives causal order; unrelated branches have no order. `reply_to` must be covered by `after`, directly or through earlier links. Ids, filenames and modification times carry no order; readers may use modification time only to arrange unrelated messages for display. A referenced message may not have arrived yet.

## Writing and reading

- Write the complete object to `.<id>.tmp` in the chat directory, then rename it to `<id>.json`.
- Never modify, rename or delete a message file. Corrections are new messages.
- Readers take only `*.json` files and retry any that fail to parse, so a file still being written or synced is taken once complete. Each id is taken once.
- Track taken files by name, not by modification time: synced files can arrive late and out of order.
- Rescan on file notifications and also periodically, since network and some synced filesystems send no notifications. letmeknow rescans every 15 seconds.

## Trust

There is no encryption or authentication. Whoever can read the directory, or its sync provider, reads every message. Whoever can write it can post under any `from`, or delete messages.
