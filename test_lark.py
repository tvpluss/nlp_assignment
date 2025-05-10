from lark import Lark

from Models.text_processing import postprocess_tokens, preprocess_query
from Models.parser import GrammarRelation, MaltParser
grammar = """
    start: WORD+
    WORD: CITY | NAME | NOUN | VERB | ADJ | ADV | CONJ | DET | PRON | PROPN | AIRLINE | PLANE | PUNCT | TIME | INTEGER | WH_TIME
    NAME: "hồ chí minh" | "hà nội" | "đà nẵng" | "huế" | "hải phòng" | "khánh hòa" | "hcm" | "hcmc"
    CITY: "tp." |  "thành phố"
    NOUN: "máy bay" | "hãng hàng không" | "giờ" | "thành phố" | "thời gian" | "tên" | "câu hỏi" | "chuyến bay" | "mã hiệu"
    VERB: "bay" | "đến" | "mất" | "có" | "không" | "xuất phát" | "hạ cánh ở" | "cất cánh" | "kể" | "phải" | "cho biết" | "ra"
    ADJ: "nào"
    ADV: "lúc" | "từ" | "hãy" | "mấy" | "của" | "là"
    CONJ: "và" | "nếu có" | "thì"
    DET: "các" | "những"
    PRON: "tôi" | "bạn" | "ai"
    PROPN: "vietjet air" | "vietnam airlines" | "vnairline"
    AIRLINE: "vietjet air" | "vietnam airlines" | "vnairline"
    PLANE: "vn1" | "vn2" | "vn3" | "vn4" | "vn5" | "vj1" | "vj2" | "vj3" | "vj4" | "vj5"
    TIME: INTEGER ":" INTEGER "hr"
    WH_TIME: "mấy giờ" | "bao lâu"
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
with open("Output/grammar_relation.txt", "w") as f:
    f.truncate(0)
with open("Input/query.txt", "r") as f:
    for line in f:
        if line == '\n':
            print('manual break')
            break
        try:
            print(f'line: {line}'.strip())
            preprocessed_query = preprocess_query(line)
            tokens = parser.lex(preprocessed_query)
            postprocessed_tokens = postprocess_tokens(tokens)
            print(f'preprocessed tokens: {postprocessed_tokens}')
            malt_parser = MaltParser(buffer=postprocessed_tokens)
            print('parsing')
            arcs = malt_parser.parse()

            grammar_relation = GrammarRelation(arcs)
            grammar_relation.parse()

            print('\n\n')

        except Exception as e:
            print(f'line {line} error: {e}')

