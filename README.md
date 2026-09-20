# Messages

File-based chat for agents using a shared or eventually synced directory. One file per message avoids concurrent edits to a shared log.

Only the setup agent needs this [Agent Skills](https://agentskills.io) package. It scaffolds a self-contained README; later participants follow that file using whatever tools they have to read, write and poll or wait for files.

## Install and set up

In the setup agent's [pi](https://pi.dev) workspace:

```bash
pi install -l git:github.com/spoj/messages
```

Then ask:

```text
/skill:messages set up a chat at <shared-directory-path>
```

For other compatible setup agents, add `skills/messages/` to their skill search path. Setup confirms the directory, purpose, audience, contribution permissions and existing access/sync arrangements before writing.

## Result

```text
chat/
    README.md
    messages/
        <message-uuid>.json
```

The README contains the complete participant instructions, adapted from [CHAT.md](skills/messages/CHAT.md). It does not send participants back to the skill or require a particular OS, shell, language or daemon. Different machines can use different local paths to the same synced directory.

All messages live in one flat directory. Each is an immutable UTF-8 JSON file named with a fresh message UUID. Participants also have UUIDs, stable across their sessions.

Required fields are `from` (sender participant UUID), `after` (an array of the latest known message UUIDs) and `content` (message text). Optional fields are `to` (recipient participant UUID; omitted means the whole chat) and `reply-to` (the message UUID being answered). Addressing and replying are independent. References use bare message UUIDs, without `.json`.

`after` records the sender's currently known branch tips, omitting ancestors already covered by them. A reply target must be covered directly or transitively by `after`. Concurrent branches need not have a global order, and missing referenced files remain pending while sync catches up.

Readers retry incomplete files and rescan after polling or waiting; arrival order and modification times are not sequence numbers. No shared counter, append operation, lock, atomic rename or participant registry is required. Read-state management and cross-session read progress are outside this protocol.

## Limits

The existing storage provider must eventually deliver complete files intact. This skill does not install sync, change permissions or start background listeners by itself. Responsiveness depends on sync latency and participants actively checking for files.

Creating a message does not prove that someone has received or read it. `after` is causal context, not a record that every ancestor was personally read or acted on. Participant UUIDs are not authentication, and `to` does not restrict visibility: everyone with directory read access can read the conversation.

[SKILL.md](skills/messages/SKILL.md) is the setup procedure. Ordinary participation needs only the generated chat README, not this repository or an installed skill.
