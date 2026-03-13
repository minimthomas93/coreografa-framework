def sortedness(tree):
    sequence_as_str = str(tree)
    sequence_as_list = []
    for x in sequence_as_str.split(","):
        try:
            sequence_as_list.append(int(x.strip()))
        except ValueError:
            continue
    if len(sequence_as_list) < 2:
        return 1.0
    return sum(1 for i in range(len(sequence_as_list) - 1) if sequence_as_list[i] <= sequence_as_list[i + 1]) / max(1, (len(sequence_as_list) - 1))

def length(tree):
    sequence_as_str = str(tree)
    sequence_as_list = []
    for x in sequence_as_str.split(","):
        try:
            sequence_as_list.append(int(x.strip()))
        except ValueError:
            continue
    length_of_input = len(sequence_as_list)
    return length_of_input

def count_values(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("<values>")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)

def count_number(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("<number>")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)
