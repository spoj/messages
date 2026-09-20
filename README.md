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
        <uuid>.json
```

The README contains the complete participant instructions, adapted from [CHAT.md](skills/messages/CHAT.md). It does not send participants back to the skill or require a particular OS, shell, language or daemon. Different machines can use different local paths to the same synced directory.

Each message is an immutable UTF-8 JSON file with a fresh random UUID filename. Required fields are `from` and `text`; replies can name an earlier file using `reply_to`. A timestamp is optional and does not establish ordering.

Readers track seen filenames locally, retry incomplete files and rescan after polling or waiting. Late files and replies arriving before their referenced messages are expected. No shared counter, append operation, lock, atomic rename, participant registry or shared read-state file is required.

## Limits

The existing storage provider must eventually deliver complete files intact. This skill does not install sync, change permissions or start background listeners by itself. Responsiveness depends on sync latency and participants actively checking for files.

Creating a message does not prove that someone has received or read it. Reconnecting participants reconstruct context before acting on earlier requests. Sender labels are not authentication, and everyone with directory read access can read the conversation.

[SKILL.md](skills/messages/SKILL.md) is the setup procedure. Ordinary participation needs only the generated chat README, not this repository or an installed skill.
