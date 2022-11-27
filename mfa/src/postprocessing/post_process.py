import json
import numpy as np
# import pandas as pd
import argparse
import helpers
import os
import glob
import post_process_helper
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_aligned', help='raw algined',
        default="./aligned_output")

    parser.add_argument('--raw_lyric', help='raw lyric',
        default="./lyrics")

    parser.add_argument('--output_dir', help='output dir',
        default="./output")

    parser.add_argument('--merge_blank', action='store_true')
    parser.add_argument('--mfa', action='store_true')
    parser.add_argument('--merge_strategy', default="vanilla")
    parser.add_argument('--input_label_type', default="txt")

    args = parser.parse_args()
    raw_output = args.raw_aligned
    raw_lyrics = args.raw_lyric
    output = args.output_dir
    merge_blank = args.merge_blank
    merge_strategy = args.merge_strategy
    mfa = args.mfa
    input_label_type = args.input_label_type

    print(f"Processing folder: {raw_output}")

    file_names = [x.split(os.sep)[-1][:-4] for x in glob.glob(f"{raw_output}/*.csv")]

    print(f"Merge strategy: {merge_strategy}" if merge_blank else "")

    for f in tqdm(file_names):
        try:
            if input_label_type == "json":
                post_process_helper.post_process_json(f, raw_output, raw_lyrics,
                        output_dir=output,
                        merge_blank=merge_blank,
                        merge_strategy=merge_strategy,
                        mfa=mfa)
            else:
                post_process_helper.post_process(f, raw_output, raw_lyrics,
                        output_dir=output,
                        merge_blank=merge_blank,
                        merge_strategy=merge_strategy,
                        mfa=mfa)
        except Exception as E:
            print(E)
            print(f)
            break

    # for f in file_names:
    #     if f.endswith("37303932305f3431"):
    #         post_process_helper.post_process(f, raw_output, raw_lyrics,
    #             output_dir=output,
    #             merge_blank=merge_blank,
    #             merge_strategy=merge_strategy,
    #             mfa=mfa)
