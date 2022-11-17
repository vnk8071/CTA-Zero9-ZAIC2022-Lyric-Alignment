# %%file augmentation.py

import numpy as np
import librosa
import os
import argparse
import glob
import soundfile as sf
import shutil
from tqdm import tqdm

from joblib import Parallel, delayed

def load_audio_file(file_path, sr):
    data, _ = librosa.core.load(file_path, sr=sr)
    return data

def manipulate_pitch(data, sampling_rate, pitch_factor):
    return librosa.effects.pitch_shift(data, sr=sampling_rate, n_steps=pitch_factor)

def manipulate_speed(data, speed_factor):
    return librosa.effects.time_stretch(data,rate=speed_factor)

def augment(file_name):
  data = load_audio_file(f"{input_dir}\{file_name}.wav", sr)

  data_pitch = manipulate_pitch(data, sr, np.random.randint(-3, 3))
  sf.write(f"{output_dir}\{file_name}_manulated_pitch.wav", data_pitch, sr, subtype='PCM_24')
  data_speed = manipulate_speed(data, np.random.randint(2, 4))
  sf.write(f"{output_dir}\{file_name}_manulated_speed.wav", data_speed, sr, subtype='PCM_24')


  if not debug:
      shutil.copyfile(f"{input_dir}\{file_name}.wav", f"{output_dir}\{file_name}.wav")
      shutil.copyfile(f"{input_dir}\{file_name}.txt", f"{output_dir}\{file_name}.txt")

      shutil.copyfile(f"{input_dir}\{file_name}.txt", f"{output_dir}\{file_name}_manulated_pitch.txt")
      shutil.copyfile(f"{input_dir}\{file_name}.txt", f"{output_dir}\{file_name}_manulated_pitch.txt")
      shutil.copyfile(f"{input_dir}\{file_name}.txt", f"{output_dir}\{file_name}_manulated_speed.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='input dir',
        default="./data/data_seperated/train_seperated")
    parser.add_argument('--output_dir', help='output dir',
        default="./data/data_seperated/train_seperated_aug")
    parser.add_argument('--debug', action='store_true', help='debugging')
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    debug = args.debug

    sr = 16000
    file_names = [x.split("\\")[-1][:-4] for x in glob.glob(f"{input_dir}/*.wav")]

    # print(file_names)
    # for file_name in tqdm(file_names):
    #     agument(file_name)

    Parallel(n_jobs=-1)(delayed(augment)(file_name) for file_name in file_names)