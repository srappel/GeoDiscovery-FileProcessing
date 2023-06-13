# noidbind.py
# this script, when passed a arkid, will bind the where field to a URL, in this case, the
# appropriate show page on GeoDiscovery

# Example bind URL: "https://digilib-dev.uwm.edu/noidu_gmgs?bind+set+77981/gmgs4x54g16+where+https://uwm.edu/libraries/"

import requests
import re

def generate_bind_url(arkid, field, baseURL) -> str:
    # Check to see if it is a valid arkid using regex
    try:
        arkregex = re.compile(r"(\d{5})\/(\w{11})")
    except re.error as ex:
        print(ex)
        return

    check_arkid = arkregex.match(arkid)

    if not check_arkid is None:
        # Construct the URL:
        bind_URL = ("https://digilib-dev.uwm.edu/noidu_gmgs?bind+set+"
        + arkid 
        + "+" 
        + field
        + "+" 
        + baseURL
        + arkid) 
        return bind_URL
    else:
        return

def bindArk(bind_URL):
    r = requests.get(bind_URL)
    return r.status_code
        
if __name__ == "__main__":
    print(bindArk(generate_bind_url("77981/gmgssf2mb2h", "where", "https://geodiscovery.uwm.edu/")))