"""
Tools for updating AGSL metadata for GeoDiscovery

TODO: Include rights test in the construction of the download URI
TODO: bind method for the Identifier class
TODO: method to Update the AGSL hours

"""

import arcpy
import requests
import re

import xml.etree.ElementTree as ET

from arcpy import metadata as md
from datetime import datetime
from pathlib import Path
from enum import Enum

DEV = True

RIGHTS = ['public', 'restricted-uw-system', 'restricted-uwm']

APPLICATION_URL = 'https://geodiscovery.uwm.edu/'
APPLICATION_URL_DEV = 'https://geodiscovery-dev.uwm.edu/'
FILE_SERVER_URL = 'https://geodata.uwm.edu/'
NOID_URL_DEV = 'https://digilib-dev.uwm.edu/noidu_gmgs?'
NOID_URL = 'https://.uwm.edu/noidu_gmgs?'

ARK_REGEX = r"(\d{5})\/(\w{11})"

SEARCH_STRING_DICT = {
    "altTitle": ".//idCitation/resAltTitle",
    "rights": ".//othConsts",
    "identCode": ".//citId/identCode",
    "citationIdentifier": ".dataIdInfo/idCitation",
    "metadataFileID": ".//mdFileID",
    "datasetURI": ".//dataSetURI",
    "contact": ".//rpCntInfo/cntHours/../..", # code smell. This is only finding contacts that have hours listed.
    "contactDisplayName": "./displayName",
    "contactHours": ".//cntHours",
    "timeRangeBegin": ".//tmBegin",
    "timeRangeEnd": ".//tmEnd",
    "timeInstantExtent": ".//tmPosition"
}

class Dataset:

    def __init__(self, providedPath):
        self.path = Path(providedPath)
        self.metadata: AGSLMetadata = AGSLMetadata(self.get_dataset_metadata(self.path))

    def get_dataset_metadata(self, path) -> tuple[str,md.Metadata,ET.Element]:
        dataset_Metadata_object = md.Metadata(path)

        if dataset_Metadata_object.isReadOnly is None: # This means that nothing was passed
            print("A blank metadata object was created")
            return
        elif dataset_Metadata_object.isReadOnly is True: # This means that a URI was passed, but it isn't a valid XML document
            print("Not a valid URI")
            return
        else:
            dataset_root_Element = ET.fromstring(dataset_Metadata_object.xml)
            return dataset_Metadata_object.xml, dataset_Metadata_object, dataset_root_Element

class AGSLMetadata:

    def __init__(self, dataset_metadata_tuple):
        self.xml_text: str = dataset_metadata_tuple[0]
        self.md_object: md.Metadata = dataset_metadata_tuple[1]
        self.rootElement: ET.Element = dataset_metadata_tuple[2]
        self.altTitle: str = self.get_alt_title()

    def get_alt_title(self) -> str:
        rootElement = self.rootElement
        altTitle_Element = rootElement.find(SEARCH_STRING_DICT["altTitle"])
        if not altTitle_Element is None:
            return altTitle_Element.text

    def create_and_write_identifiers(self, right_string) -> None:
        
        # mint a new arkid:
        new_identifier = Identifier()
        new_identifier.mint()
        self.arkid: Identifier = new_identifier

        # Generate the text strings
        ark_URI: str = APPLICATION_URL + 'ark:-' + self.arkid.arkid.replace('/','-')
        download_URI: str = f'{FILE_SERVER_URL}{right_string}/{self.arkid.assignedName}/{self.altTitle}.zip'
        
        def check_if_existing_identifier(root, find_string) -> bool:
            if len(root.findall(find_string)) > 0:
                return True
            else:
                return False

        if check_if_existing_identifier(self.rootElement, SEARCH_STRING_DICT["identCode"]):
            identCode_Element = self.rootElement.find(SEARCH_STRING_DICT["identCode"])
        else:
            dataset_idCitation_Element = self.rootElement.find(SEARCH_STRING_DICT["citationIdentifier"])
            citId_Element = ET.SubElement(dataset_idCitation_Element, 'citId', xmls="")
            identCode_Element = ET.SubElement(citId_Element, 'identCode')
            
        identCode_Element.text = ark_URI

        # Write the Metadata File ID Code:
        if check_if_existing_identifier(self.rootElement, SEARCH_STRING_DICT["metadataFileID"]):
            dataset_mdFileID_Element = self.rootElement.find(SEARCH_STRING_DICT["metadataFileID"])
        else:
            dataset_mdFileID_Element = ET.SubElement(self.rootElement, 'mdFileID')
        
        dataset_mdFileID_Element.text = f'ark:/{self.arkid.arkid}'

        # Write the Dataset URI:
        if check_if_existing_identifier(self.rootElement, SEARCH_STRING_DICT["datasetURI"]):
            dataset_dataSetURI_Element = self.rootElement.find(SEARCH_STRING_DICT["datasetURI"])
        else:
            dataset_dataSetURI_Element = ET.SubElement(self.rootElement, 'dataSetURI')
        
        dataset_dataSetURI_Element.text = download_URI

        # Write the new ET to the Metdata object and save:
        self.md_object.xml = ET.tostring(self.rootElement)
        self.md_object.save()
        
        # Reassign some attributes:
        self.xml_text = self.md_object.xml

        return

    def dual_metadata_export(self, md_outputdir=None, md_filename=None) -> tuple[Path,Path]:
        dataset_path = Path(self.md_object.uri)

        if md_outputdir is None:
            if dataset_path.parent.suffix == ".gdb":
                parent = dataset_path.parent.parent
            elif dataset_path.parent.is_dir() is False:
                print("updateMetadta.py > Dataset > dual_metadta_export() -> Parent is not a dir!")
                return
            else:
                parent = dataset_path.parent
        else:
            if Path(md_outputdir).is_dir():
                parent = Path(md_outputdir)
            else:
                print("updateMetadta.py > Dataset > dual_metadta_export() -> specified output directory is not a valid directory!")
                return

        if md_filename is None: # Default
            output_ISO_Path = parent / f'{dataset_path.stem}_ISO.xml'
            output_FGDC_Path = parent / f'{dataset_path.stem}_FGDC.xml'
        else:
            output_ISO_Path = parent / f'{md_filename}_ISO.xml'
            output_FGDC_Path = parent / f'{md_filename}_FGDC.xml'
        
        self.md_object.exportMetadata(output_ISO_Path, 'ISO19139_GML32', metadata_removal_option='REMOVE_ALL_SENSITIVE_INFO')
        self.md_object.exportMetadata(output_FGDC_Path, 'FGDC_CSDGM', metadata_removal_option='REMOVE_ALL_SENSITIVE_INFO')
        
        return output_ISO_Path, output_FGDC_Path
  
