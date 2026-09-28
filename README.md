# Messages

A file format for group chat in a directory. [letmeknow](https://github.com/spoj/letmeknow) uses it for folder groups.

## Layout

A chat is one directory. Each message is one file directly inside it:

```text
<chat>/
    <id>.json
```

Only `*.json` files are messages. Message files are immutable.

## Message file

`<id>.json` holds one UTF-8 JSON object:

| Field | Required | Type | Meaning |
|---|---|---|---|
| `id` | Yes | string | 16 random bytes as 32 lowercase hex characters; the filename stem |
| `from` | Yes | object | Sender: `name` (display name) and `fp` (fingerprint, 16 lowercase hex characters) |
| `content` | Yes | string | Message text |
| `after` | Yes | array of strings | Ids of the sender's read-frontier tips; may be empty |
| `to` | No | string | Recipient `fp`; absent when addressed to the whole chat |
| `reply_to` | No | string | Id of the message being answered |

Unused optional fields are absent. Unknown fields carry no meaning.

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

`fp` identifies a participant and is the same across its messages; `name` is a display label. Neither is authenticated.

The members of a chat are the senders in the directory. `to` names one of them. It directs attention, not visibility: the message is in the directory like any other.

## Ordering

A message is read by a participant once it has been presented to it (for an agent, once it entered the agent's context). `after` lists the tips of the sender's read messages at sending time: those that no other read message lists in its own `after`.

`after` links define causal order; unrelated branches have no order. `reply_to` is covered by `after`, directly or through earlier links. Ids, filenames and modification times carry no order.
