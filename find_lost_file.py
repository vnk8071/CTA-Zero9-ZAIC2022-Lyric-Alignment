import os
import argparse

def get_list_file(dir):
    rs = []
    for root, dirs, files in os.walk(dir):
        for name in files:
            filepath = root + os.sep + name
            if filepath.endswith(".wav"):
                rs.append(name)
    return rs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder_1', help='input dir',
        default="./train_separated")
    parser.add_argument('--folder_2', help='output dir',
        default="./songs")
    args = parser.parse_args()
    folder_1 = args.folder_1
    folder_2 = args.folder_2

    files_2 = get_list_file(folder_1)
    files_1 = get_list_file(folder_2)

    rs = list(set(files_1) - set(files_2))
    print(rs)
    # # rs = sox_file(folder_1, folder_2)
    # print(f"Processed {len(rs)} files")