import pandas as pd

# Hack: https://stackoverflow.com/questions/69515086/error-attributeerror-collections-has-no-attribute-callable-using-beautifu
import collections
collections.Callable = collections.abc.Callable

import argparse

from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List, Dict, AnyStr, Union
from pathlib import Path

# == LEGEND
# th = table header
# td = table data (may include all, including th)
# p_td = parsed table data

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
    print(td_2)
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
    
TOTAL_TABLES = 8

def parse_table_by_id(table: Tag, idx: int):
    # Table 0: Metadata - System Info
    if idx == 0:
        return parse_table_1(table)

    # Table 1: Metadata - Installed Batteries
    if idx == 1:
        return parse_table_2(table)

    # Table 2: Recent Usage
    if idx == 2:
        return parse_table_3(table)

    # Table 3: Battery Usage (under the chart)
    if idx == 3:
        return parse_table_4(table)

    # Table 4: Usage History
    if idx == 4:
        return parse_table_5(table)

    # Table 5: Battery Capacity History
    if idx == 5:
        return parse_table_6(table)

def parse_tables(tables: ResultSet[Tag], table_flags: List[bool]) -> List[Union[None, List[Dict[AnyStr, AnyStr]]]]:
    """Parser for Battery Report Tables

    Args:
        tables (ResultSet[Tag]):
            input array of table nodes from the report
        table_flags: (List[bool]):
            list of bools whether to add or skip parsing for specific tables

    Returns:
        List[Union[None, List[Dict[AnyStr, AnyStr]]]]:
            List of all the parsed information.
            NOTE: For now it is stored either in List of Dicts, or in a Dict,
            but that's going to change to use a common container class.
    """
    tables_container = []
    for i in range(0, TOTAL_TABLES):
        tables_container.append([])
    
    if not tables:
        return tables_container

    for ti, tf in enumerate(table_flags[:6]):
        if tf:
            print("Ti: %s" % ti)
            tables_container[ti] = parse_table_by_id(tables[ti], ti)
    
    # Table 6: Battery Life Estimates &
    # Table 7: Current estimate of battery life based on all observed drains since OS install
    if table_flags[6] or table_flags[7]:
        p_td_7, p_td_8 = parse_table_7_8(tables[6], tables[7])
        if table_flags[6]:
            tables_container[6] = p_td_7
        if table_flags[7] and p_td_8:
            tables_container[7] = p_td_8

    return tables_container

arg_parser = argparse.ArgumentParser(description="Windows Battery Report Parser & Analyser.")
group = arg_parser.add_mutually_exclusive_group(required=True)
group.add_argument('--input_dir', type=Path, help='Directory with reports to parse')
group.add_argument('--input_file', type=Path, help='Report File to parse')
arg_parser.add_argument('--tables', nargs="+", default='all', help='Tables to parse (default: %(default)s)')
arg_parser.add_argument('--output_dir', type=Path, help='Directory to save parsed reports to')

def parse_file(input_path, table_flags):
    with input_path as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    tables = soup.find_all('table')
    return parse_tables(tables, table_flags)

def handle_parsed_tables(parsed_tables: List[Union[None, List[Dict[AnyStr, AnyStr]]]], output_dir_path: Path, output_path_pattern: str):
    print(parsed_tables)

    for pt in parsed_tables:
        print(10*'-')
        print(pt)

    for idx, pt in enumerate(parsed_tables): # TODO: use indexes not of output array, but of global table presence
        print(10*'=')
        print(idx)
        pt_df = pd.DataFrame(data=pt)
        print(pt_df.head())
        output_path_df = output_dir_path / (output_path_pattern % idx)
        print(output_path_df)
        pt_df.to_parquet(path=output_path_df)

if __name__ == '__main__':
    args = arg_parser.parse_args()
    print(args)

    if not args.input_dir and not args.input_file:
        print("There's nothing to process. Exiting...")
        exit(0)
    
    if args.input_dir:
        input_paths = list(args.input_dir.glob('*.html'))
    else:
        input_paths = [args.input_file]
    print(input_paths)
    
    input_paths_non_presence_check = any([not p.exists() for p in input_paths])
    if input_paths_non_presence_check:
        print("Input does not exist. Exiting...")
        exit(0)

    if not args.output_dir:
        print("There's nowhere to save. Exiting...")
        exit(0)
    
    output_dir_path = args.output_dir
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)

    table_process_ids = range(0, TOTAL_TABLES)
    table_process_flags = [True] * TOTAL_TABLES
    if args.tables != 'all':
        def table_param_check(t):
            return t < 1 or t > TOTAL_TABLES
        
        table_checks = [table_param_check(int(t)) for t in args.tables]
        print(table_checks)
        if any(table_checks):
            print("Invalid tables identificators were given. Exiting...")
            exit(0)
        
        table_process_ids = [int(ti)-1 for ti in args.tables]
        table_process_flags = [False] * TOTAL_TABLES
        for ti in table_process_ids:
            table_process_flags[ti] = True
    
    print("Table Process Flags: %s" % table_process_flags)
    
    # TODO: add merging
    for i, fp in enumerate(input_paths):
        print("I: %s / FP: %s " % (i, fp))
        output_path_pattern = f"test_{i}_%s.parquet"
        parsed_tables = parse_file(open(fp), table_process_flags)
        handle_parsed_tables(parsed_tables, output_dir_path, output_path_pattern)