#!/bin/bash

PUBLIC_TEST=./data/public_test
SONG_RAW_DIR=./data/public_test/songs
SONG_SEP_TEMP=./data/public_test/songs_seperated_tmp
SEPERATED_DATA_DIR=./data/public_test/songs_seperated
OPTIMIZED_DATA_DIR=./data/public_test/optimized

python ./demucs/seperate_vocal.py --input_dir $SONG_RAW_DIR --output_dir $SONG_SEP_TEMP
python ./demucs/rename_files.py --input_dir $SONG_RAW_DIR --output_dir $SEPERATED_DATA_DIR

mkdir $OPTIMIZED_DATA_DIR
echo "normalize audio clips to sample rate of 16k"
find  $SEPERATED_DATA_DIR "*.wav" -type f -execdir ffmpeg -i {} -ar 16000 -ac 1 -y  `pwd`/data/public_test/optimized/{} \;
echo "Number of clips" $(ls ./data/public_test/optimized | wc -l)

# mkdir $PUBLIC_TEST/optimized
cp $PUBLIC_TEST/labels/*txt $OPTIMIZED_DATA_DIR
# cp $PUBLIC_TEST/songs_seperated/* $PUBLIC_TEST/optimized 

echo "splitting audios and lyrics into folders..."
python ./utils/split_folders.py --input_dir $OPTIMIZED_DATA_DIR --output_dir $PUBLIC_TEST/optimized_splitted --amount_per_folder 25
echo "Number of folders" $(ls  $PUBLIC_TEST/optimized_splitted | wc -l)