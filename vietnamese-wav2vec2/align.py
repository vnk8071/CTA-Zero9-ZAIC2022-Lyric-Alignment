from transformers.file_utils import cached_path, hf_bucket_url
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC, AutoTokenizer, Wav2Vec2ProcessorWithLM
import librosa
import os
import argparse
import pandas as pd
import torch
import numpy as np
import re
import json
from tqdm.auto import tqdm

from importlib.machinery import SourceFileLoader

def load_model_processor(model_name):
    processor = Wav2Vec2ProcessorWithLM.from_pretrained(model_name)
    # model = Wav2Vec2ForCTC.from_pretrained(model_name)
    model = SourceFileLoader("model", cached_path(hf_bucket_url(model_name,filename="model_handling.py"))).load_module().Wav2Vec2ForCTC.from_pretrained(model_name)
    model = model.to("cuda:0")
    return model, processor

def lyric_alignment(wav_dir, model, processor):
    wav, _ = librosa.load(os.path.join(wav_dir, wav_file), sr = 16000)
    input_values = processor.feature_extractor(wav, sampling_rate=16000, return_tensors="pt")
    input_values = input_values.to("cuda:0")

    logits = model(**input_values).logits[0]
    pred_ids = torch.argmax(logits, axis=-1)
    pred_transcript = processor.tokenizer.decode(pred_ids)
    print(f"transcript: {pred_transcript}")

    time_offset = model.config.inputs_to_logits_ratio / 16000

    outputs = processor.tokenizer.decode(pred_ids, output_word_offsets=True)
    lyric_offset = [
        {
            "Label": d["word"],
            "Begin": int(d["start_offset"] * time_offset * 1000),
            "End": int(d["end_offset"] * time_offset * 1000),
            "Type": "words"
    }
        for d in outputs.word_offsets
    ]
    return lyric_offset

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_wav', help='raw wav directory',
        default="")
    parser.add_argument('--model_name', help='raw algined',
        default="nguyenvulebinh/wav2vec2-large-vi-vlsp2020")
    parser.add_argument('--output_dir', help='output to save lyric alignment',
        default="./output_process")
    args = parser.parse_args()

    wav_dir = args.raw_wav
    model_name = args.model_name
    output_dir = args.output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    model, processor = load_model_processor(model_name)

    files = os.listdir(wav_dir)
    wav_files = [file for file in files if file.endswith("wav")]

    for wav_file in tqdm(wav_files):
        lyric_offset = lyric_alignment(wav_dir, model, processor)
        with open(os.path.join(output_dir, wav_file.rsplit(".")[0] + ".json"), "w") as outfile:
            json.dump(lyric_offset, outfile, indent=4)