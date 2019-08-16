# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 17:32:06 2019

@author: xcxg109
"""

import os
from pathlib import Path
import re
import pandas as pd
import settings


def gamut_search_type():
    while True:
        try:
            data_type = input("Search by: \n1. Terminal Node\n2. Org Node\n3. SKU\n4. Other ")
            if data_type in ['1', 'node', 'Node', 'NODE', 'terminal', 'Termina', 'TERMINAL', 't', 'T']:
                data_type = 'node'
                break
            elif data_type in ['2', 'org', 'Org', 'ORG', 'o', 'O']:
                data_type = 'org'
                break
            elif data_type in ['3', 'sku', 'Sku', 'SKU', 's', 'S']:
                data_type = 'sku'
                break
            elif data_type in ['4', 'other', 'Other', 'OTHER', 'o', 'O']:
                data_type = 'other'
                break
        except ValueError:
            print('Invalid search type')
                    
    if data_type == 'other':
        while True:
            try:
                data_type = input ('Query Type?\n1. Attribute Value\n2. Attribute Name ')
                if data_type in ['attribute value', 'Attribute Value', 'value', 'Value', 'VALUE', '1']:
                    data_type = 'value'
                    break
                elif data_type in ['attribute name', 'Attribute Name', 'name', 'Name', 'NAME', '2']:
                    data_type = 'name'
                    break
            except ValueError:
                print('Invalid search type')
    
    return data_type



def gamut_data_in(data_type, directory_name):
#    type_list = ['Node', 'SKU']
    
    if data_type == 'node':
        search_data = input('Input Terminal Node ID or hit ENTER to read from file: ')
    elif data_type == 'org':
        search_data = input('Input Yellow node ID or hit ENTER to read from file: ')
    elif data_type == 'sku':
        search_data = input ('Input SKU or hit ENTER to read from file: ')
    elif data_type == 'value':
        search_data = input ('Input attribute value to search for: ')
    elif data_type == 'name':
        search_data = input ('Input attribute name to search for: ')
  
    if search_data != "":
        search_data = [search_data]
        return search_data
    else:
        #read file
#        file_name = settings.get_file_name()
#        file_path = Path(directory_name)/file_name  #setup the data file to read
#        file_path = os.path.join(directory_name, file_name)
#        file_data = [re.split('\s+', i.strip('\n')) for i in open(file_path)]
        file_data = settings.get_file_data()

        if data_type == 'node':
            search_data = [int(row[0]) for row in file_data[1:]]
            return search_data
        elif data_type == 'yellow':
            search_data = [str(row[0]) for row in file_data[1:]]
#            search_data = file_data
            return search_data
        elif data_type == 'sku':
            search_data = [row[0] for row in file_data[1:]]
            return search_data


def attr_data_out(directory_name, df, df_stats, df_fill, search_level):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    df['CATEGORY_NAME'] = modify_name(df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names   
    df.drop(columns=['Count', 'Fill_Rate %'], inplace=True)
    
    quer = 'ATTRIBUTES'
    outfile = outfile_name (directory_name, quer, df, search_level)

  #  outfile = Path(directory_name)/"{} {} ATTRIBUTES.xlsx".format(k, df.iloc[0,2])   #set directory path and name output file
    
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    df_stats.to_excel(writer, sheet_name='Stats', startrow=1, startcol=0)
    df_fill.to_excel(writer, sheet_name='Stats', startrow =5, startcol=5, index=False)
    df.to_excel(writer, sheet_name='Data', index=False)
    
    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet1 = writer.sheets['Stats']
    worksheet2 = writer.sheets['Data']
    
    layout = workbook.add_format({'align': 'left',
                                  'text_wrap': True})
    num_layout = workbook.add_format({'align': 'left',
                                  'text_wrap': True,
                                  'num_format': '##0.00'})

    #setup display for Stats sheet
    worksheet1.set_column('A:A', 40, layout)
    worksheet1.set_column('B:B', 60, layout)
    worksheet1.set_column('F:F', 40, layout)
    worksheet1.set_column('G:G', 15, num_layout)
    worksheet1.set_column('H:H', 20, layout)
    #steup display for Data sheet
    worksheet2.set_column('F:F', 25, layout)
    worksheet2.set_column('G:G', 30, layout)
    worksheet2.set_column('H:H', 60, layout)
    
    writer.save()
