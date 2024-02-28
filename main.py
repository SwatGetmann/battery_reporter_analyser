import pandas as pd

# Hack: https://stackoverflow.com/questions/69515086/error-attributeerror-collections-has-no-attribute-callable-using-beautifu
import collections
collections.Callable = collections.abc.Callable

import argparse

from bs4 import BeautifulSoup, ResultSet, Tag
from typing import List, Union
from pathlib import Path


# == LEGEND
# th = table header
# td = table data (may include all, including th)
# p_td = parsed table data

def parse_table_1(table: Tag):
    # Table 0: Metadata - System Info
    td_1 = [el.text.strip() for el in table.find_all('td')]
    th_1 = td_1[0::2]
    df = pd.DataFrame(data=[td_1[1::2]], columns=th_1)
    return df

def parse_table_2(table: Tag):
    # Table 1: Metadata - Installed Batteries
    td_2 = [el.text.strip() for el in table.find_all('td')]
    # Battery info is given per each battery attached, but we deal with a single one
    td_2[0], td_2[1] = [x.strip() for x in td_2[1].split("\n") if x]
    th_2 = td_2[0::2]
    df = pd.DataFrame(data=[td_2[1::2]], columns=th_2)
    return df

def parse_table_3(table: Tag):
    # Table 2: Recent Usage
    td_3 = [el.text.strip() for el in table.find_all('td')]
    th_3 = td_3[0:4] + ["CAPACITY REMAINING (mWh)"]
    td_3 = [td_3[4+i:4+i+5] for i in range(0, len(td_3[4:]), 5)]
    df = pd.DataFrame(data=td_3, columns=th_3)
    return df

def parse_table_4(table: Tag):
    # Table 3: Battery Usage (under the chart)
    td_4 = [el.text.strip() for el in table.find_all('td')]
    th_4 = td_4[0:4] + ["ENERGY DRAINED (mWh)"]
    td_4 = [el for el in td_4 if el]
    td_4 = [td_4[4+i:4+i+5] for i in range(0, len(td_4[4:]), 5)]
    df = pd.DataFrame(data=td_4, columns=th_4)
    return df

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
    df = pd.DataFrame(data=td_5, columns=th_5)
    return df

def parse_table_6(table: Tag):
    # Table 5: Battery Capacity History
    td_6 = [el.text.strip() for el in table.find_all('td')]
    th_6 = td_6[0:3]
    td_6 = [td_6[3+i:3+i+3] for i in range(0, len(td_6[3:]), 3)]
    df = pd.DataFrame(data=td_6, columns=th_6)
    return df

def parse_table_7_8(table1: Tag, table2: Tag):
    # Table 6: Battery Life Estimates
    td_7 = [el.text.strip() for el in table1.find_all('td')]
    th_7_l1 = td_7[0:4]
    th_7_l2 = td_7[4:10]
    th_7_l1.insert(2, th_7_l1[1])
    th_7_l1.append(th_7_l1[-1])
    th_7 = [f"{th_7_l1[i]} - {th_7_l2[i]}" for i in range(len(th_7_l1))]
    td_7 = [td_7[10+i:10+i+6] for i in range(0, len(td_7[10:]), 6)]
    df_7 = pd.DataFrame(data=td_7, columns=th_7)
    if not table2:
        return (df_7, None)

    # Table 7: Current estimate of battery life based on all observed drains since OS install
    # NOTE: Table has no th! So they are taken from the previous step.
    td_8 = [el.text.strip() for el in table2.find_all('td')]
    df_8 = pd.DataFrame(data=[td_8], columns=th_7)
    return (df_7, df_8)
    
TOTAL_TABLES = 8

def parse_table_by_id(table: Tag, idx: int) -> pd.DataFrame:
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
    
    raise BaseException('No known index is given!')

def parse_tables(
        tables: ResultSet[Tag],
        table_flags: List[bool],
        tables_container: List[List[Union[None,pd.DataFrame]]]):
    """Parser for Battery Report Tables

    Args:
        tables (ResultSet[Tag]):
            input array of table nodes from the report
        table_flags: (List[bool]):
            list of bools whether to add or skip parsing for specific tables
        tables_container: (List[List[Union[None,pd.DataFrame]]])
            container for parsed pandas dataframes, later to be merged
    """
    
    if not tables:
        return tables_container

    for ti, tf in enumerate(table_flags[:6]):
        if tf:
            print("Ti: %s" % ti)
            tables_container[ti].append(parse_table_by_id(tables[ti], ti))
    
    # Table 6: Battery Life Estimates &
    # Table 7: Current estimate of battery life based on all observed drains since OS install
    if table_flags[6] or table_flags[7]:
        p_td_7, p_td_8 = parse_table_7_8(tables[6], tables[7])
        if table_flags[6]:
            tables_container[6].append(p_td_7)
        if table_flags[7] and p_td_8 is not None and not p_td_8.empty:
            tables_container[7].append(p_td_8)

arg_parser = argparse.ArgumentParser(description="Windows Battery Report Parser & Analyser.")
group = arg_parser.add_mutually_exclusive_group(required=True)
group.add_argument('--input_dir', type=Path, help='Directory with reports to parse')
group.add_argument('--input_file', type=Path, help='Report File to parse')
arg_parser.add_argument('--tables', nargs="+", default='all', help='Tables to parse (default: %(default)s)')
arg_parser.add_argument('--output_dir', type=Path, help='Directory to save parsed reports to')

def parse_file(input_path):
    with input_path as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    tables = soup.find_all('table')
    return tables

def save_tables(
        tables_container: List[List[Union[None,pd.DataFrame]]],
        output_dir_path: Path,
        output_path_pattern: str):
    for idx, pt_df in enumerate(tables_container):
        print(10*'=')
        print(idx)
        if pt_df and type(pt_df[-1]) == pd.DataFrame:
            last_df : pd.DataFrame = pt_df[-1]
            print(last_df.head())
            # MOVE: saving to parquet / any other format
            output_path_df = output_dir_path / (output_path_pattern % idx)
            print(output_path_df)
            last_df.to_parquet(path=output_path_df)

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
    
    tables_container = []
    for _ in range(TOTAL_TABLES):
        tables_container.append([])

    for i, fp in enumerate(input_paths):
        print("I: %s / FP: %s " % (i, fp))
        output_path_pattern = f"test_{i}_%s.parquet"
        table_tags = parse_file(open(fp))
        parse_tables(table_tags, table_process_flags, tables_container)
        save_tables(tables_container, output_dir_path, output_path_pattern)