# pathlib.py
# pathlib is like os on steroids and is new ao 3.4
# treates filepaths and dirpaths as objects rather than as strings

from pathlib import Path

def print_directory_contents():
    # Uses the current working dir:
    entries = Path.cwd()

    # Can also hard code a path:
    # entries = Path('images/')

    # Can also use the home dir (C:\users\username on Win):
    # entries = Path.home()

    # Creates an iterator of all files and folders in pwd
    for entry in entries.iterdir():
        # each entry contains an object for the file or subdir
        print(entry.name) # The name of the file
        print(entry.parent) # The parent directory
        print(entry.parent.parent) # The grandparent directory
        print(entry.stem) # the name of the file without the extension
        print(entry.suffix) # only the file extension
        print(entry.stat()) # returns the os stat object (size, last mod, etc)
        print()

if __name__ == "__main__":
    print_directory_contents()