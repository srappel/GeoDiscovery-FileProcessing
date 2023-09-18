import updateMetadata

# Take as an argument a directory containing a bunch of datasets (in dirs)

# Loop through each directory in the parent folder 

# Create a updateMetadata.Dataset object by passing each dir Path
# to the Dataset factory Dataset(Path)
# This will create:
#   - Dataset.data (Path to the actual data)
#   - Dataset.datatype (Integer code)
#   - Dataset.metadata (A AGSLMetadata Object)

# Creating the Dataset object will create the AGSLMetadata object:
# This creates:
#   - Dataset.metadata.xml_text
#   - Dataset.metadata.md_object
#   - Dataset.metadata.rootElement
#   - Dataset.metadata.altTitle
#   - Dataset.metadata.rights

### Now we need to run through some functions on the data:

## Create and Write Identifiers:
## Dataset.metadata.create_and_write_identifiers()

# First, this will mint a new Identifier object.
# This creates:
#   -Dataset.metadata.identifier.arkid
#   -Dataset.metadata.identifier.nameAuthorityNumber
#   -Dataset.metadata.identifier.assignedName

# Next, it will write the infomration from the Identifier object
# into the correct places in the xml metadata.

# Finally, it saves the metadata object.

## Update AGSL Hours
## Dataset.metadata.update_agsl_hours() 

# Updates the hours in the metadata and saves the metadata object.

## Dual Metadata Export
## Dataset.metadata.dual_metadata_export

# This exports the metadata to the parent directory for the dataset

## Bind the ArkID using NOID
## Dataset.metadata.bind()

# Creates the bind parameters:
# who, what, when, where, meta-who, meta-when, meta-uri, rights, download
# Sends the bind request using the requests library

### Now we need to "ingest" the dataset, which involves
# Creating a new zip archive containing the data and xml metadata
# The zip file will be named after the alt-title
# Put it in a directory named after the assignedName from the arkid
# Put that directory in the appropriate folder on the webserver (by rights)
# Create a copy of the ISO Xml (assignedName_ISO.xml) in the metadata directory on the webserver

### Testing/Logging

# if it is successful:
# write to log the path on the webserver

# if it fails
# write the failture to the log
# write an error message indicating where/why it failed
# MOVE TO THE NEXT DATASET!