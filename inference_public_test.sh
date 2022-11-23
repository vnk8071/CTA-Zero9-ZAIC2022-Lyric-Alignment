#!/bin/bash

INSTALL_DIR=/tmp/mfa
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

OUTPUT_DIR=./data/output/public_test_raw
mkdir -p $OUTPUT_DIR

source $INSTALL_DIR/miniconda3/bin/activate aligner; \
mfa align ./data/public_test/optimized_splitted \
--dictionary_path vietnamese_mfa \
--acoustic_model_path vietnamese_mfa \
$OUTPUT_DIR \
--output_format csv \
--clean --overwrite \
--debug \
--beam 4000 \
--retry_beam 16000 \ --frame_length 20 --frame_shift 120

PUBLIC_TEST_OUTPUT_RAW=./data/output/public_test_raw
RAW_LYRIC_JSON=./data/public_test/json_labels
OUTPUT_DIR=./data/output/public_test_json

python ./utils/move_folders.py --source $PUBLIC_TEST_OUTPUT_RAW --destination $PUBLIC_TEST_OUTPUT_RAW
python remove_empty_folders.py --source $PUBLIC_TEST_OUTPUT_RAW

# python ./mfa/src/post-processing/post_process.py --raw_aligned $PUBLIC_TEST_OUTPUT_RAW \
# --raw_lyric $RAW_LYRIC_JSON \
# --output_dir $OUTPUT_DIR \
# --mfa --input_label_type json --merge_blank