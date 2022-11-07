import json
import numpy as np
import re
import os
from tqdm import tqdm

input_folder = "data/train/labels"
output_folder = "data/train/lyrics"

def clean_word(word):
    word = re.sub(r'\W', '', word)
    return word

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for json_file in tqdm(os.listdir(input_folder)):
    words = []
    file_name = json_file.rsplit("/")[-1].split(".")[0]
    f = open(os.path.join(input_folder, json_file))
    json_file = json.load(f)

    for dct in json_file:
        words.extend([clean_word(word['d']) for word in dct['l']])

    with open (os.path.join(output_folder, file_name + ".lab"), "w") as out_f:
        out_f.write(" ".join(words))

print("DONE")