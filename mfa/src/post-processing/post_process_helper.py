# pylint: disable-all
import json
import pandas as pd
import argparse
import helpers
import os
import numpy as np
import tqdm

def merge(word, r, next_r, merge_strategy="vanilla", mfa=False):
    if merge_strategy == "vanilla":
        word["e"] = next_r.Begin
        if mfa:
            word["e"]*=1000
    elif merge_strategy == "mean":
        mean = (r.End + next_r.Begin) // 2
        # print(mean)
        if mfa:
            mean*=1000
        r.End = mean
        # next_r.Begin = mean
        word["e"] = mean
        return mean
    r_ = next_r.Begin
    r_ *= 1000 if mfa else 1
    return r_

def mapping_csv_and_lyrics(df, words):
    if len(df)>len(words):
        df = df.iloc[:len(words), : ]

    else:
        append_ = [{"Label":"","Begin":0,"End":0,"Type":"words"} for i in range(len(words) - len(df))]
        df = pd.concat([df, pd.DataFrame.from_records(append_)])
    return df


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def post_process(FILE_NAME, raw_output="./aligned_output", raw_lyric="./lyrics", output_dir="./output",
    merge_blank=False, merge_strategy="vanilla", mfa=False):

    if not (os.path.isdir(output_dir)):
        os.makedirs(output_dir)
    # FILE_NAME = FILE_NAME
    output_raw = pd.read_csv(f"./{raw_output}/{FILE_NAME}.csv")

    # output_raw = output_raw[output_raw.Type == "words"]

    lyric = helpers.read_lyrics(f"./{raw_lyric}/{FILE_NAME}.txt")
    words = lyric.split(" ")
    # try:
        
    #     output_raw["OG_word"] = words
    # except:
    #     output_raw = mapping_csv_and_lyrics(output_raw, words)
    #     print(len(output_raw), len(words), FILE_NAME)
    #     print(output_raw)
    #     output_raw["OG_word"] = words

    if len(words)!=output_raw.shape[0]:
        output_raw = mapping_csv_and_lyrics(output_raw, words)
    # print(output_raw.shape, len(words))
    output_raw["OG_word"] = words
    start_sentences_index = helpers.get_start_sentence_position(lyric)

    rs = []
    for i, e in enumerate(start_sentences_index):
        try:
            rows = output_raw.iloc[start_sentences_index[i]:
                start_sentences_index[i+1]]
        except Exception as ádasdasda:
            rows = output_raw.iloc[start_sentences_index[i]:]
        sequence = {}
        sequence["l"] = []

        # print(rows)
        merge_val = None
        for ii, r in rows.iterrows():
            word = {}
            word["d"] = f"{r.OG_word}"

            word["s"] = r.Begin
            if merge_blank and ii <= rows.tail(1).index.item()-1:
                if merge_val:
                    word["s"] = merge_val
                if r.End != output_raw.iloc[ii+1, :].Begin:
                    merge_val = merge(word, r, output_raw.iloc[ii+1, :],
                        merge_strategy)
                    if merge_strategy == "mean":
                        output_raw.iloc[ii+1, 0] = merge_val
                else:
                    word["e"] = r.End
            else:
                word["e"] = r.End
            if mfa:
                word["s"] *= 1000
                word["e"] *= 1000
            sequence["l"].append(word)
        sequence["s"] = rows.iloc[0].Begin
        sequence["e"] = max(rows.End.to_list())
        if mfa:
            sequence["s"]*=1000
            sequence["e"]*=1000
        rs.append(sequence)

    with open(f'./{output_dir}/{FILE_NAME}.json', 'w', encoding='utf-8') as f:
        json.dump(rs, f, ensure_ascii=False, indent=1, cls=NpEncoder)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--raw_aligned', help='raw algined',
#         default="./aligned_output")

#     parser.add_argument('--raw_lyric', help='raw lyric',
#         default="./lyrics")

#     parser.add_argument('--output_dir', help='raw lyric',
#         default="./output")

#     parser.add_argument('--merge_blank', action='store_true')
#     parser.add_argument('--merge_strategy', default="vanilla")

#     args = parser.parse_args()
#     raw_output = args.raw_aligned
#     raw_lyrics = args.raw_lyric
#     output = args.output_dir
#     merge_blank = args.merge_blank
#     merge_strategy = args.merge_strategy

#     print(f"Processing folder: {raw_output}")
#     file_names = [x.split("\\")[-1][:-4] for x in glob.glob(f"{raw_output}/*.csv")]
#     print(f"Merge strategy: {merge_strategy}" if merge_blank else "")
#     for f in tqdm(file_names):
#         post_process_helper.post_process(f, raw_output, raw_lyrics,
#                 output_dir=output,
#                 merge_blank=merge_blank,
#                 merge_strategy=merge_strategy)

#     for f in file_names:
#         if f.endswith("37303234365f3431"):
#             post_process_helper.post_process(f, raw_output, raw_lyrics,
#                 output_dir=output,
#                 merge_blank=merge_blank,
#                 merge_strategy=merge_strategy)

