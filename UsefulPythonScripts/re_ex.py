import re

phoneRegex = re.compile(r'''(
(\d\d\d-)? #Test
(\d{3}-) # first 3
(\d\d\d\d) # last 4
)''', re.VERBOSE)

phoneRegex.findall("I would like to call you from either 414-865-1475 or 628-1877")

