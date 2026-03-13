from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree

def count_xml_attribute(tree: DerivationTree) -> int:
    target = NonTerminal("<xml_attribute>")
    count = 0
    if tree.symbol == target:
        count += 1
    for child in tree.children:
        count += count_xml_attribute(child)
    return count

def helper_count_attributes(node: DerivationTree):
    target_open_tag = NonTerminal("<xml_open_tag>")
    total_attrs = 0
    total_tags = 0
    if node.symbol == target_open_tag:
        # count attributes in the <xml_attributes> subtree
        tag_attrs = sum(count_xml_attribute(child) for child in node.children)
        if tag_attrs > 0:
            total_attrs += tag_attrs
            total_tags += 1
    for child in node.children:
        a, t = helper_count_attributes(child)
        total_attrs += a
        total_tags += t
    return total_attrs, total_tags

def avg_attributes(tree: DerivationTree) -> float:
    total_attrs, total_tags = helper_count_attributes(tree)
    if total_tags == 0:
        return 0.0
    return total_attrs / total_tags

def depth(tree: DerivationTree) -> int:
    if not tree.children:
        return 1
    return 1 + max(depth(child) for child in tree.children)

def count_text(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("<text>")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)
