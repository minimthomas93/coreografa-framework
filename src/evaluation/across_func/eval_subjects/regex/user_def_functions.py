import re

def count_pattern_tokens(tree):
    pattern = str(tree).strip()
    tokens = re.findall(r'\[[^\]]+\]|\([^\)]+\)|\w|\W', pattern)
    return len(tokens)


def count_term(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("<term>")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)
