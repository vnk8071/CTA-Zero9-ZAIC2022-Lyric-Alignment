#!/bin/bash

PUBLIC_TEST_OUTPUT_RAW=./data/output/public_test_raw
RAW_LYRIC_JSON=./data/public_test/json_labels
OUTPUT_DIR=./data/output/public_test_json

python ./utils/move_folders.py --source $PUBLIC_TEST_OUTPUT_RAW --destination $PUBLIC_TEST_OUTPUT_RAW
python remove_empty_folders.py --source $PUBLIC_TEST_OUTPUT_RAW

python ./mfa/src/post-processing/post_process.py --raw_aligned $PUBLIC_TEST_OUTPUT_RAW \
--raw_lyric $RAW_LYRIC_JSON \
--output_dir $OUTPUT_DIR \
--mfa --input_label_type json --merge_blank