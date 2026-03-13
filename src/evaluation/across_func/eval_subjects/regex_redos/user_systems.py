import re
import regex

def redos_match(tree):
    try:
        text = str(tree)
        return bool(re.match(r"^(a|aa)+$", text))
    except re.error:
        return False

def not_redos_match(tree):
    try:
        text = str(tree)
        return bool(re.match(r"^a+$", text))
    except re.error:
        return False