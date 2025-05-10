from lark import Lark

from Models.preprocessing import postprocess_tokens, preprocess_query
from Models.utils import GrammarRelation, MaltParser
grammar = """
    start: WORD+
    WORD: CITY | NOUN | VERB | ADJ | ADV | CONJ | DET | PRON | PROPN | AIRLINE | PLANE | PUNCT | NAME | TIME | HOUR | INTEGER
    NAME: "hồ chí minh" | "hà nội" | "đà nẵng" | "huế" | "hải phòng" | "khánh hòa" | "hcm" | "hcmc"
    CITY: "tp." |  "thành phố"
    NOUN: "máy bay" | "hãng hàng không" | "giờ" | "thành phố" | "thời gian" | "tên" | "câu hỏi" | "chuyến bay" | "mã hiệu"
    VERB: "bay" | "đến" | "mất" | "có" | "không" | "xuất phát" | "hạ cánh ở" | "cất cánh" | "kể" | "phải" | "cho biết" | "ra"
    ADJ: "nào"
    ADV: "lúc" | "bao lâu" | "từ" | "hãy" | "mấy" | "của" | "là"
    CONJ: "và" | "nếu" | "thì"
    DET: "các" | "những"
    PRON: "tôi" | "bạn" | "ai"
    PROPN: "vietjet air" | "vietnam airlines" | "vnairline"
    AIRLINE: "vietjet air" | "vietnam airlines" | "vnairline"
    PLANE: "vn1" | "vn2" | "vn3" | "vn4" | "vn5" | "vj1" | "vj2" | "vj3" | "vj4" | "vj5"
    HOUR: "hr"
    TIME: INTEGER ":" INTEGER
    INTEGER: /[0-9]+/
    PUNCT: "." | "?" | "," | "!"
    %ignore " "
"""

parser = Lark(grammar)
# clean up output file
with open("Output/parsing.txt", "w") as f:
    f.truncate(0)
with open("Output/arcs.txt", "w") as f:
    f.truncate(0)
with open("Output/tree.txt", "w") as f:
    f.truncate(0)
with open("Input/query.txt", "r") as f:
    for line in f:
        if line == '\n':
            print('manual break')
            break
        try:
            preprocessed_query = preprocess_query(line)
            tokens = parser.lex(preprocessed_query)
            postprocessed_tokens = postprocess_tokens(tokens)
            print(f'line: {line}')
            print(f'postprocessed_tokens: {postprocessed_tokens}')
            malt_parser = MaltParser(buffer=postprocessed_tokens)
            print('parsing')
            arcs = malt_parser.parse()

            grammar_relation = GrammarRelation(arcs)
            grammar_relation.build_tree()

        except Exception as e:
            print(f'line {line} error: {e}')

