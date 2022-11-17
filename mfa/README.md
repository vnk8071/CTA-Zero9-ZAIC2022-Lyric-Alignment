# Zalo AI Challenge 2022 - Lyric Alignment

## Introduction

### Problem statement

Many of us love to sing along with songs in the way of our favorite singers in albums (karaoke style). To make it, we may need to remove the vocals of the singer(s) from the songs, then provide the lyrics aligned timely with the accompaniment sounds. There are various tools to remove vocals, but it is hard to align the lyrics with the song.

In this challenge, participants will build a model to align lyrics with a music audio.

- Input: a music segment (including vocal) and its lyrics.

- Output: start-time and end-time of each word in the lyrics.

### Dataset

[Training data]:
1057 music segments from ~ 480 songs.

Each segment is provided with an audio formatted as WAV file and a ground-truth JSON file which includes lyrics and aligned time frame of each single word as the above example.

[Testing data]:
Public test: 264 music segments from ~ 120 songs without aligned lyric files.

[Private test]: 464 music segments from ~ 200 songs without aligned lyric files.

### Evaluation

Accuracy of prediction will be evaluated using Intersection over Union (IoU).

IoU of prediction and the ground truth of an audio segment (𝑠𝑖) is computed by the following formula:

![sample](https://lh4.googleusercontent.com/KjnUk0C-1e3WeTcPDpUInuW2UiyD6cE4C-_QxS3_BHE_7DPnorqW0Idqyu-eI0jQJnRJkighZAwKuADEULbFRvShb5_qndoZemVd6E-aPly-mNR0w4fdKK4yLta1L8xJDcOGDMzOwrobMTCOYrOqPWhKGeLqAXpIkPizQli-qteq-pBSxxfUMqJsYuGd_-yxHIH8MBSaoA)

where 𝑚 is the number of tokens of 𝑠𝑖.

![IoU](https://lh3.googleusercontent.com/qRxfTCeuFVVp5FhOX07AKx3ijbq-Urtr6xPcVLlA8FTRDxKp4ztnFQrL3G4RgHBIQ5gowpgfT6Ba9Tvv0U3vl05C5f3sDaua5H00da_P71kE4yf5tBaTTHNpMlXO4jncAvZ-kRcBBp6dyEdswI80zY1cdyLUCLH2drybOnn0dOPPgf0v7kbcE-ayXWxNK46X)

Then the Final IoU of across all 𝑛 audio segments is the average of their corresponding IoUs:

## Installation

```
conda create -n lyric-alignment python=3.8
conda activate lyric-alignment
conda install -c conda-forge montreal-forced-aligner
conda install -c conda-forge python=3.8 kaldi sox librosa biopython praatio tqdm requests colorama pyyaml pynini openfst baumwelch ngram
```

## Download pre-trained model and dictionary for Vietnamese language

```
mfa models download acoustic vietnamese_mfa
mfa models download dictionary vietnamese_mfa
```

## Evaluate corpus

```
python validate.py validate data/train/train --dictionary_path vietnamese_mfa --acoustic_model_path vietnamese_mfa --config_path config/mfa_config.yaml --clean --overwrite
```

## Training

```
python train.py train data/train/train --dictionary_path models/vietnamese_mfa.dict --acoustic_model_path models/vietnamese_mfa.zip --output_directory output --config_path config/mfa_config.yaml --output_model_path output_model.zip --clean --overwrite
```

## Align

```
python align.py align data/train/train --dictionary_path vietnamese_mfa --acoustic_model_path vietnamese_mfa --output_directory ~/output --config_path config/mfa_config.yaml --clean --overwrite
```

## Post Process

if lyrics label is json (default is txt)

```
 python .\post_process.py --raw_aligned .\output_raw (csv format) --raw_lyric .\lyrics (txt or json) --output_dir .\output dir --mfa --input_label_type json
```

if merge blank, using

```
--merge_blank
--merge_stategy : vanilla or mean
```
