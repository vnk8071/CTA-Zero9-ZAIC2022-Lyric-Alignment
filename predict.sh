#!/bin/bash

INSTALL_DIR=/tmp/mfa
PRIVATE_TEST=data/private_test
SONG_RAW_DIR=data/private_test/songs
RAW_LYRIC_JSON=data/private_test/sample_labels
SONG_SEP_TEMP=data/private_test/songs_seperated_tmp
SEPERATED_DATA_DIR=data/private_test/songs_seperated
OPTIMIZED_DATA_DIR=data/private_test/private_test_optimized
OPTIMIZED_SPLITTED_DATA_DIR=data/private_test/private_test_separated_optimized

OUTPUT_ROOT=./data/output_private_test
PRIVATE_TEST_OUTPUT_RAW=./data/output_private_test/private_test_raw
OUTPUT_DIR=./data/output_private_test/private_test_json

# echo "Extract public test sample"
# rm -rf data/
# mkdir data/
# unzip ./public_test_sample.zip -d $PUBLIC_TEST

start=$(date +%s)
# echo "Separate vocal from raw audio"
# python3 ./demucs_utils/seperate_vocal.py --input_dir $SONG_RAW_DIR --output_dir $SONG_SEP_TEMP
# python3 ./demucs_utils/rename_files.py --input_dir $SONG_SEP_TEMP --output_dir $SEPERATED_DATA_DIR

# mkdir $OPTIMIZED_DATA_DIR
# echo "Normalize audio clips to sample rate of 16k"
# for file in $SEPERATED_DATA_DIR/*.wav
# do
#     ffmpeg -i ${file} -ar 16000 -ac 1 -y  $OPTIMIZED_DATA_DIR/${file##*/}
# done

# echo "Number of clips" $(ls $OPTIMIZED_DATA_DIR | wc -l)

# python3 ./utils/process_label_to_txt.py --input_dir $RAW_LYRIC_JSON --output_dir $OPTIMIZED_DATA_DIR
# # cp $PUBLIC_TEST/labels/*txt $OPTIMIZED_DATA_DIR

# echo "splitting audios and lyrics into folders..."
# python3 ./utils/split_folders.py --input_dir $OPTIMIZED_DATA_DIR --output_dir $OPTIMIZED_SPLITTED_DATA_DIR --amount_per_folder 20
# echo "Number of folders" $(ls  $OPTIMIZED_SPLITTED_DATA_DIR | wc -l)

mkdir -p $PRIVATE_TEST_OUTPUT_RAW

# source $INSTALL_DIR/miniconda3/bin/activate aligner; \
python3 ./mfa/align.py align \
--corpus_directory $OPTIMIZED_SPLITTED_DATA_DIR \
--dictionary_path mfa/models/vietnamese_mfa_dict_ver3.dict \
--acoustic_model_path mfa/models/mfa_vn_vocal_train_combine_train_public_test.zip \
--config_path mfa/config/align_config.yaml \
--output_directory $PRIVATE_TEST_OUTPUT_RAW \
--output_format csv \
--debug \
-j 100

python3 ./utils/move_folders.py --source $PRIVATE_TEST_OUTPUT_RAW --destination $PRIVATE_TEST_OUTPUT_RAW
python3 ./utils/remove_empty_folders.py --source $PRIVATE_TEST_OUTPUT_RAW

# rm -r $SONG_SEP_TEMP
# rm -r $SONG_RAW_DIR

SUBMISSION_DIR=./result
mkdir $SUBMISSION_DIR

OUTPUT_FILE=./result/submission.zip
python3 ./mfa/src/postprocessing/post_process.py --raw_aligned $PRIVATE_TEST_OUTPUT_RAW \
--raw_lyric $RAW_LYRIC_JSON \
--output_dir $OUTPUT_DIR \
--mfa --input_label_type json --merge_blank

end=$(date +%s)
echo "Done processed, saved postprocessed in" $OUTPUT_DIR

zip -r -j $OUTPUT_FILE $OUTPUT_DIR

runtime=$((end-start))
echo "Total time inference: $runtime second"
echo "Output of submission will be saved in" $OUTPUT_FILE