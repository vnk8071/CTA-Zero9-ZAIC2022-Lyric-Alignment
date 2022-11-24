# 1. Set up

# 1.2 Get data for inference

The data for `public_test` and `private_test` are put in folder like this

```
root/
└── data/
    ├── public_test/
    │   ├── songs/
    │   │   ├── song_1.wav
    │   │   ├── song_2.wav
    │   │   └── ...
    │   ├── lyrics/
    │   │   ├── song_1.txt
    │   │   ├── song_2.txt
    │   │   └── ...
    │   └── lyrics_json/
    │       ├── song_1.json
    │       ├── song_2.json
    │       └── ...
    └── private_test/
        ├── songs/
        │   ├── song_1.wav
        │   ├── song_2.wav
        │   └── ...
        ├── lyrics/
        │   ├── song_1.txt
        │   ├── song_2.txt
        │   └── ...
        └── lyrics_json/
            ├── song_1.json
            ├── song_2.json
            └── ...
```

# 2. Inference on public test

Clean the bash script and set the execute permission

```
sed -i -e 's/\r$//' ./inference_public_test.sh
chmod +x ./inference_public_test.sh

sed -i -e 's/\r$//' ./postprocess_public_test.sh
chmod +x ./postprocess_public_test.sh
```

Align the public test, after done this step, output is still in the csv format, so we still need the post-processing to convert it to json and zip the submission

```
./inference_public_test.sh
```

Post processing, output in `data/output/public_test/`

```
./postprocess_public_test.sh
```

# 3. Inference on private test
