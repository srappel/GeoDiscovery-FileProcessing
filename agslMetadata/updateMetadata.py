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

    
    
class Metadata:
    """Representation of a metadata record for a dataset in our geospatial data collection"""

    title: str
    rights: str # Todo: make this an enum
    arkid: str

    
