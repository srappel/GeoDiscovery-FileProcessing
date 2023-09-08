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
from enum import Enum

DEV = True

IDENTIFIER_LIST = ["mdFileID","dataSetURI","identCode"] # code smell. DRY: These are already in SEARCH_STRING_DICT
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
        # self.metadata: tuple[str,md.Metadata,ET.Element] = self.get_dataset_metadata(self.path)
        self.metadata = Metadata(self.get_dataset_metadata(self.path))

    def get_dataset_metadata(self, path) -> tuple[str,md.Metadata,ET.Element]:
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
        dataset_Metadata_object = md.Metadata(path)
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

    def __init__(self, dataset_metadata_tuple):
        self.xml_text: str = dataset_metadata_tuple[0]
        self.md_object: md.Metadata = dataset_metadata_tuple[1]
        self.rootElement: ET.Element = dataset_metadata_tuple[2]
        self.altTitle: str = self.get_alt_title()

    def check_if_existing_identifier(self, find_string) -> bool:
        """ Check if the specified identifier exists in the metadata record
        
        Used in write_identifiers()
        
        returns a boolean (True or False) indicating if the string passed exists.
        Uses the ET.findall() syntax to create a list of matches.
        If there is 1 or more matches, returns true. Else returns false.
        
        :param xml.etree.ElementTree.Element rootElement: The root Element of the metadata
        :param str find_string: a string using xml.etree.ElementTree.findall syntax
        :returns: True if one or more of the element is found, False if none found.
        :rtype: bool    
        """
        if len(self.rootElement.findall(find_string)) > 0:
            return True
        else:
            return False

    def get_alt_title(self) -> str:
        rootElement = self.rootElement
        altTitle_Element = rootElement.find(SEARCH_STRING_DICT["altTitle"])
        if not altTitle_Element is None:
            return altTitle_Element.text

    def write_identifiers(self, arkid, right_string, IDENTIFIER_LIST) -> ET.Element:
        """ Inserts the arkid as text property of specified identifiers in the metadata Element    
        TODO: Test to ensure the ark that is passed is valid? With a REGEX or maybe even a request?
        TODO: Access constraints
            dct_accessrights_s - XSLT looks at legalconstraints/other constraints
            /MD_Metadata/identificationInfo/MD_DataIdentification/resourceConstraints[13]/MD_LegalConstraints/otherConstraints/gco:CharacterString
        TODO: Update the dataSetURI to use the download URL rather than the application URL
        """   
        rootElement = self.rootElement
        ark_URI = APPLICATION_URL + 'ark:-' + arkid.replace('/','-')
        alt_title = self.get_alt_title(self.rootElement) 
        download_URI = f'{FILE_SERVER_URL}{right_string}/{arkid[-11:]}/{alt_title}.zip'
        
        # IDENTIFIER_LIST = ["mdFileID","dataSetURI","identCode"]
        # Write the Citation Identifier Code:
        if check_if_existing_identifier(rootElement, SEARCH_STRING_DICT["citationIdentifier"]) is True:
            dataset_identCode = rootElement.find(SEARCH_STRING_DICT["citationIdentifier"])
            dataset_identCode.text = ark_URI
        else:
            dataset_idCitation_Element = rootElement.find(SEARCH_STRING_DICT["citationIdentifier"])
            citId_Element = ET.SubElement(dataset_idCitation_Element, 'citId', xmls="")
            identCode_Element = ET.SubElement(citId_Element, 'identCode')
            identCode_Element.text = ark_URI

        # Write the Metadata File ID Code:
        if check_if_existing_identifier(rootElement, SEARCH_STRING_DICT["metadataFileID"]) is True:
            dataset_mdFileID_Element = rootElement.find(SEARCH_STRING_DICT["metadataFileID"])
        else:
            dataset_mdFileID_Element = ET.SubElement(rootElement, 'mdFileID')
        
        dataset_mdFileID_Element.text = f'ark:/77981/{arkid.split("/")[1]}'

        # Write the Dataset URI:
        if check_if_existing_identifier(rootElement, SEARCH_STRING_DICT["datasetURI"]) is True:
            dataset_dataSetURI_Element = rootElement.find(SEARCH_STRING_DICT["datasetURI"])
        else:
            dataset_dataSetURI_Element = ET.SubElement(rootElement, 'dataSetURI')
        
        dataset_dataSetURI_Element.text = download_URI

        print(f'The URI for the dataset is {ark_URI}')
        print(f'The Download URL for the dataset is {download_URI}')
        return rootElement
  
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

    dataset = Dataset(r"c:\Users\srappel\Desktop\Test Fixture Data\DoorCounty_Lighthouses_2010_UW\DoorCounty_Lighthouses_2010.shp")
    print(f'\nThe dataset path is: {dataset.path}\n')

    dataset_Metadata = dataset.metadata
    print(f"The class of dataset_Metadata is {dataset_Metadata.__class__}")
    print(f"The dataset's alt title is {dataset_Metadata.altTitle}\n")
    
    new_arkid_a = Identifier()
    new_arkid_b = Identifier()

    new_arkid_a.mint()
    new_arkid_b.mint()

    print(f"The a dataset's full ARKID is ark:/{new_arkid_a.arkid}")
    print(f"The a dataset's NAN is {new_arkid_a.nameAuthorityNumber}")
    print(f"The a dataset's Name is {new_arkid_a.assignedName}")

    print(f"The b dataset's full ARKID is ark:/{new_arkid_b.arkid}")
    print(f"The b dataset's NAN is {new_arkid_b.nameAuthorityNumber}")
    print(f"The b dataset's Name is {new_arkid_b.assignedName}")

    print("Success!")

if __name__ == "__main__":
    main()  

    
