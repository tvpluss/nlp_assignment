dependency_parsing_file = 'Output/dependency_parsing.txt'
grammar_relation_file = 'Output/grammar_relation.txt'
arcs_file = 'Output/arcs.txt'
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
                

class GrammarRelation:
    def __init__(self, arcs: list[Relation]):
        self.arcs = arcs
        self.file = open(grammar_relation_file, 'a')
    
    def write_to_file(self, content: str):
        print(content, file=self.file)

    def parse(self):
        for arc in self.arcs:
            if arc.relation_name == 'which':
                self.write_to_file(f'{str(arc): <40} -> (WHICH m1 {arc.left})')
            elif arc.relation_name == 'nsub':
                self.write_to_file(f'{str(arc): <40} -> (m1 PRED {arc.left})(m1 LSUB {arc.right})')
            elif arc.relation_name == 'loc-obj':
                has_city = False
                # check for city nmod
                if Relation(arc.right, 'nmod', 'thành_phố') in self.arcs:
                    has_city = True
                # check if relation is from or to
                if arc.left in ['đến', 'ra']:
                    self.write_to_file(f'{str(arc): <40} -> (m1 TO-LOC {'thành_phố-' if has_city else ''}{arc.right})')
                else:
                    self.write_to_file(f'{str(arc): <40} -> (m1 FROM-LOC {'thành_phố-' if has_city else ''}{arc.right})')
                if has_city:
                    self.write_to_file(f'{str(Relation('thành_phố', 'nmod', arc.right)): <40}')
            elif arc.relation_name == 'at-time':
                self.write_to_file(f'{str(arc): <40} -> (m1 AT-TIME {arc.right})')
        self.write_to_file('\n')
               
