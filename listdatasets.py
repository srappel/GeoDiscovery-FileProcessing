# listdatasets.py
# this script will use pathlib to list all the ISO datasets in the UWM_Geometadata_ISO directory

from pathlib import Path

def list_directory_contents(path) -> list:
    dirs = []
    entries = Path(path)
    for entry in entries.iterdir():
        clean = entry.stem.rstrip("_ISO")
        dirs.append(clean)
    return dirs

if __name__ == "__main__":
    # Prints first 5 results
    print(list_directory_contents(r'S:\_H_GML\Departments\AGSL\GIS\Projects\METADATA\Complete_ISO\UWM_Geometadata_ISO\Open')[0:5])
