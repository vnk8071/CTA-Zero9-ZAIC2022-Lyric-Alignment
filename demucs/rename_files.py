import os
import argparse


def move_files(dir, new_root):
    r = []
    print(dir)
    for root, dirs, files in os.walk(dir):
        for name in files:
            filepath = root + os.sep + name
            if not filepath.endswith("no_vocals.wav"):
                # print(root, name)
                new_name = root.split("\\")
                old_name = os.path.join(root, name)
                new_name = os.path.join(new_root, root.split("\\")[1]+".wav")
                os.rename(old_name, new_name)
                r.append(new_name)
    return r

# # Renaming the file
# os.rename(old_name, new_name)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='separated folder',
        default="./mdx_extra")
    parser.add_argument('--output_dir', help='output folder',
        default="./output")
    args = parser.parse_args()
    root_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    r = move_files(root_dir, output_dir)
    print(f"Successful move {len(r)} files")

