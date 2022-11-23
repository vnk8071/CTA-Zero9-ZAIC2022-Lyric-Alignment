import shutil
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='input dir',
        default="./output/train_splitted")
    parser.add_argument('--destination', help='output dir',
        default="./output/train_splitted")
    args = parser.parse_args()
    source = args.source
    destination = args.destination

    # code to move the files from sub-folder to main folder.
    for d in os.listdir(source):
        files = os.listdir(os.path.join(source, d))
        for file in files:
            file_name = os.path.join(os.path.join(source, d), file)
            shutil.move(file_name, destination)
        print("Files Moved")