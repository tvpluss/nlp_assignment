dependency_parsing_file = 'Output/dependency_parsing.txt'
grammar_relation_file = 'Output/grammar_relation.txt'
arcs_file = 'Output/arcs.txt'
logical_form_file = 'Output/logical_form.txt'
class Relation:
    # A relation arc of left -> right
    def __init__(self, left: str, relation_name: str, right: str):
        self.left: str = left
        self.right: str = right
        self.relation_name: str = relation_name

    def __str__(self):
        return self.relation_name + "(" + self.left + "->" + self.right + ")"

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right
    
    def equals(self, left: str, right: str):
        return self.left == left and self.right == right

relations: list[Relation] = []
with open('Models/relations.txt', 'r') as f:
    for line in f:
        if line.strip() == '':
            break
        relate, left_val, right_val = line.strip().split(' ')
        relations.append(Relation(left_val, relate, right_val))
def find_relation(left: str, right: str) -> Relation | None:
    for relation in relations:
        if relation.equals(left, right):
            return relation
    return None


class MaltParser:
    def __init__(self, buffer: list[str]):
        self.stack = ['root']
        self.buffer = buffer
        self.arcs = []
        self.file_parsing = open(dependency_parsing_file, 'a')
        self.file_arcs = open(arcs_file, 'a')

    def write_to_parsing(self, content: str):
        print(content, file=self.file_parsing)

    def write_to_arcs(self, content: str):
        print(content, file=self.file_arcs)
    
    def is_head(self, w_i: str) -> bool:
        # skipp root (đi)
        if w_i == 'đi':
            return False
        for arc in self.arcs:
            if arc.right == w_i:
                return True
        return False
    
    def has_hidden_relation(self, w_i:str)->bool:
        for w_k in self.buffer:
            if find_relation(w_i, w_k) is not None:
                return True
        return False

    def reduce(self):
        # Pop the stack
        self.stack.pop()
        self.write_to_parsing(f"{'REDUCE ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
    def shift(self):
        # Move w_i to the stack
        self.stack.append(self.buffer[0])
        self.buffer = self.buffer[1:]

        self.write_to_parsing(f"{'SHIFT ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
    def left_arc(self, relation_name: str):
        '''
        Left-Arc adds a dependency arc from next to top and pops the stack;
        allowed only if top has no head.
        '''
        w_i = self.stack.pop()
        w_j = self.buffer[0]

        self.arcs.append(Relation(w_j, relation_name, w_i))
        self.write_to_parsing(f"{f'LA {relation_name} ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
    def right_arc(self, relation_name: str):
        '''
        Right-Arc adds a dependency arc from top and pops the stack;
        allowed only if top has no head.
        '''
        w_i = self.stack[-1]
        w_j = self.buffer[0]
        self.buffer = self.buffer[1:]

        self.stack.append(w_j)
        self.arcs.append(Relation(w_i, relation_name, w_j))
        self.write_to_parsing(f"{f'RA {relation_name} ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")


    def parse(self) -> list[Relation]:
        self.write_to_parsing(f"{'ACTION': <25} {'STACK': <40} {'BUFFER': <100} {'ARCS'}")
        self.write_to_parsing(
        f"{'':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
        index =0

        while 1:
            index+=1
            if len(self.buffer) == 0 or index >100:
                # The buffer is empty, the parsing is done
                self.write_to_parsing("\n")
                self.write_to_arcs(", ".join(str(arc) for arc in self.arcs) + "\n")
                return self.arcs
            
            w_i = self.stack[-1]
            w_j = self.buffer[0]

            right_rel = find_relation(w_i, w_j)
            left_rel = find_relation(w_j, w_i)

            # special case: 
            # <from> w_i <to>
            #  where w_i is a location
            #  w_i is already head, so we can reduce
            if self.is_head(w_i) and w_i in ['đà_nẵng', 'hồ_chí_minh', 'huế', 'thành_phố']:
                self.reduce()
            elif right_rel is None and left_rel is None:
                # Check if w_i still has hidden relation with words in the buffer
                if self.has_hidden_relation(w_i):
                    # w_i still has hidden relation with words in the buffer, so we can shift
                    self.shift()
                else:
                    # w_i has no hidden relation with words in the buffer, so we can reduce
                    self.reduce()
            else:
                # w_i has relation with w_j
                if right_rel is not None:
                    self.right_arc(right_rel.relation_name)
                else:
                    self.left_arc(left_rel.relation_name)
                
class Token:
    def __init__(self, word:str, type:str):
        self.word = word
        self.type = type
        self.children: list[Token] = []

    def __str__(self):
        return f'{self.word} ({self.type})'



class GrammarRelation:
    def __init__(self, arcs: list[Relation]):
        self.arcs = arcs
        self.file = open(grammar_relation_file, 'a')
    
    def write_to_file(self, content: str):
        print(content, file=self.file)

    def parse(self):
        # Handle which flight question first
        parsed_tree = Token('m1', 'ROOT')
        for arc in self.arcs:
            if arc.relation_name == 'which':
                parsed_tree.children.append(Token(arc.left, 'WHICH'))
                self.write_to_file(f'{str(arc): <40} -> (WHICH m1 {arc.left})')
            elif arc.relation_name == 'nsub':
                parsed_tree.children.append(Token(arc.left, 'LSUB'))
                self.write_to_file(f'{str(arc): <40} -> (m1 PRED {arc.left})(m1 LSUB {arc.right})')
            elif arc.relation_name == 'to-loc':
                has_city = False
                # check for city nmod
                if Relation(arc.right, 'nmod', 'thành_phố') in self.arcs:
                    has_city = True
                token = Token(arc.right, 'DEST')
                if has_city:
                    token.children.append(Token('thành_phố', 'CITY'))
                parsed_tree.children.append(token)
                self.write_to_file(f'{str(arc): <40} -> (m1 TO-LOC {'thành_phố-' if has_city else ''}{arc.right})')
            elif arc.relation_name == 'from-loc':
                has_city = False
                # check for city nmod
                if Relation(arc.right, 'nmod', 'thành_phố') in self.arcs:
                    has_city = True
                token = Token(arc.right, 'SOURCE')
                if has_city:
                    token.children.append(Token('thành_phố', 'CITY'))
                parsed_tree.children.append(token)
                self.write_to_file(f'{str(arc): <40} -> (m1 FROM-LOC {'thành_phố-' if has_city else ''}{arc.right})')
            elif arc.relation_name == 'run-time':
                parsed_tree.children.append(Token(arc.left, 'RUN-TIME'))
                self.write_to_file(f'{str(arc): <40} -> (m1 RUN-TIME {arc.left})')
            elif arc.relation_name == 'at-time':
                parsed_tree.children.append(Token(arc.right, 'AT-TIME'))
                self.write_to_file(f'{str(arc): <40} -> (m1 AT-TIME {arc.right})')
            elif arc.relation_name == 'wh-time':
                parsed_tree.children.append(Token('m1', 'WH-TIME'))
                self.write_to_file(f'{str(arc): <40} -> (WH-TIME m1)')
        self.write_to_file('\n')
        return parsed_tree

class LogicalForm:
    def __init__(self):
        # None mean not specified
        # start with ? mean requested
        # other mean given
        self.destination = None
        self.source = None
        self.run_time = None
        self.at_time = None
        self.which = None
    
    def __str__(self):
        return f'from {self.source} to {self.destination} arrival {self.at_time} flight_time {self.run_time} which {self.which}'
class ParseLogicalForm:
    def __init__(self, tree: Token):
        self.tree = tree
        self.file = open(logical_form_file, 'a')
    def write_to_file(self, content: str):
        print(content, file=self.file)

    def parse(self):
        # recursively parse the tree
        logical_form = LogicalForm()
        self.parse_tree(self.tree, logical_form)
        print(logical_form)
        self.write_to_file('\n')

    def parse_tree(self, node: Token, logical_form: LogicalForm, indent: int = 0):

        if node.type == 'WHICH':
            self.write_to_file(f'{indent * ' '}WH ?m1')
            logical_form.which = '?m1'
        elif node.type == 'LSUB':
            self.write_to_file(f'{indent * ' '}FLIGHT ?m1')
            logical_form.flight = '?m1'
        elif node.type == 'WH-TIME':
            self.write_to_file(f'{indent * ' '}RUN-TIME ?m1 ?t1')
            logical_form.run_time = '?t1'
        elif node.type == 'DEST':
            buffer = ""
            if len(node.children) > 0:
                buffer = f'{indent * ' '}DEST ?m1 CITY-{node.word}'
            else:
                buffer = f'{indent * ' '}DEST ?m1 {node.word}'
            self.write_to_file(buffer)
            logical_form.destination = node.word
            return
        elif node.type == 'SOURCE':
            buffer = ""
            if len(node.children) > 0:
                buffer = f'{indent * ' '}SOURCE ?m1 CITY-{node.word}'
            else:
                buffer = f'{indent * ' '}SOURCE ?m1 {node.word}'
            self.write_to_file(buffer)
            logical_form.source = node.word
            return
        elif node.type == 'AT-TIME':
            self.write_to_file(f'{indent * ' '}AT-TIME ?t1')
            logical_form.at_time = '?t1'
            return
        elif node.type == 'RUN-TIME':
            self.write_to_file(f'{indent * ' '}RUN-TIME ?m1 {node.word}')
            logical_form.run_time = node.word
            return
        if len(node.children) > 0:
            for child in node.children:
                self.parse_tree(child, logical_form, indent + 4)
