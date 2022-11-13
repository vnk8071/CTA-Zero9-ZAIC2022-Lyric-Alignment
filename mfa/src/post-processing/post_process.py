import json
import numpy as np
import pandas as pd
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

    parser.add_argument('--output_dir', help='raw lyric',
        default="./output")

    parser.add_argument('--merge_blank', action='store_true')
    parser.add_argument('--mfa', action='store_true')
    parser.add_argument('--merge_strategy', default="vanilla")

    args = parser.parse_args()
    raw_output = args.raw_aligned
    raw_lyrics = args.raw_lyric
    output = args.output_dir
    merge_blank = args.merge_blank
    merge_strategy = args.merge_strategy
    mfa = args.mfa

    print(f"Processing folder: {raw_output}")
    file_names = [x.split("\\")[-1][:-4] for x in glob.glob(f"{raw_output}/*.csv")]
    print(f"Merge strategy: {merge_strategy}" if merge_blank else "")

    for f in tqdm(file_names):
        post_process_helper.post_process(f, raw_output, raw_lyrics,
                output_dir=output,
                merge_blank=merge_blank,
                merge_strategy=merge_strategy,
                mfa=mfa)

    # for f in file_names:
    #     if f.endswith("3130303030365f3431"):
    #         post_process_helper.post_process(f, raw_output, raw_lyrics,
    #             output_dir=output,
    #             merge_blank=merge_blank,
    #             merge_strategy=merge_strategy)

