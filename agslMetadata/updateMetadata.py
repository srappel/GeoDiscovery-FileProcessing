"""
Tools for updating AGSL metadata for GeoDiscovery
"""

import arcpy
import requests
import re

import xml.etree.ElementTree as ET

from arcpy import metadata as md
from datetime import datetime
from pathlib import Path

class Dataset:
    """Representation of the directory containing a dataset in any form"""

    name: str
    status: str # Todo: make this an enum
    arkid: str

    def __init__(self, providedPath):
        self.path = Path(providedPath)

    def get_dataset_metadata(self) -> tuple[str,md.Metadata,ET.Element]:
        """Gets a dataset's metadata
        
        Returns a tupale with three objects:
        - XML as a single string
        - arcpy.metadata.Metadata object
        - xml.etree.ElementTree Element Object for the root element (<metadata>)
        
        :param str dataset: The path to the dataset as a string
        :returns: a tuple with three object representations of the dataset's metadata
        :rtype: tuple[str,md.Metadata,ET.Element]
        """
        # get the md.Metadata object.
        dataset_Metadata_object = md.Metadata(self.path)
        # isReadOnly test to make sure we can write to the object else error
        if dataset_Metadata_object.isReadOnly is None: # This means that nothing was passed
            #ERROR
            print("A blank metadata object was created")
            return
        elif dataset_Metadata_object.isReadOnly is True: # This means that a URI was passed, but it isn't a valid XML document
            #ERROR
            print("Not a valid URI")
            return
        else:
            # create an ET for the root
            dataset_root_Element = ET.fromstring(dataset_Metadata_object.xml)
            # Return a tuple with the XML as a string, a Metadata object, and a Element object for the metadata (root) tag
            return dataset_Metadata_object.xml, dataset_Metadata_object, dataset_root_Element

    def dual_metadata_export(self, md_outputdir=None, md_filename=None) -> tuple[Path,Path]:
        """Exports an ISO and FGDC format XML file for the dataset.
        
        :param str dataset: The path to the dataset as a string
        :param str md_outputdir: The directory to store the 2 new files. Default is the parent directory, or grandparent if parent is a FileGeodatabase.
        :param str md_filename: A AGSL format filename (e.g. geography_theme_year) to use as the metadata filename. 
        :returns: a tuple containing the Path to the ISO and FGDC XML Files
        :rtype: tuple[Path,Path]
        """
        # Create the Metadata Object
        dataset_md = md.Metadata(dataset)
        
        # If the md_outputdir optional argument is specified, use it was the output directory
        # Otherwise default to the parent directory of the dataset.
        # If the parent directory is a FileGeodatabase, use the Grandparent (parent dir of the Geodatabase)
        if md_outputdir is None:
            if Path(dataset).parent.suffix == ".gdb":
                parent = Path(dataset).parent.parent
            elif Path(dataset).parent.is_dir() is False:
                print("updateMetadta.py > Dataset > dual_metadta_export() -> Parent is not a dir!")
                return
            else:
                parent = Path(dataset).parent
        else:
            if Path(md_outputdir).is_dir():
                parent = Path(md_outputdir)
            else:
                print("updateMetadta.py > Dataset > dual_metadta_export() -> specified output directory is not a valid directory!")
                return
            
        # If the md_filename optional argument is specified, use it as the filename for the new metadata.
        # Otherwise, use the dataset's filename (the Path.stem) as the filename to prefix the _ISO or _FGDC suffix.
        if md_filename is None: # Default
            output_ISO_Path = parent / f'{Path(dataset).stem}_ISO.xml'
            output_FGDC_Path = parent / f'{Path(dataset).stem}_FGDC.xml'
        else:
            output_ISO_Path = parent / f'{md_filename}_ISO.xml'
            output_FGDC_Path = parent / f'{md_filename}_FGDC.xml'
        
        dataset_md.exportMetadata(output_ISO_Path, 'ISO19139_GML32', metadata_removal_option='REMOVE_ALL_SENSITIVE_INFO')
        dataset_md.exportMetadata(output_FGDC_Path, 'FGDC_CSDGM', metadata_removal_option='REMOVE_ALL_SENSITIVE_INFO')
        return output_ISO_Path, output_FGDC_Path
    
class Metadata:
    """Representation of a metadata record for a dataset in our geospatial data collection"""

    title: str
    rights: str # Todo: make this an enum
    arkid: str
    mdObject: md.Metadata

def main() -> None:
    """Main function."""

    dataset = Dataset(r"c:\Users\srappel\Desktop\Test Fixture Data\DoorCounty_Lighthouses_2010_UW\DoorCounty_Lighthouses_2010.shp")
    dataset_metadata_string = dataset.get_dataset_metadata()[0]
    print(f'The dataset path is: {dataset.path}')
    print(f"The dataset's metadata is:\n{dataset_metadata_string}")

if __name__ == "__main__":
    main()  

    
