# pylint: disable-all
import json
import pandas as pd
import argparse
import helpers
import os
import numpy as np
import tqdm
import glob
import helpers

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

def merge_csv(rows, merge_strategy="vanilla", mfa=False):
    for i, r in rows.iterrows():
        if i < len(rows) -1 :
            if r.End != rows.iloc[i+1, :].Begin:
                # print(f"Before: \n", r)
                if merge_strategy == "vanilla":
                    rows.iloc[i, 1] = rows.iloc[i+1, :].Begin
                else:
                    tmp = (r.End + rows.iloc[i+1, :].Begin) / 2
                    rows.iloc[i, 1] = tmp #rows.iloc[i+1, :].Begin
                    rows.iloc[i+1, 0] = tmp
                # print(f"After: \n", r)
    return rows

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


def post_process(file_name, raw_output="./aligned_output", raw_lyric="./lyrics", output_dir="./output",
    merge_blank=False, merge_strategy="vanilla", mfa=False):

    if not (os.path.isdir(output_dir)):
        os.makedirs(output_dir)

    output_raw = pd.read_csv(f"./{raw_output}/{file_name}.csv")

    # output_raw = output_raw[output_raw.Type == "words"]

    lyric = helpers.read_lyrics(f"./{raw_lyric}/{file_name}.txt")
    words = lyric.split(" ")

    if len(words)!=output_raw.shape[0]:
        output_raw = mapping_csv_and_lyrics(output_raw, words)

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

        merge_val = None
        for ii, r in rows.iterrows():
            word = {}
            word["d"] = f"{r.OG_word}"
            word["s"] = r.Begin
            if merge_blank and ii <= rows.tail(1).index.item()-1:
                # if merge_val:
                #     word["s"] = merge_val
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

    with open(f'./{output_dir}/{file_name}.json', 'w', encoding='utf-8') as f:
        json.dump(rs, f, ensure_ascii=False, indent=1, cls=NpEncoder)

