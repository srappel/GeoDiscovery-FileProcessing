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

    path: Path
    name: str
    status: str # Todo: make this an enum
    arkid: str
    metadata: tuple[str,md.Metadata,ET.Element]

    def __init__(self):
        try:
            metadata = get_dataset_metadata(self)
        except:
            #error
            print("There was an error setting the metadata attribute while constructing the Document class")

    def get_dataset_metadata(self) -> tuple[str,md.Metadata,ET.Element]:
        """Gets a dataset's metadata
        
        Returns a tuple with three objects:
        - XML as a single string
        - arcpy.metadata.Metadata object
        - xml.etree.ElementTree Element Object for the root element (<metadata>)
        
        :param str dataset: The path to the dataset as a string
        :returns: a tuple with three object representations of the dataset's metadata
        :rtype: tuple[str,md.Metadata,ET.Element]
        """
        # get the md.Metadata object.
        dataset_Metadata_object = md.Metadata(dataset)
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
    
class Metadata:
    """Representation of a metadata record for a dataset in our geospatial data collection"""

    title: str
    rights: str # Todo: make this an enum
    arkid: str

    
