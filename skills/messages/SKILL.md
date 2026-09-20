---
name: messages
description: Set up file-based chat in a specified directory, including a self-contained README for participants. Use when asked to scaffold a chat that works through shared or eventually synced files without a required participant runtime.
---

# Messages

Set up the chat; participants follow its README without needing this skill.

1. Confirm the target directory, purpose, intended readers and contribution permissions. Inspect any existing contents before writing. Reuse an existing chat's instructions rather than resetting it; do not overwrite unrelated files. Ask only for missing facts needed to proceed.
2. Check the storage provider's access and sync arrangements. Different participants can use different local paths to the same directory. A local writable folder alone does not establish shared access or sync.
3. Read [CHAT.md](CHAT.md), copy it to the chat's `README.md`, and fill its header placeholders with confirmed facts. Create `messages/`. Keep the participant instructions self-contained and paths relative to the chat directory. Do not require a skill installation, particular OS, shell, language, daemon or atomic filesystem operation.
4. Verify the scaffold and report the participant-accessible location, remaining access questions and how to join: read `README.md`, then read, write and poll or wait for message files. Do not claim cross-device delivery or active monitoring without observing it.

Use existing storage and sync facilities; this skill does not supply transport. Do not change permissions, introduce a sync service or create synthetic chat messages without authorization. Keep participant details and access notes appropriate to the directory's audience. No shared append log, counter, participant registry or read-state file is needed.
