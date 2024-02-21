import pandas as pd

# Hack: https://stackoverflow.com/questions/69515086/error-attributeerror-collections-has-no-attribute-callable-using-beautifu
import collections
collections.Callable = collections.abc.Callable

from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List

def parse_table_1(table: Tag):
    # Table 0: Metadata - System Info
    td_1 = [el.text.strip() for el in table.find_all('td')]
    th_1 = td_1[0::2]
    p_td_1 = [dict(zip(th_1, td_1[1::2]))]
    return p_td_1

def parse_table_2(table: Tag):
    # Table 1: Metadata - Installed Batteries
    td_2 = [el.text.strip() for el in table.find_all('td')]
    # Battery info is given per each battery attached, but we deal with a single one
    td_2[0], td_2[1] = [x.strip() for x in td_2[1].split("\n") if x]
    th_2 = td_2[0::2]
    p_td_2 = [dict(zip(th_2, td_2[1::2]))]
    return p_td_2

def parse_table_3(table: Tag):
    # Table 2: Recent Usage
    td_3 = [el.text.strip() for el in table.find_all('td')]
    th_3 = td_3[0:4] + ["CAPACITY REMAINING (mWh)"]
    td_3 = [td_3[4+i:4+i+5] for i in range(0, len(td_3[4:]), 5)]
    p_td_3 = [dict(zip(th_3, d)) for d in td_3]
    return p_td_3

def parse_table_4(table: Tag):
    # Table 3: Battery Usage (under the chart)
    td_4 = [el.text.strip() for el in table.find_all('td')]
    th_4 = td_4[0:4] + ["ENERGY DRAINED (mWh)"]
    td_4 = [el for el in td_4 if el]
    td_4 = [td_4[4+i:4+i+5] for i in range(0, len(td_4[4:]), 5)]
    p_td_4 = [dict(zip(th_4, d)) for d in td_4]
    return p_td_4

def parse_table_5(table: Tag):
    # Table 4: Usage History
    td_5 = [el.text.strip() for el in table.find_all('td')]
    # Fixes for merged table cells
    th_5_l1 = td_5[0:4]
    th_5_l2 = td_5[4:10]
    th_5_l1.insert(2, th_5_l1[1])
    th_5_l1.append(th_5_l1[-1])
    th_5 = [f"{th_5_l1[i]} - {th_5_l2[i]}" for i in range(len(th_5_l1))]
    td_5 = [td_5[10+i:10+i+6] for i in range(0, len(td_5[10:]), 6)]
    p_td_5 = [dict(zip(th_5, d)) for d in td_5]
    return p_td_5

def parse_table_6(table: Tag):
    # Table 5: Battery Capacity History
    td_6 = [el.text.strip() for el in table.find_all('td')]
    th_6 = td_6[0:3]
    td_6 = [td_6[3+i:3+i+3] for i in range(0, len(td_6[3:]), 3)]
    p_td_6 = [dict(zip(th_6, d)) for d in td_6]
    return p_td_6

def parse_table_7_8(table1: Tag, table2: Tag):
    # Table 6: Battery Life Estimates
    td_7 = [el.text.strip() for el in table1.find_all('td')]
    th_7_l1 = td_7[0:4]
    th_7_l2 = td_7[4:10]
    th_7_l1.insert(2, th_7_l1[1])
    th_7_l1.append(th_7_l1[-1])
    th_7 = [f"{th_7_l1[i]} - {th_7_l2[i]}" for i in range(len(th_7_l1))]
    td_7 = [td_7[10+i:10+i+6] for i in range(0, len(td_7[10:]), 6)]
    p_td_7 = [dict(zip(th_7, d)) for d in td_7]
    
    if not table2:
        return (p_td_7, None)

    # Table 7: Current estimate of battery life based on all observed drains since OS install
    # NOTE: Table has no th! So they are taken from the previous step.
    td_8 = [el.text.strip() for el in table2.find_all('td')]
    p_td_8 = [dict(zip(th_7, td_8))]

    return (p_td_7, p_td_8)
    

def parse_tables(tables: ResultSet[Tag]):
    """Parser for Battery Report Tables

    Args:
        tables (ResultSet[Any]): input array of table nodes from the report

    Returns:
        List[Union[None, List[Dict[AnyStr, AnyStr]]]]:
            List of all the parsed information.
            NOTE: For now it is stored either in List of Dicts, or in a Dict,
            but that's going to change to use a common container class.
    """
    if not tables:
        return []

    tables_parsed = []

    # th = table header
    # td = table data (may include all, including th)
    # p_td = parsed table data

    # Table 0: Metadata - System Info
    tables_parsed.append(parse_table_1(tables[0]))

    # Table 1: Metadata - Installed Batteries
    tables_parsed.append(parse_table_2(tables[1]))

    # Table 2: Recent Usage
    tables_parsed.append(parse_table_3(tables[2]))

    # Table 3: Battery Usage (under the chart)
    tables_parsed.append(parse_table_4(tables[3]))

    # Table 4: Usage History
    tables_parsed.append(parse_table_5(tables[4]))

    # Table 5: Battery Capacity History
    tables_parsed.append(parse_table_6(tables[5]))

    # Table 6: Battery Life Estimates &
    # Table 7: Current estimate of battery life based on all observed drains since OS install
    p_td_7, p_td_8 = parse_table_7_8(tables[6], tables[7])
    tables_parsed.append(p_td_7)
    if p_td_8:
        tables_parsed.append(p_td_8)

    return tables_parsed


if __name__ == '__main__':
    input_path = "./test/battery-report-240217-j.html"
    output_path_pattern = "./parquets/test_%s.parquet"

    with open(input_path, 'r') as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    tables = soup.find_all('table')
    parsed_tables = parse_tables(tables)
    for pt in parsed_tables:
        print(10*'-')
        print(pt)

    for idx, pt in enumerate(parsed_tables):
        print(10*'=')
        print(idx)
        pt_df = pd.DataFrame(data=pt)
        print(pt_df.head())