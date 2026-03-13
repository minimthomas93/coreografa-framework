import re
import regex

text = "ab"
def re_match(tree):
    try:
        pattern = str(tree)
        return bool(re.match(pattern, text))
    except re.error:
        return False

def regex_match(tree):
    try:
        pattern = str(tree)
        return bool(regex.match(pattern, text))
    except regex.error:
        return False