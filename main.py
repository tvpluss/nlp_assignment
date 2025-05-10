import py_vncorenlp

# Automatically download VnCoreNLP components from the original repository
# and save them in some local working folder
py_vncorenlp.download_model(save_dir='./')

# Load VnCoreNLP from the local working folder that contains both `VnCoreNLP-1.2.jar` and `models` 
rdrsegmenter = py_vncorenlp.VnCoreNLP(save_dir='./')
# Equivalent to: model = py_vncorenlp.VnCoreNLP(annotators=["wseg", "pos", "ner", "parse"], save_dir='/absolute/path/to/vncorenlp')

text = "Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây."
output = rdrsegmenter.word_segment(text)
print(output)
