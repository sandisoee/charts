#!/usr/bin/env python3
"""
    populate helm chart values.yaml files from subchart values.yaml files
"""
from operator import sub
import sys
import re
import argparse
import os 
from pathlib import Path
import yaml


""" 
Todo:
    - take a dest values.yaml and multiple src values.yam as input params
    - write values to dest file 
    - ensure that the Globals section has all properties from all subcharts i.e diff and merge or perhaps 
      just check the longest set of global properties from the subcharts and use these 
    - probably create a shell script to run this util i.e. with the input params set
    - consider putting this into the pipleine when done.

"""
read_data = "" 

def get_subcharts_from_parent(pcy) : 
    """ 
            return a list of subcharts from the parent chart's chart.yaml
    """  
    parent_chart_data = "" 
    subchart_list = []
    with open(pcy, "r") as stream:
        try:
            parent_chart_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    dlist = parent_chart_data['dependencies']
    for i in range(len(dlist)): 
        if ( dlist[i]['name'] != 'common' ) :
            sc_dir=Path(dlist[i]['repository']).name
            subchart_list.append(sc_dir)
    print(subchart_list)
    return subchart_list            

def get_globals_offset (data) : 
    """
            get and return the pointer to the end of the Globals section of the 
            subchart
            returns : offset if found  or -1 if not found 
    """
    ### get the globals section from subchart values.yaml 
    globals_start=re.search('global:', data, re.MULTILINE)
    if globals_start: 
        print(globals_start)
        print(globals_start.end())
    globals_end=re.search('^[a-z]',data[globals_start.end():],re.MULTILINE)
    if globals_end: 
        print(globals_end.end())

    offset=globals_start.end() + globals_end.start()
    return globals_start.start() , offset

def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Automate helm parent chart values.yaml creation')
    parser.add_argument("-p", "--parentchart", required=True, help="parent chart name ")

    args = parser.parse_args(args)
    if len(sys.argv[1:])==0:
        parser.print_help()
        parser.exit()
    return args

##################################################
# main
##################################################
def main(argv) :
    args=parse_args()
    
    subcharts_list = [ "chart-admin", "chart-service"]
    subchart_data_list = []
    subchart_start_offset_list = []
    subchart_end_offset_list = []
    max_globals_sec = 0 
    max_ptr=0
    script_dir = Path( __file__ ).parent.absolute()
    parent_chart_dir = script_dir.parent / 'mojaloop' / args.parentchart
    parent_chart_yaml = parent_chart_dir / 'chart.yaml'
    parent_values_yaml = parent_chart_dir / 'values.yaml'
    charts_dir = script_dir.parent / 'mojaloop'
    print(parent_chart_dir)
    print(parent_values_yaml)
    print(parent_chart_yaml)
    
    # ensure that the parent chart dir and chart.yaml exist
    if not (parent_chart_dir.is_dir() and parent_chart_yaml.exists() ) : 
        print(f"Error: missing parent chart directory or chart.yaml")
        sys.exit("....exiting")

    subcharts_list = get_subcharts_from_parent(parent_chart_yaml)
    if (len(subcharts_list) == 0 ) : 
        print(f"no subcharts for {arg.parentchart}")
        print("exiting")
        sys.exit()

    for i in range(len(subcharts_list)) : 
        with open(charts_dir / subcharts_list[i] / "values.yaml") as f:
            read_data = f.read()
        subchart_data_list.append(read_data)
        sos, eos = get_globals_offset(read_data)
        subchart_start_offset_list.append(sos)
        subchart_end_offset_list.append(eos)
        if (eos - sos > max_globals_sec ) :
            max_ptr = i
            max_globals_sec=eos-sos 
    
    # write the globals section to the toplevel chart from the subchart with the 
    # longest globals section. 
    with open(parent_values_yaml,'w') as f:
        s = subchart_data_list[max_ptr]
        globals_section=s[subchart_start_offset_list[max_ptr]:subchart_end_offset_list[max_ptr] ]
        print (globals_section, file=f)
        print("## configurable values for subcharts ", file=f)

        ### now add the subchart specific sections
        for i in range(len(subcharts_list)) : 
            sc_data = subchart_data_list[i]
            sc_offset =  subchart_end_offset_list[i]
            print(f"{subcharts_list[i]}:",file=f)
            x = sc_data[sc_offset:].split('\n')
            print('  ', end='', file=f)
            print('\n  '.join(x) , end='\n',file=f)
    

        



if __name__ == "__main__":
    main(sys.argv[1:])
