from fandango.language.tree import DerivationTree
import re
def count_tables(tree: DerivationTree) -> int:
    sql_str = str(tree).lower()
    # Match table names after 'from' or 'join'
    tables = re.findall(r'\b(?:from|join)\s+([a-zA-Z_][\w]*)', sql_str)
    return len(tables)

def count_column_name(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("<column_name>")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)
