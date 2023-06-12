# glob.py
# This script has some basic functionality using the glob module
# It's from the Python: Working with Files 01_04 exercise files

import glob

# Prints any items matching the search string '*.png' (not recursive)
def display_pngs():
    png_files = glob.glob('*.png')
    print(png_files)\
    
# print any files matching search string '*monster01*' not recursive)
def find_monster_one():
    filtered_items = glob.glob('*monster01*')
    print(filtered_items)

# Uses iglob which returns an iterator rather than a list.
# Also uses the recursive flag to look in subdirectories.
# The addition of '**/' to the search string will ensure
# files contained in directories not containing the string
# 'monster01' are still included.
def find_monster_one_in_subdirs():
    for file in glob.iglob('**/*monster01*', recursive=True):
        print(file)

# This loop will return True when run as a script, but not if it's imported
# as a module.
if __name__ == "__main__":
    display_pngs()
    find_monster_one()
    find_monster_one_in_subdirs()