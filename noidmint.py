# noidmint.py
# Stephen Appel 6/12/2023
# Mint's a ark:id using our noid minting service at UWM Libraries

import requests
import re

def searchForID(text) -> str:
    # Will match the whole ID
    # Group 1 will be the *Name Assigning Authority Number*
    # Group 2 will be the *Assigned Name*
    arkregex = re.compile(r"(\d{5})\/(\w{11})")
    arkid = arkregex.search(text)
    return arkid[0]

def mintArk(minter) -> str:
    #Send the request to the minter. Catch connection errors.
    try:
        r = requests.get(minter)
    except:
        print("There was a connection error! Check the URL you used to request the id!")
        return

    # Check the status code the minter returns. It should be 200 if the request was completed.
    if r.status_code != 200:
        print("There was a non-200 status code from the minter: " + r.status_code)
        return
    # If the status code is 200, then grab the text, run it through the searchForID function to get a string with the arkID
    else:
        minter_text = r.text
        arkid = searchForID(minter_text)
        return arkid

# This function will not run if this script is imported as a subscript, it's only for testing.
if __name__ == "__main__":
    print(mintArk('https://digilib-dev.uwm.edu/noidu_gmgs?mint+1'))