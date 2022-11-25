import librosa
import pandas as pd
from tqdm import tqdm
import os

audio_dir = "data/public_test/public_test/songs"
lyric_dir = "data/public_test/public_test/lyrics"
output_dir = "mfa/output"

file_name_list = []
duration_list = []
channel_list = []
lyric_list = []

for file in tqdm(os.listdir(audio_dir)):
    file_name = file.split(".")[0]
    file_name_list.append(file_name)
    data, sr = librosa.load(os.path.join(audio_dir, file), mono=False)
    duration = librosa.get_duration(y=data, sr=sr)
    duration_list.append(duration)
    channel = "stereo" if data.shape[0] == 2 else "mono"
    channel_list.append(channel)
    with open(os.path.join(lyric_dir, file_name + ".txt")) as f:
        lyric = f.readline()
        lyric_list.append(lyric)
    
    eda = pd.DataFrame({
        "filename": file_name_list, 
        "duration": duration_list, 
        "channel": channel_list,
        "lyric": lyric_list,
        })
    eda.to_csv(os.path.join(output_dir, "EDA_public_test.csv"), index=False)