class Identifier:

    def mint(self, dev=DEV) -> None:
        if dev == False:
            minter = NOID_URL + 'mint+1'
        else:
            minter = NOID_URL_DEV + 'mint+1'

        try:
            mint_request = requests.get(minter)
        except Exception as ex:
            print(ex)
            return

        if mint_request.status_code != 200:
            print(f"mint request status code = {mint_request.status_code}")
            return
        else:
            regex = re.compile(ARK_REGEX)
            regex_result = regex.search(mint_request.text)
            if not regex_result is None:
                self.arkid = regex_result[0]
                self.nameAuthorityNumber = regex_result[1]
                self.assignedName = regex_result[2]
                return
            else:
                raise Exception("Failed to mint an arkid!")
                return
        
def main() -> None:
    """Main function."""

    # Test creating the Dataset and AGSL Metadata objects:
    dataset = Dataset(r"c:\Users\srappel\Desktop\Test Fixture Data\DoorCounty_Lighthouses_2010_UW\DoorCounty_Lighthouses_2010.shp")
    print(f'\nThe dataset path is: {dataset.path}\n')

    dataset_metadata = dataset.metadata
    print(f"The class of dataset_metadata is {dataset_metadata.__class__}")
    print(f"The dataset's alt title is {dataset_metadata.altTitle}\n")
    
    # Test creating identifiers:
    new_arkid = Identifier()
    new_arkid.mint()

    print(f"The full test ARKID is ark:/{new_arkid.arkid}")
    print(f"The NAN is {new_arkid.nameAuthorityNumber}")
    print(f"The assigned name is {new_arkid.assignedName}")

    # Test writing the identifiers:
    dataset_metadata.create_and_write_identifiers("public")

    print(f"The Metadata File ID is: {ET.fromstring(dataset_metadata.xml_text).find(SEARCH_STRING_DICT['metadataFileID']).text}")
    print(f"The Citation ID is: {ET.fromstring(dataset_metadata.xml_text).find(SEARCH_STRING_DICT['identCode']).text}")
    print(f"The Dataset URI is: {ET.fromstring(dataset_metadata.xml_text).find(SEARCH_STRING_DICT['datasetURI']).text}")

    # Test Dual Metadata Export:
    print(f"The dataset's path is: {dataset_metadata.md_object.uri}")

    ISO_dir, FGDC_dir = dataset_metadata.dual_metadata_export() # returns the 2 paths of the exported md
    print("Result of Dual Metadata Export:")
    print(ISO_dir)
    print(FGDC_dir)

    print("Success!")

if __name__ == "__main__":
    main()  

    
