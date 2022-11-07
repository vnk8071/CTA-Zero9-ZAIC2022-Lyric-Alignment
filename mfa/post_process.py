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

    args = parser.parse_args()
    raw_output = args.raw_aligned
    raw_lyrics = args.raw_lyric

    file_names = [x.split("\\")[-1][:-4] for x in glob.glob("./aligned_output/*.csv")]

    for f in tqdm(file_names):
        post_process_helper.post_process(f)
