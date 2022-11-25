#!/bin/bash

PUBLIC_TEST_OUTPUT_RAW=./data/output/public_test_raw
RAW_LYRIC_JSON=./data/public_test/json_labels
OUTPUT_DIR=./data/output/public_test_json
OUTPUT_FILE=./data/output/public_test_submission.zip
python3 ./mfa/src/post-processing/post_process.py --raw_aligned $PUBLIC_TEST_OUTPUT_RAW \
--raw_lyric $RAW_LYRIC_JSON \
--output_dir $OUTPUT_DIR \
--mfa --input_label_type json --merge_blank

echo "Done processed, saved postprocessed in" $OUTPUT_DIR

zip $OUTPUT_FILE $OUTPUT_DIR

echo "Done processed, saved submission in" $OUTPUT_FILE