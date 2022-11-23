import os
import argparse
import numpy as np
import json

import re
import os
from tqdm import tqdm

# input_folder = "data/train/labels"
# output_folder = "data/train/lyrics"

def clean_word(word):
    word = re.sub(r'\W', '', word)
    return word

# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# for json_file in tqdm(os.listdir(input_folder)):
#     words = []
#     file_name = json_file.rsplit("/")[-1].split(".")[0]
#     f = open(os.path.join(input_folder, json_file))
#     json_file = json.load(f)

#     for dct in json_file:
#         words.extend([clean_word(word['d']) for word in dct['l']])

#     with open (os.path.join(output_folder, file_name + ".lab"), "w") as out_f:
#         out_f.write(" ".join(words))

# print("DONE")

# # Renaming the file
# os.rename(old_name, new_name)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='og labels folder',
        default="./og_labels")
    parser.add_argument('--output_dir', help='output folder',
        default="./output")

    args = parser.parse_args()
    root_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for json_file in tqdm(os.listdir(root_dir)):
        words = []
        file_name = json_file.rsplit("/")[-1].split(".")[0]
        f = open(os.path.join(root_dir, json_file), encoding="UTF-8")
        json_file = json.load(f)

        for dct in json_file:
            words.extend([clean_word(word['d']) for word in dct['l']])

        with open (os.path.join(output_dir, file_name + ".txt"), "w", encoding="UTF-8") as out_f:
            out_f.write(" ".join(words))

