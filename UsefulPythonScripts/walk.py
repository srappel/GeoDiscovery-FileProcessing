# walk.py
# I'm already pretty familiar with walks, but I didn't know about the bottom_up
# method used. 
# Important note: walk only returns relative path information, not absolute paths.
# If we need to know more about a file, we need to use other operations from os

import os

def top_down_walk():
    for dirpath, dirnames, files in os.walk('artwork/'):
        print("Directory: ", dirpath)
        print("Includes these directories:")
        for dirname in dirnames:
            print(dirname)
        print("Includes these files:")
        for filename in files:
            print(filename)
        print()

def bottom_up_walk():
    for dirpath, dirnames, files in os.walk('artwork/', topdown=False):
        print("Directory: ", dirpath)
        print("Includes these directories:")
        for dirname in dirnames:
            print(dirname)
        print("Includes these files:")
        for filename in files:
            print(filename)
        print()

if __name__ == "__main__":
    #top_down_walk()
    bottom_up_walk()