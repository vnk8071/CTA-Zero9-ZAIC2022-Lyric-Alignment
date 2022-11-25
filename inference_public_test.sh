#!/bin/bash

INSTALL_DIR=/tmp/mfa
PUBLIC_TEST=data/public_test
SONG_RAW_DIR=data/public_test/songs
SONG_SEP_TEMP=data/public_test/songs_seperated_tmp
SEPERATED_DATA_DIR=data/public_test/songs_seperated
OPTIMIZED_DATA_DIR=data/public_test/optimized
OPTIMIZED_SPLITTED_DATA_DIR=data/public_test/optimized_splitted

echo "Extract public test sample"
rm -rf data/
mkdir data/
unzip ./public_test_sample.zip -d $PUBLIC_TEST

echo "Separate vocal from raw audio"
python ./demucs/seperate_vocal.py --input_dir $SONG_RAW_DIR --output_dir $SONG_SEP_TEMP
python ./demucs/rename_files.py --input_dir $SONG_SEP_TEMP --output_dir $SEPERATED_DATA_DIR

mkdir $OPTIMIZED_DATA_DIR
echo "Normalize audio clips to sample rate of 16k"
for file in $SEPERATED_DATA_DIR/*.wav
do
    ffmpeg -i ${file} -ar 16000 -ac 1 -y  $OPTIMIZED_DATA_DIR/${file##*/}
done
# find  $SEPERATED_DATA_DIR -name "*.wav" -type f -exec sh -c "file=\"{}\" ; ffmpeg -i \"\$file\" -ar 16000 -ac 1 -y  $OPTIMIZED_DATA_DIR/${"\$file\"##/}" \;
echo "Number of clips" $(ls $OPTIMIZED_DATA_DIR | wc -l)

cp $PUBLIC_TEST/labels/*txt $OPTIMIZED_DATA_DIR

echo "splitting audios and lyrics into folders..."
python ./utils/split_folders.py --input_dir $OPTIMIZED_DATA_DIR --output_dir $PUBLIC_TEST/optimized_splitted --amount_per_folder 50
echo "Number of folders" $(ls  $PUBLIC_TEST/optimized_splitted | wc -l)

OUTPUT_DIR=./data/output/public_test_raw
mkdir -p $OUTPUT_DIR

source $INSTALL_DIR/miniconda3/bin/activate aligner; \
mfa align $OPTIMIZED_SPLITTED_DATA_DIR \
--dictionary_path vietnamese_mfa \
--acoustic_model_path vietnamese_mfa \
$OUTPUT_DIR \
--output_format csv \
--clean \
--overwrite \
--debug \
--beam 4000 \
--retry_beam 16000 \
--frame_length 20 \
--frame_shift 120

PUBLIC_TEST_OUTPUT_RAW=./data/output/public_test_raw
RAW_LYRIC_JSON=./data/public_test/json_labels
OUTPUT_DIR=./data/output/public_test_json

python ./utils/move_folders.py --source $PUBLIC_TEST_OUTPUT_RAW --destination $PUBLIC_TEST_OUTPUT_RAW
python ./utils/remove_empty_folders.py --source $PUBLIC_TEST_OUTPUT_RAW

rm -r $SONG_SEP_TEMP
rm -r $SONG_RAW_DIR

# python ./mfa/src/post-processing/post_process.py --raw_aligned $PUBLIC_TEST_OUTPUT_RAW \
# --raw_lyric $RAW_LYRIC_JSON \
# --output_dir $OUTPUT_DIR \
# --mfa --input_label_type json --merge_blank

# echo "please run the `postprocess_public_test.sh` for finalize the output"