import os
import re

YES_RE = os.getenv("APPROVAL_YES_REGEX", r"(?i)\b(yes|yeah|yep|approve|upload|go ahead|post it)\b")
NO_RE  = os.getenv("APPROVAL_NO_REGEX",  r"(?i)\b(no|nope|don'?t|do not|stop|reject|not now)\b")

_yes = re.compile(YES_RE)
_no = re.compile(NO_RE)

def parse_approval_decision(transcript: str) -> str:
    if not transcript:
        return "unknown"
    if _no.search(transcript):
        return "no"
    if _yes.search(transcript):
        return "yes"
    return "unknown"
