import re
import uuid

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
FIELDS = {"from", "to", "reply-to", "after", "content"}
REQUIRED = {"from", "after", "content"}


def is_uuid(value):
    if not isinstance(value, str) or not UUID_RE.fullmatch(value):
        return False
    return str(uuid.UUID(value)) == value


def valid_message(message):
    if not isinstance(message, dict):
        return False
    if not REQUIRED <= message.keys() <= FIELDS:
        return False
    if not is_uuid(message["from"]) or not isinstance(message["content"], str):
        return False
    if "to" in message and not is_uuid(message["to"]):
        return False
    if "reply-to" in message and not is_uuid(message["reply-to"]):
        return False
    after = message["after"]
    return (
        isinstance(after, list)
        and all(is_uuid(item) for item in after)
        and len(after) == len(set(after))
    )
