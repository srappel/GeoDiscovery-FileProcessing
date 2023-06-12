# GeoDiscovery File Processing

A place to store the scripts used to process AGSL Archival GIS data.

## Links and notes:

* [Deep dive into pathlib](https://youtu.be/UcKkmwaRbsQ)

## Example Steps to process \Test Fixture Data\Wisconsin_IceAgeTrail_2019:

1. Mint an ark for the resource using NOID
1. Bind the ark's `where` tag to "https://geodiscovery.uwm.edu/*ark:id*"
1. Add the ark:id and the url generated to the ArcGIS format metadata (Wisconsin_IceAgeTrail_2019.shp.xml)
1. Regenerate ISO and FGDC XML metadata (Wisconsin_IceAgeTrail_2019_ISO.xml and Wisconsin_IceAgeTrail_2019_FGDC.xml)
1. Zip the folder -> Wisconsin_IceAgeTrail_2019.zip
1. Use the metadata to determine which directory the folder will go to (public, UW, UW-System)
1. Create a directory with the ark:id as the directory name
1. Put the zip file in the directory
1. Create copies of ISO and FGDC metadata outside the zip in the directory.
1. Use GeoCombine to generate aardvark JSON metadata - > *ark:id*.json, put it in the directory. (This step should include generating the download link: https://geodata.uwm.edu/*public*/*ark:id*)
