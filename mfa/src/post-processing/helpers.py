import re

def check_sequence_valid(l):
    return sum([len(process_lyrics(ll["d"])) != 0 for ll in l])

def check_start_sentence(word):
    return word[0].isupper()

def process_lyrics(text):
    text = re.sub(r"[(“)]", '', text)
    text = re.sub(r' +', ' ', text)
    # text = re.sub(r'.+', ' ', text)
    text = text.replace(".", "")
    text = text.strip()
    return text

def read_lyrics(path):
    """Doc con cac"""
    with open(path, "r", encoding="UTF-8") as file:
        line = file.read()
    return process_lyrics(line)

def get_start_sentence_position(line, condition=check_start_sentence):
    """Doc con cac"""
    return [i for i, elem in enumerate(line.split(" ")) if condition(elem)]