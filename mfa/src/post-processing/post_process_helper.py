import json
import numpy as np
import pandas as pd
import argparse
from mfa.src import helpers
import os


def post_process(FILE_NAME, raw_output="./aligned_output", raw_lyric="./lyrics", output_dir="./output", merge_blank=False):
    if not (os.path.isdir(output_dir)):
        os.makedirs(output_dir)
    FILE_NAME = FILE_NAME
    output_raw = pd.read_csv(f"./{raw_output}/{FILE_NAME}.csv")

    output_raw = output_raw[output_raw.Type == "words"]

    lyric = helpers.read_lyrics(f"./{raw_lyric}/{FILE_NAME}.txt")

    try:
        words = lyric.split(" ")
        output_raw["OG_word"] = words
    except Exception as e:
        print(len(words), len(output_raw), FILE_NAME)
        print(words)
        print(output_raw)
    start_sentences_index = helpers.get_start_sentence_position(lyric)
    # print(output_raw)
    # print(lyric)
    # print(start_sentences_index)

    rs = []
    for i, e in enumerate(start_sentences_index):
        try:
            # print(start_sentences_index[i],start_sentences_index[i+1])
            rows = output_raw.iloc[start_sentences_index[i]:
                start_sentences_index[i+1]]
        except Exception as e:
            rows = output_raw.iloc[start_sentences_index[i]:]
        sequence = {}
        sequence["l"] = []
        # print(f"Len: {len(rows)}")
        # print(rows)
        for ii, r in rows.iterrows():
            word = {}
            word["d"] = f"{r.OG_word}"

            word["s"] = r.Begin * 1000
            if ii <= len(rows)-2:
                if r.End != output_raw.iloc[ii+1, :].Begin:
                    word["e"] = output_raw.iloc[ii+1, :].Begin * 1000
                else:
                    word["e"] = r.End * 1000
            else:
                word["e"] = r.End * 1000
            sequence["l"].append(word)
        sequence["s"] = rows.iloc[0].Begin * 1000
        sequence["e"] = rows.iloc[-1].End * 1000
        rs.append(sequence)

    with open(f'./{output_dir}/{FILE_NAME}.json', 'w', encoding='utf-8') as f:
        json.dump(rs, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='raw file name',
        default="37303134325f3137")
    args = parser.parse_args()

    post_process(args.file, raw_output="aligned_output", raw_lyric="aligned_output_test", output_dir="concac")
