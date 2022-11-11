import subprocess
import argparse
import os

# bashCommand = "cwm --rdf test.rdf --ntriples > test.nt"
# process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
# output, error = process.communicate()
def sox_file(dir, new_root):
    rs = []
    file = ""
    bashCommand = f"sox --norm=-3 {file} -r 16k -c 2 /{output_dir}/{file}"
    for root, dirs, files in os.walk(dir):
        for name in files:
            filepath = root + os.sep + name
            if filepath.endswith(".wav"):
                # print(root, name)
                new_name = root.split(os.sep)
                # print(filepath)
                old_name = os.path.join(root, name)
                new_name = os.path.join(new_root, filepath.split(os.sep)[1])
                # os.rename(old_name, new_name)
                print(old_name, new_name)
                bashCommand = f"sox --norm=-3 {old_name} -r 16k -c 2 {new_name}"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                rs.append(new_name)
    return rs

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='input dir',
        default="./public_test_separated")
    parser.add_argument('--output_dir', help='output dir',
        default="./public_test_separated_optimized")
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    rs = sox_file(input_dir, output_dir)
    print(f"Processed {len(rs)} files")