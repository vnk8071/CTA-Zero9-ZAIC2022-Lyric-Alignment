import os
from tqdm import tqdm
from collections import Counter 

input_folder = "../data/public_test/lyrics"
output_folder = "output/check_words.txt"
lst_words = []

def check_word(lyric_file):
    # file_name = lyric_file.rsplit("/")[-1].split(".")[0]
    with open(os.path.join(input_folder, lyric_file)) as f:
        for line in f:
            lst_words.extend(line.split(" "))


if __name__ == '__main__':
    for lyric_file in tqdm(os.listdir(input_folder)):
        check_word(lyric_file)
    counter_words = Counter(lst_words)
    out_f = open(os.path.join(output_folder), "w")
    for key_val in enumerate(counter_words):
        out_f.writelines(f"{key_val[0]} - {key_val[1]} - {len(key_val[1])}\n") 