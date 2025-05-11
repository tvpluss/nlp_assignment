
# NLP Assignment
BÀI TẬP LỚN MÔN HỌC XLNNTN LỚP CAO HỌC CNTT HK242
Trương Vĩnh Phước - 2470506
## Development
Develop on Mac M1, python 3.13.2
Using `lark` package to tokenize input to list of tokens, included in requirements.txt
## Quick run
Run
```bash
docker compose up --build -d
```
To run the assignment, the output is mount to Output/ folder
## Models
### equivalents.txt
- Contain equivalents to convert to normalized words for ease of development
Ex:
    - xuất_phát->bay
    - tp.->thành_phố

### parser.py
- Main file to hold logics, includes:
    - Malt Parser
    - Grammar Relation Parser
    - Logical Form Parser
    - Procedure Form Parser
- And other helper functions

### relations.txt
- Contain relations of all words that this assignment is working on (ex: đi, có, bao_lâu, hồ_chí_minh)
- Each line represent a relation, in the format of: \<relation> \<left_word> \<right_word> 
Ex:
    - root root đi
    - nmod hà_nội thành_phố
### text_processing.py
- Include function to preprocessing text before sending the token to parsers