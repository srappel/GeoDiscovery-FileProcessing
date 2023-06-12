import os

def display_cwd():
    cwd = os.getcwd()
    print("Current Working Directory: ", cwd)\
    
def up_one_directory_level():
    os.chdir("../")

def display_entries_in_directory(directory):
    with os.scandir(directory) as entries:
        for entry in entries:
            print(entry.name)

if __name__ == "__main__":
    display_cwd()
    up_one_directory_level()
    display_cwd()
    display_entries_in_directory('images/')