import os
import argparse

def remove_empty_folders(path_abs):
    walk = list(os.walk(path_abs))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='og labels folder',
        default="./og_labels")

    args = parser.parse_args()
    root_dir = args.source
    remove_empty_folders(root_dir)