from dataclasses import dataclass, field
from typing import Set, List, Dict

State = Set[str]

@dataclass
class Reader:
    value: str
    pos: str = 0

    @property
    def end(self):
        return self.pos >= len(self.value)
    
    def advance(self):
        if self.end:
            return
        
        self.pos += 1

    def read(self) -> str:
        if self.end:
            return None
    
        ch = self.value[self.pos]
        self.advance()

        return ch

    def peek(self) -> str:
        if self.end:
            return None

        return self.value[self.pos]


def parse_regex(value: str):
    return parse_alternative(Reader(value))

def parse_alternative(reader: Reader):
    node = parse_sequence(reader)

    while reader.peek() == "|":
        reader.advance()

        right = parse_sequence(reader)
        node = OrRegexNode(left=node, right=right)

    return node

def parse_sequence(reader: Reader):
    terms: list[RegexNode] = []

    while not reader.end and reader.peek() not in (")", "|"):
        terms.append(parse_term(reader))
    
    if not terms:
        return LeafRegexNode(value="")
    
    if len(terms) == 1:
        return terms[0]
    
    node, *terms = terms
    for other in terms:
        node = CatRegexNode(left=node, right=other)
    
    return node

def parse_term(reader: Reader):
    node = parse_factor(reader)

    while reader.peek() == "*":
        reader.advance()
        node = StarRegexNode(child=node)
    
    return node

def parse_factor(reader: Reader):
    if reader.peek() == "(":
        reader.advance()
        value = parse_alternative(reader)
        reader.advance()

        return value
    
    value = reader.read()
    return LeafRegexNode(value=value if value is not None else "")


class RegexNode:
    def __init__(self) -> None:
        self.firstpos: State = set()
        self.lastpos: State = set()
    
    def __str__(self) -> str:
        pass

    @property
    def firstpos(self) -> State:
        pass

    @property
    def lastpos(self) -> State:
        pass

    @property
    def nullable(self) -> bool:
        pass

    def followpos(self, followpos_table: Dict[str, State]=None) -> Dict[str, State]:
        pass

    def name_leaves(self, leaf_counter=0):
        pass

class CatRegexNode(RegexNode):
    def __init__(self, left: RegexNode=None, right: RegexNode=None):
        self.left: RegexNode = left
        self.right: RegexNode = right
    
    def __str__(self) -> str:
        return f"CatRegexNode(left={self.left}, right={self.right})"

    @property
    def firstpos(self) -> State:
        return self.left.firstpos if not self.left.nullable else self.left.firstpos.union(self.right.firstpos)

    @property
    def lastpos(self) -> State:
        return self.right.lastpos if not self.right.nullable else self.left.lastpos.union(self.right.lastpos)
    
    @property
    def nullable(self) -> bool:
        return self.left.nullable and self.right.nullable
    
    def followpos(self, followpos_table: Dict[str, State]=None) -> Dict[str, State]:
        if followpos_table is None: followpos_table = {}
        for i in self.left.lastpos:
            followpos_table[i] = followpos_table[i].union(self.right.firstpos)
        self.left.followpos(followpos_table)
        self.right.followpos(followpos_table)
        return followpos_table
    
    def name_leaves(self, leaf_counter=0, leaf_symbols=None):
        if leaf_symbols is None: leaf_symbols = {}
        leaf_counter, leaf_symbols = self.left.name_leaves(leaf_counter, leaf_symbols)
        leaf_counter, leaf_symbols = self.right.name_leaves(leaf_counter, leaf_symbols)
        return leaf_counter, leaf_symbols

class OrRegexNode(RegexNode):
    def __init__(self, left: RegexNode=None, right: RegexNode=None):
        self.left: RegexNode = left
        self.right: RegexNode = right
    
    def __str__(self) -> str:
        return f"OrRegexNode(left={self.left}, right={self.right})"
    
    @property
    def firstpos(self):
        return self.left.firstpos.union(self.right.firstpos)

    @property
    def lastpos(self):
        return self.left.lastpos.union(self.right.lastpos)
    
    @property
    def nullable(self):
        return self.left.nullable or self.right.nullable
    
    def followpos(self, followpos_table: Dict[str, State]=None) -> Dict[str, State]:
        if followpos_table is None: followpos_table = {}
        self.left.followpos(followpos_table)
        self.right.followpos(followpos_table)
        return followpos_table
    
    def name_leaves(self, leaf_counter=0, leaf_symbols=None):
        if leaf_symbols is None: leaf_symbols = {}
        leaf_counter, leaf_symbols = self.left.name_leaves(leaf_counter, leaf_symbols)
        leaf_counter, leaf_symbols = self.right.name_leaves(leaf_counter, leaf_symbols)
        return leaf_counter, leaf_symbols

class StarRegexNode(RegexNode):
    def __init__(self, child: RegexNode=None):
        self.child: RegexNode = child
    
    def __str__(self) -> str:
        return f"StarRegexNode(child={self.child})"
    
    @property
    def firstpos(self):
        return self.child.firstpos
    
    @property
    def lastpos(self):
        return self.child.lastpos
    
    @property
    def nullable(self):
        return True

    def followpos(self, followpos_table: Dict[str, State]=None) -> Dict[str, State]:
        if followpos_table is None: followpos_table = {}
        self.child.followpos(followpos_table)
        for i in self.child.lastpos:
            followpos_table[i] = followpos_table[i].union(self.child.firstpos)
        return followpos_table
    
    def name_leaves(self, leaf_counter=0, leaf_symbols=None):
        if leaf_symbols is None: leaf_symbols = {}
        leaf_counter, leaf_symbols = self.child.name_leaves(leaf_counter, leaf_symbols)
        return leaf_counter, leaf_symbols

class LeafRegexNode(RegexNode):
    def __init__(self, value: chr=None, leaf_number=0):
        self.value: chr = value
        self.leaf_number = leaf_number
    
    def __str__(self) -> str:
        return f"LeafRegexNode(value={self.value})"
    
    @property
    def firstpos(self):
        if self.value == "&": return set()
        return {self.leaf_number}
    
    @property
    def lastpos(self):
        if self.value == "&": return set()
        return {self.leaf_number}
    
    @property
    def nullable(self):
        return self.value == "&"

    def followpos(self, followpos_table: Dict[str, State]=None) -> Dict[str, State]:
        if followpos_table is None: followpos_table = {}
        return followpos_table
    
    def name_leaves(self, leaf_counter=0, leaf_symbols=None):
        if leaf_symbols is None: leaf_symbols = {}
        if self.value == "&": return leaf_counter, leaf_symbols
        leaf_counter += 1
        self.leaf_number = str(leaf_counter)
        leaf_symbols[str(leaf_counter)] = self.value
        return leaf_counter, leaf_symbols


if __name__ == "__main__":
    root = parse_regex("a(a*(bb*a)*)*|b(b*(aa*b)*)*")
    root = CatRegexNode(left=root, right=LeafRegexNode(value="#"))
    leaf_counter, leaf_symbols = root.name_leaves()

    followpos_table = {}
    for i in range(1, leaf_counter+1): followpos_table[str(i)] = set()
    
    root.followpos(followpos_table)
