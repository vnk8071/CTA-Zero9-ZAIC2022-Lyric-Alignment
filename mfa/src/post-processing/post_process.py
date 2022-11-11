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
    args = parser.parse_args()
    raw_output = args.raw_aligned
    raw_lyrics = args.raw_lyric
    output = args.output_dir

    if not os.path.isdir(output):
        os.makedirs(output)

    print(raw_output)

    file_names = [x.split(os.sep) for x in glob.glob("{raw_output}\*.csv")]

    print(glob.glob("{raw_output}\*.csv"))
    for f in tqdm(file_names):
        post_process_helper.post_process(f, raw_output, raw_lyrics, output)
