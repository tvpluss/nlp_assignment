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
        relate, left_val, right_val = line.strip().split(' ')
        relations.append(Relation(left_val, relate, right_val))
def find_relation(left: str, right: str) -> Relation | None:
    for relation in relations:
        if relation.equals(left, right):
            return relation
    return None

print([relation.__str__() for relation in relations])


class MaltParser:
    def __init__(self, buffer: list[str]):
        self.stack = ['root']
        self.buffer = buffer
        self.arcs = []
        self.file_parsing = open('Output/parsing.txt', 'a')
        self.file_arcs = open('Output/arcs.txt', 'a')

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

    def reduce(self):
        # Pop the stack
        self.stack.pop()
        self.write_to_parsing(f"{'Reduce ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
    def shift(self):
        # Move w_i to the stack
        self.stack.append(self.buffer[0])
        self.buffer = self.buffer[1:]

        self.write_to_parsing(f"{'Shift ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
    def left_arc(self, relation_name: str):
        '''
        Left-Arc adds a dependency arc from next to top and pops the stack;
        allowed only if top has no head.
        '''
        w_i = self.stack.pop()
        w_j = self.buffer[0]

        self.arcs.append(Relation(w_j, relation_name, w_i))
        self.write_to_parsing(f"{'Left-Arc ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")
    
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
        self.write_to_parsing(f"{'Right-Arc ':<25}  {'[' + ', '.join(item for item in self.stack) + ']':<40} {'[' + ', '.join(item for item in self.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in self.arcs) + ']'}")


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

            if right_rel is None and left_rel is None:
                # Check if w_i is HEAD
                if self.is_head(w_i):
                    # w_i is HEAD, so we can reduce
                    self.reduce()
                else:
                    # w_i is not HEAD, so we can shift
                    self.shift()
            else:
                # w_i has relation with w_j
                if right_rel is not None:
                    self.right_arc(right_rel.relation_name)
                else:
                    self.left_arc(left_rel.relation_name)
                

class Token():
    def __init__(self, word, type):
        self.type = type
        self.word = word
        self.children = []

    def add(self, node_to_add):
        self.children.append(node_to_add)

    def __str__(self):
        if self.children:
            if "-from" in self.word:
                return "{} [{}]".format(self.type + " " + self.word[:-5],
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
            elif "-to" in self.word:
                return "{} [{}]".format(self.type + " " + self.word[:-3],
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
            else:
                return "{} [{}]".format(self.type + " " + self.word,
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
        else:
            if self.type != "<none>":
                if "-from" in self.word:
                    return "{}".format(self.type + " " + self.word[:-5])
                elif "-to" in self.word:
                    return "{}".format(self.type + " " + self.word[:-3])
                else:
                    return "{}".format(self.type + " " + self.word)
            else:
                return ""

class GrammarRelation:
    def __init__(self, arcs: list[Relation]):
        self.arcs = arcs
        self.file = open('Output/tree.txt', 'a')
               
    def build_tree(self):
        parent_name = child_name = None
        parent_node = child_node = None
        tree = {}
        for idx, arc in enumerate(self.arcs):
            if arc.relation_name == 'root':
                parent_name = arc.left
                child_name = arc.right
                parent_node = Token(parent_name, 'S')
                child_node = Token(child_name, 'V')
            elif arc.relation_name == 'nmod':
                parent_name = arc.left
                child_name = arc.right
                parent_node = Token(parent_name, 'N')
                child_node = Token(child_name, 'N')
            elif arc.relation_name == 'tmod':
                parent_name = arc.left
                child_name = arc.right
                parent_node = Token(parent_name, 'N')
                child_node = Token(child_name, 'T')
            elif arc.relation_name in ['dobj', 'nsub']:
                parent_name = arc.left
                child_name = arc.right
                parent_node = Token(parent_name, 'V')
                child_node = Token(child_name, 'N')
            else:
                print(f'unaccounted relation: {arc.relation_name}')
                pass
            # Add to the tree
            tree.setdefault(parent_name, parent_node)
            tree.setdefault(child_name, child_node)
            tree[parent_name].add(tree[child_name])
        
        # write to file
        print("S root [", file=self.file)
        print("SUBJ [" + str(tree["root"].children[0].children[0]) + "]", file=self.file)
        print("[MAIN-" + tree["root"].children[0].type + " " + tree["root"].children[0].word + "]",
              file=self.file)
        for i in range(1, len(tree["root"].children[0].children)):
            if str(tree["root"].children[0].children[i]) != "":
                print("[" + str(tree["root"].children[0].children[i]) + "]", file=self.file)
        print("]", file=self.file)

        
    
    

