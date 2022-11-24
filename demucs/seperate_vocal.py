#@title Useful functions, don't forget to execute
import os
import io
from pathlib import Path
import select
# from shutil import rmtree
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO
import argparse


# Customize the following options!
model = "mdx_extra"
extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.
two_stems = 'vocals'   # only separate one stems from the rest, for instance
# two_stems = "vocals"

# Options for the output audio.
mp3 = False
mp3_rate = 320
float32 = True  # output as float 32 wavs, unsused if 'mp3' is True.
int24 = False 

def find_files(in_path):
    out = []
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
        p_stdout.fileno(): (p_stdout, sys.stdout),
        p_stderr.fileno(): (p_stderr, sys.stderr),
    }
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        if sys.platform == 'win32':
            ready = os.read(fds)
        else:
            ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()

def separate(in_path=None, out_path=None):
    # inp = inp 
    # out_path = out_path 
    cmd = ["python", "-m", "demucs.separate", "-o", str(out_path), "-n", model]
    # if mp3:
    #     cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
      cmd += [f"--two-stems={two_stems}"]
    files = [str(f) for f in find_files(in_path)]
    if not files:
        print(f"No valid audio files in {in_path}")
        return
    # print("Going to separate the files:")
    # print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='input dir',
        default="./og")
    parser.add_argument('--output_dir', help='output dir',
        default="./output")
    args = parser.parse_args()
    in_path = args.input_dir
    out_path = args.output_dir

    if not (os.path.isdir(out_path)):
        os.makedirs(out_path)


    separate(in_path, out_path)
