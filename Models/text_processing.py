roots = ['đến', 'bay', 'xuất phát']
def preprocess_query(query: str) -> str:
    query = query.strip()
    query = query.lower()
    return query

def postprocess_tokens(tokens)->list[str]:
    tokens = [token.value.lower().replace(' ', '_') for token in tokens]
    tokens = normalize_text(tokens)
    tokens = clean_text(tokens)
    tokens = ensure_each_root_show_up_only_once(tokens)
    return tokens

def ensure_each_root_show_up_only_once(tokens: list[str]) -> list[str]:
    seen = set()
    filtered = []

    for token in tokens:
        if token not in roots:
            filtered.append(token)
        elif token not in seen:
            filtered.append(token)
            seen.add(token)
    return filtered


def have_root(text_list: list[str]) -> bool:
    # one ROOT: đi
    return 'đi' in text_list

def add_root(text_list: list[str]) -> list[str]:
    if not have_root(text_list):
        index = -1
        for i in range(len(text_list)):
            if text_list[i] in ['đến', 'từ', 'lúc', 'hết']:
                index = i
                break
        text_list.insert(index, 'đi')
    return text_list

removed_tokens = ['có', "không", "nếu_có", "thì", "là", ',']
def clean_text(texts: list[str]) -> list[str]:
    filtered_texts = [text for text in texts if text not in removed_tokens]
    return filtered_texts

def normalize_text(texts: list[str]) -> list[str]:
    '''
    Convert some word into normal form for easier to progress, the equivalent file is opened'''
    equivalents = dict()
    with open('Models/equivalents.txt', 'r') as f:
        for line in f:
            line = line.strip()
            rough_texts, normal_text = line.split('->')
            rough_texts = rough_texts.split(',')
            for rough_text in rough_texts:
                equivalents.setdefault(rough_text, normal_text)
    for i in range(len(texts)):
        if equivalents.get(texts[i]):
            texts[i] = equivalents[texts[i]]
    return texts