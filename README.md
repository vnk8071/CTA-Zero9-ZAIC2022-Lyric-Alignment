# Zalo AI Challenge 2022 - Lyric Alignment

[**Introduction**](#introduction) | [**Dataset**](#dataset) | [**Evaluation Metric**](#evaluation-metric) | [**Solutions**](#solutions) < [**MFA**](#montreal-forced-aligner) | [**Transformers** ](#transformers)> | [**Leaderboard**](#leaderboard)
## Team members:
- Vu Xuan Hien <a href="https://github.com/XuanHien304">(Github)</a>
- Vo Nguyen Khoi (Me)
- Pham Bao Loc <a href="https://github.com/BaoLocPham">(Github)</a>

## Introduction
### Problem statement

Many of us love to sing along with songs in the way of our favorite singers in albums (karaoke style). To make it, we may need to remove the vocals of the singer(s) from the songs, then provide the lyrics aligned timely with the accompaniment sounds. There are various tools to remove vocals, but it is hard to align the lyrics with the song.

In this challenge, participants will build a model to align lyrics with a music audio.

- Input: a music segment (including vocal) and its lyrics.

- Output: start-time and end-time of each word in the lyrics.

## Dataset
[Training data]:
1057 music segments from ~ 480 songs.

Each segment is provided with an audio formatted as WAV file and a ground-truth JSON file which includes lyrics and aligned time frame of each single word as the above example.

[Testing data]:
Public test: 264 music segments from ~ 120 songs without aligned lyric files.

[Private test]: 464 music segments from ~ 200 songs without aligned lyric files.

## Evaluation Metric
Accuracy of prediction will be evaluated using Intersection over Union (IoU).

IoU of prediction and the ground truth of an audio segment (𝑠𝑖) is computed by the following formula:

![sample](https://lh4.googleusercontent.com/KjnUk0C-1e3WeTcPDpUInuW2UiyD6cE4C-_QxS3_BHE_7DPnorqW0Idqyu-eI0jQJnRJkighZAwKuADEULbFRvShb5_qndoZemVd6E-aPly-mNR0w4fdKK4yLta1L8xJDcOGDMzOwrobMTCOYrOqPWhKGeLqAXpIkPizQli-qteq-pBSxxfUMqJsYuGd_-yxHIH8MBSaoA)

where 𝑚 is the number of tokens of 𝑠𝑖.

![IoU](https://lh3.googleusercontent.com/qRxfTCeuFVVp5FhOX07AKx3ijbq-Urtr6xPcVLlA8FTRDxKp4ztnFQrL3G4RgHBIQ5gowpgfT6Ba9Tvv0U3vl05C5f3sDaua5H00da_P71kE4yf5tBaTTHNpMlXO4jncAvZ-kRcBBp6dyEdswI80zY1cdyLUCLH2drybOnn0dOPPgf0v7kbcE-ayXWxNK46X)

Then the Final IoU of across all 𝑛 audio segments is the average of their corresponding IoUs.

## Solutions
### Montreal Forced Aligner
The Montreal Forced Aligner is a command line utility for performing forced alignment of speech datasets using Kaldi (http://kaldi-asr.org/).

For details: <a href="https://github.com/vnk8071/CTA-Zero9-ZAIC2022-Lyric-Alignment/tree/master/mfa">MFA folder</a>
### Baseline on Public Test
- Use pre-trained model.
- Use upper case for split sequence.
- Add ending comma in each sequence.

Result:
<img src="images/baseline_mfa.jpg">

### Wav2Vec
The model first processes the raw waveform of the speech audio with a multilayer convolutional neural network to get latent audio representations of 25ms each. These representations are then fed into a quantizer as well as a transformer. The quantizer chooses a speech unit for the latent audio representation from an inventory of learned units. About half the audio representations are masked before being fed into the transformer. The transformer adds information from the entire audio sequence. Finally, the output of the transformer is used to solve a contrastive task. This task requires the model to identify the correct quantized speech units for the masked positions.

Source: https://ai.facebook.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/

For details: <a href="https://github.com/vnk8071/CTA-Zero9-ZAIC2022-Lyric-Alignment/tree/master/transformers">Transformers folder</a>

### Our pipeline
<img src="images/pipeline.jpg">
#1. Separate vocal

- We use Demucs of Facebook-research team for removing noise of raw audio.
- Use pre-trained model mdx_extra.

#2. Pre-process

- Normalize raw audio to 16k sample rate and convert to mono chanel.
- Strip special character and process with lower case.
- Convert number in lyric to string. 

#3. Model MFA | wav2vec

- We custom result inference of 2 models into same format: list of dictionary with 3 keys (word, start time, and end time)

#4. Post-process

- Merge time-step between 2 words 
- Map output into ground truth label (json format)

Running pipeline with bash script
```
sh ./predict.sh
```
### Improvement
- Separate vocal to remove noise.
- Merge time-step between 2 words.
- Fine-tuning hyper-parameters for Vietnamese dataset.
- Adapt new dataset from zing mp3.

## Leaderboard
Link: https://challenge.zalo.ai/portal/lyric-alignment/leaderboard