def post_process_json(file_name, raw_output="./aligned_output", raw_lyric="./json_lyrics", output_dir="./output",
    merge_blank=False, merge_strategy="vanilla", mfa=False, debug=False):


    if not (os.path.isdir(output_dir)):
        os.makedirs(output_dir)

    with open(f'{raw_lyric}/{file_name}.json', 'r', encoding="UTF-8") as f:
        label_json = json.load(f)

    output_raw = pd.read_csv(f"./{raw_output}/{file_name}.csv")

    output_raw = output_raw[output_raw.Type == "words"]

    if merge_blank:
        output_raw = merge_csv(output_raw, merge_strategy)
        if debug:
            print(output_raw)

    offset = 0

    try:
        for i, l in enumerate(label_json):
            # print(len(l["l"]))
            start, end = offset, len(l["l"]) + offset
            tmp_rows = output_raw.iloc[start:end]
            if debug:
                    print(tmp_rows)
            count_parenthesis = 0
            if helpers.check_sequence_valid(l["l"]) == 0:
                if debug:
                    print("there's is a empty sequence")
                continue
            for ii, ll in enumerate(l["l"]):
                if len(helpers.process_lyrics(ll["d"])) == 0:
                    if debug:
                        print("yes")
                        print(helpers.check_sequence_valid(l["l"]))
                    ii -= 1
                    count_parenthesis += 1
                    continue
                if debug:
                    print(ll["d"], tmp_rows.iloc[ii,:].Label)
                ll["s"] = tmp_rows.iloc[ii,:].Begin * (1000 if mfa else 1)
                ll["e"] = tmp_rows.iloc[ii,:].End * (1000 if mfa else 1)
                # if merge_blank and ii <= tmp_rows.tail(1).index.item()-1:
                #     # print(tmp_rows.tail(1).index.item())
                #     # if merge_val:
                #     #     word["s"] = merge_val
                #     if tmp_rows.iloc[ii,:].End != tmp_rows.iloc[ii+1, :].Begin:
                #         merge_val = merge(ll, tmp_rows, tmp_rows.iloc[ii+1, :],
                #             merge_strategy)
                #         # if merge_strategy == "mean":
                #         #     output_raw.iloc[ii+1, 0] = merge_val
                #     else:
                #         ll["e"] = tmp_rows.iloc[ii,:]
                # else:
                #     ll["e"] = tmp_rows.iloc[ii,:].End
            l["s"] = tmp_rows.iloc[0,:].Begin * (1000 if mfa else 1)
            l["e"] = tmp_rows.iloc[-1,:].End  * (1000 if mfa else 1)
            offset += (len(l["l"]) - count_parenthesis)
        with open(f'./{output_dir}/{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(label_json, f, ensure_ascii=False, indent=1, cls=NpEncoder)
    except Exception as e:
        print(e)
        print(file_name)
        print(len(output_raw))
        print(len(label_json))
        # print()

def post_process_json(file_name, raw_output="./aligned_output", raw_lyric="./json_lyrics", output_dir="./output",
    merge_blank=False, merge_strategy="vanilla", mfa=False, debug=False):

    if not (os.path.isdir(output_dir)):
        os.makedirs(output_dir)

    with open(f'{raw_lyric}/{file_name}.json', 'r', encoding="UTF-8") as f:
        label_json = json.load(f)

    output_raw = pd.read_csv(f"./{raw_output}/{file_name}.csv")

    output_raw = output_raw[output_raw.Type == "words"]

    if merge_blank:
        output_raw = merge_csv(output_raw, merge_strategy)
        if debug:
            print(output_raw)

    offset = 0

    try:
        for i, l in enumerate(label_json):
            # print(len(l["l"]))
            start, end = offset, len(l["l"]) + offset
            tmp_rows = output_raw.iloc[start:end]
            if debug:
                    print(tmp_rows)
            count_parenthesis = 0
            if helpers.check_sequence_valid(l["l"]) == 0:
                if debug:
                    print("there's is a empty sequence")
                continue
            for ii, ll in enumerate(l["l"]):
                if len(helpers.process_lyrics(ll["d"])) == 0:
                    if debug:
                        print("yes")
                        print(helpers.check_sequence_valid(l["l"]))
                    ii -= 1
                    count_parenthesis += 1
                    continue
                if debug:
                    print(ll["d"], tmp_rows.iloc[ii,:].Label)
                ll["s"] = tmp_rows.iloc[ii,:].Begin * (1000 if mfa else 1)
                ll["e"] = tmp_rows.iloc[ii,:].End * (1000 if mfa else 1)
                # if merge_blank and ii <= tmp_rows.tail(1).index.item()-1:
                #     # print(tmp_rows.tail(1).index.item())
                #     # if merge_val:
                #     #     word["s"] = merge_val
                #     if tmp_rows.iloc[ii,:].End != tmp_rows.iloc[ii+1, :].Begin:
                #         merge_val = merge(ll, tmp_rows, tmp_rows.iloc[ii+1, :],
                #             merge_strategy)
                #         # if merge_strategy == "mean":
                #         #     output_raw.iloc[ii+1, 0] = merge_val
                #     else:
                #         ll["e"] = tmp_rows.iloc[ii,:]
                # else:
                #     ll["e"] = tmp_rows.iloc[ii,:].End
            l["s"] = tmp_rows.iloc[0,:].Begin * (1000 if mfa else 1)
            l["e"] = tmp_rows.iloc[-1,:].End  * (1000 if mfa else 1)
            offset += (len(l["l"]) - count_parenthesis)
        with open(f'./{output_dir}/{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(label_json, f, ensure_ascii=False, indent=1, cls=NpEncoder)
    except Exception as e:
        print(e)
        print(file_name)
        print(len(output_raw))
        print(len(label_json))
        # print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_aligned', help='raw algined',
        default="./aligned_output")

    parser.add_argument('--raw_lyric', help='raw lyric',
        default="./lyrics")

    parser.add_argument('--output_dir', help='raw lyric',
        default="./output_test")

    parser.add_argument('--merge_blank', action='store_true')
    parser.add_argument('--merge_strategy', default="vanilla")
    parser.add_argument('--input_label_type', default="txt")
    parser.add_argument('--mfa', action='store_true')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    raw_output = args.raw_aligned
    raw_lyrics = args.raw_lyric
    output = args.output_dir
    merge_blank = args.merge_blank
    merge_strategy = args.merge_strategy
    input_label_type = args.input_label_type
    mfa = args.mfa
    debug = args.debug

    print(f"Processing folder: {raw_output}")

    file_names = [x.split(os.sep)[-1][:-4] for x in glob.glob(f"{raw_output}/*.csv")]
    print(f"Merge strategy: {merge_strategy}" if merge_blank else "")

    for f in file_names:
        if f.endswith("37303234365f3231"):
            if input_label_type == "json":
                post_process_json(f, raw_output, raw_lyrics,
                        output_dir=output,
                        merge_blank=merge_blank,
                        merge_strategy=merge_strategy,
                        mfa=mfa, 
                        debug=debug)

