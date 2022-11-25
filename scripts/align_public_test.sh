#!/bin/bash

INSTALL_DIR=/tmp/mfa
OUTPUT_DIR=./data/output/public_test_raw
mkdir `pwd`

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