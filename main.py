import pandas as pd

# Hack: https://stackoverflow.com/questions/69515086/error-attributeerror-collections-has-no-attribute-callable-using-beautifu
import collections
collections.Callable = collections.abc.Callable

from bs4 import BeautifulSoup

with open("./test/battery-report-240217-j.html", 'r') as fp:
    soup = BeautifulSoup(fp, 'html.parser')

tables = soup.find_all('table')

# Table 0: Metadata - System Info
metadata_str = [el.text.strip() for el in tables[0].find_all('td')]
metadata = dict(zip(metadata_str[0::2], metadata_str[1::2]))

# Table 1: Metadata - Installed Batteries
metadata2_str = [el.text.strip() for el in tables[1].find_all('td')]
# Battery info is broken - fix
metadata2_str[0], metadata2_str[1] = [x.strip() for x in metadata2_str[1].split("\n") if x]
metadata2 = dict(zip(metadata2_str[0::2], metadata2_str[1::2]))

# Table 2: Recent Usage
metadata3_str = [el.text.strip() for el in tables[2].find_all('td')]
headers = metadata3_str[0:4] + ["CAPACITY REMAINING (mWh)"]
data = [metadata3_str[4+i:4+i+5] for i in range(0, len(metadata3_str[4:]), 5)]
[dict(zip(headers, d)) for d in data]