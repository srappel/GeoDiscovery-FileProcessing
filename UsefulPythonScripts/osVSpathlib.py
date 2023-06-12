import os
from pathlib import Path

## Two different options to make a directory

# Using os.mkdir requires making a try loop to catch an ex if it exists already

# using pathlib, there is an exist_ok flag that we can use to avoid needing to use
# a try loop

def make_logs_dir():
    try:
        os.mkdir("logs/")
    except FileExistsError as ex:
        print("logs directory already exists")

def make_output_dir():
    dir_path = Path("output/")
    dir_path.mkdir(exist_ok=True)

if __name__ == "__main__":
    make_logs_dir()
    make_output_dir()