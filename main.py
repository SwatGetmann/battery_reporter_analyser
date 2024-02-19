import pandas as pd

# Hack: https://stackoverflow.com/questions/69515086/error-attributeerror-collections-has-no-attribute-callable-using-beautifu
import collections
collections.Callable = collections.abc.Callable

from bs4 import BeautifulSoup, ResultSet
from typing import Any

def parse_tables(tables: ResultSet[Any]):
    """Parser for Battery Report Tables

    Args:
        tables (ResultSet[Any]): input array of table nodes from the report

    Returns:
        List[Union[None, Dict[AnyStr, AnyStr], List[Dict[AnyStr, AnyStr]]]]:
            List of all the parsed information.
            NOTE: For now it is stored either in List of Dicts, or in a Dict,
            but that's going to change to use a common container class.
    """
    if not tables:
        return []

    tables_parsed = []

    # Table 0: Metadata - System Info
    metadata_str = [el.text.strip() for el in tables[0].find_all('td')]
    headers = metadata_str[0::2]
    metadata = dict(zip(headers, metadata_str[1::2]))
    tables_parsed.append(metadata)

    # Table 1: Metadata - Installed Batteries
    metadata2_str = [el.text.strip() for el in tables[1].find_all('td')]
    # Battery info is given per each vattery attached, but we deal with a single one
    metadata2_str[0], metadata2_str[1] = [x.strip() for x in metadata2_str[1].split("\n") if x]
    headers = metadata2_str[0::2]
    metadata2 = dict(zip(headers, metadata2_str[1::2]))
    tables_parsed.append(metadata2)

    # Table 2: Recent Usage
    metadata3_str = [el.text.strip() for el in tables[2].find_all('td')]
    headers = metadata3_str[0:4] + ["CAPACITY REMAINING (mWh)"]
    data = [metadata3_str[4+i:4+i+5] for i in range(0, len(metadata3_str[4:]), 5)]
    metadata3 = [dict(zip(headers, d)) for d in data]
    tables_parsed.append(metadata3)

    # Table 3: Battery Usage (under the chart)
    metadata4_str = [el.text.strip() for el in tables[3].find_all('td')]
    headers = metadata4_str[0:4] + ["ENERGY DRAINED (mWh)"]
    metadata4_str = [el for el in metadata4_str if el]
    data = [metadata4_str[4+i:4+i+5] for i in range(0, len(metadata4_str[4:]), 5)]
    metadata4 = [dict(zip(headers, d)) for d in data]
    tables_parsed.append(metadata4)

    # Table 4: Usage History
    metadata5_str = [el.text.strip() for el in tables[4].find_all('td')]
    # Fixes for merged table cells
    headers_l1 = metadata5_str[0:4]
    headers_l2 = metadata5_str[4:10]
    headers_l1.insert(2, headers_l1[1])
    headers_l1.append(headers_l1[-1])
    headers = [f"{headers_l1[i]} - {headers_l2[i]}" for i in range(len(headers_l1))]
    data = [metadata5_str[10+i:10+i+6] for i in range(0, len(metadata5_str[10:]), 6)]
    metadata5 = [dict(zip(headers, d)) for d in data]
    tables_parsed.append(metadata5)

    # Table 5: Battery Capacity History
    metadata6_str = [el.text.strip() for el in tables[5].find_all('td')]
    headers = metadata6_str[0:3]
    data = [metadata6_str[3+i:3+i+3] for i in range(0, len(metadata6_str[3:]), 3)]
    metadata6 = [dict(zip(headers, d)) for d in data]
    tables_parsed.append(metadata6)

    # Table 6: Battery Life Estimates
    metadata7_str = [el.text.strip() for el in tables[6].find_all('td')]
    headers_l1 = metadata7_str[0:4]
    headers_l2 = metadata7_str[4:10]
    headers_l1.insert(2, headers_l1[1])
    headers_l1.append(headers_l1[-1])
    headers = [f"{headers_l1[i]} - {headers_l2[i]}" for i in range(len(headers_l1))]
    data = [metadata7_str[10+i:10+i+6] for i in range(0, len(metadata7_str[10:]), 6)]
    metadata7 = [dict(zip(headers, d)) for d in data]
    tables_parsed.append(metadata7)

    # Table 7: Current estimate of battery life based on all observed drains since OS install
    # NOTE: Table has no headers! So they are taken from the previous step.
    metadata8_str = [el.text.strip() for el in tables[7].find_all('td')]
    metadata8 = dict(zip(headers, metadata8_str))
    tables_parsed.append(metadata8)

    return tables_parsed


if __name__ == '__main__':
    with open("./test/battery-report-240217-j.html", 'r') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    tables = soup.find_all('table')
    parsed_tables = parse_tables(tables)
    for pt in parsed_tables:
        print(10*'-')
        print(pt)
