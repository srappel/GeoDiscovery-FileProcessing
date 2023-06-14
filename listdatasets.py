# listdatasets.py
# this script will use pathlib to list all the ISO datasets in the given directory

from pathlib import Path
import glob

def list_directory_contents(path) -> list:
    dirs = []
    entries = Path(path)
    for entry in entries.iterdir():
        clean = entry.stem.rstrip("_ISO")
        dirs.append(clean)
    return dirs

def find_absolute_path(root_path, dataset) -> str:
    entries = Path(root_path).glob(f'**/{dataset}/')
    for entry in entries:
        return str(entry.absolute())
    return "Undefined"

def write_to_csv(file, text):
    with file.open("a") as f:
        f.write(text + "\n")
    f.close()

if __name__ == "__main__":
    p = Path.home() / 'Desktop' / 'datalist.csv'
    p.touch(exist_ok=True)
    for dir in list_directory_contents(r'S:\_H_GML\Departments\AGSL\GIS\Projects\METADATA\Complete_ISO\UWM_Geometadata_ISO\Open'):
        abs_path = find_absolute_path(r'S:\_R_GML_Archival_AGSL\GIS_Data', dir)
        line = dir + ", " + abs_path
        print(line)
        write_to_csv(p, line)
