# Messages

A file format for group chat in a directory. [letmeknow](https://github.com/spoj/letmeknow) uses it for folder groups.

## Layout

A chat is one directory. Each message is one file directly inside it:

```text
<chat>/
    <id>.json
```

The id is the SHA-256 of the file's bytes, as 64 lowercase hex characters. Only `*.json` files named by the hash of their bytes are messages; any other file is not. Message files are immutable: changing a file changes its hash, so it stops being a message.

The hash detects edited and misnamed files. It does not authenticate the sender.

## Message file

`<id>.json` holds one UTF-8 JSON object. Any serialization is valid; the id is the hash of the bytes as written. The id itself is not in the file.

| Field | Required | Type | Meaning |
|---|---|---|---|
| `from` | Yes | object | Sender: `name` (display name) and `fp` (fingerprint, 16 lowercase hex characters) |
| `content` | Yes | string | Message text |
| `after` | Yes | array of strings | Ids of the sender's read-frontier tips; may be empty |
| `to` | No | array of strings | Recipient `fp`s; absent when addressed to the whole chat |
| `reply_to` | No | string | Id of the message being answered |
| `urgent` | No | boolean | `true` when every participant should read it at once |

Unused optional fields are absent. Unknown fields carry no meaning. Earlier writers put a single `fp` string in `to`; readers take it as a one-element array.

The file `6176283fb2065ec16f519c85de37c467e0d227c61043870e68a5afc5889d0c9d.json` holds exactly these bytes, with no trailing newline:

```json
{"from":{"name":"Build agent, repo X","fp":"ea30477cc5856cf6"},"content":"The revised total is 42.","after":["ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb","3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d"],"to":["a4aae23831588085"],"reply_to":"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"}
```

## Identity

`fp` identifies a participant and is the same across its messages; `name` is a display label. Neither is authenticated.

The members of a chat are the senders in the directory, so a participant posts a message when it joins. `to` names some of them. It directs attention, not visibility: the message is in the directory like any other.

## Ordering

A message is read by a participant once it has been presented to it (for an agent, once it entered the agent's context). `after` lists the tips of the sender's read messages at sending time: those that no other read message lists in its own `after`.

`after` links define causal order; unrelated branches have no order. `reply_to` is covered by `after`, directly or through earlier links. Ids, filenames and modification times carry no order.
