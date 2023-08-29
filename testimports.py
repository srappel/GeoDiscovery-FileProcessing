def testimports() -> str:
    try:
        import arcpy
        import requests
        import re

        import xml.etree.ElementTree as ET

        from arcpy import metadata as md
        from datetime import datetime
        from pathlib import Path
        return "pass"
    except:
        return "fail"

if __name__ == "__main__":
    print(testimports())
