# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 20:58:51 2019

@author: xcxg109
"""
import os
from pathlib import Path
import re
import pandas as pd


def search_type():
    """choose which type of data to import -- impacts which querries will be run"""
    while True:
        try:
            data_type = input("Search by: \n1. Blue (node)\n2. Yellow\n3. SKU\n4. Other ")
            if data_type in ['1', 'node', 'Node', 'NODE', 'blue', 'Blue', 'BLUE', 'b', 'B']:
                data_type = 'node'
                break
            elif data_type in ['2', 'yellow', 'Yellow', 'YELLOW', 'y', 'Y']:
                data_type = 'yellow'
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


def blue_search_level():
    """If data type is node (BLUE data), ask for segment/family/category level for pulling the query. This output feeds directly into the query"""
    while True:
        try:
            search_level = input("Search by: \n1. Segement (L1)\n2. Family (L2)\n3. Category (L3) ")
            if search_level in ['1', 'Segment', 'segment', 'SEGMENT', 'l1', 'L1']:
                search_level = 'cat.SEGMENT_ID'
                break
            elif search_level in ['2', 'Family', 'family', 'FAMILY', 'l2', 'L2']:
                search_level = 'cat.FAMILY_ID'
                break
            elif search_level in ['3', 'Category', 'category', 'CATEGORY', 'l3', 'L3']:
                search_level = 'cat.CATEGORY_ID'
                break
        except ValueError:
            print('Invalid search type')

    return search_level


def modify_name(df, replace_char, replace_with):
    return df.str.replace(replace_char, replace_with)


def col_order(df, order):
    """arrange data for output"""
    cols = df.columns.tolist()
    cols = [cols[i] for i in order]
    df = df[cols]
    return df


#function to get node/SKU data from user or read from the data.csv file
def data_in(data_type, directory_name, file_name):
#    type_list = ['Node', 'SKU']
    
    if data_type == 'node':
        search_data = input('Input Blue node ID or hit ENTER to read from file: ')
    elif data_type == 'yellow':
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
        file_path = Path(directory_name)/file_name  #setup the data file to read
#        file_path = os.path.join(directory_name, file_name)
        file_data = [re.split('\s+', i.strip('\n')) for i in open(file_path)]
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


#general output to xlsx file, used for the basic query
def data_out(directory_name, grainger_df, search_level):
    """basic output for any Grainger query""" 
    os.chdir(directory_name) #set output file path
    
    if grainger_df.empty == False:
      #  grainger_df['CATEGORY_NAME'] = modify_name(grainger_df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names
        if search_level == 'cat.SEGMENT_ID':
            outfile = Path(directory_name)/"{} HIER.xlsx".format(grainger_df.iloc[0,2])
        elif search_level == 'cat.FAMILY_ID':
            outfile = Path(directory_name)/"{} HIER.xlsx".format(grainger_df.iloc[0,4])
        else:
            outfile = Path(directory_name)/"{} HIER.xlsx".format(grainger_df.iloc[0,6])
        grainger_df.to_excel (outfile, index=None, header=True, encoding='utf-8')
    else:
        print('EMPTY DATAFRAME')


#output for short descriptions for Grainger and Gamut
def shorties_data_out(directory_name, grainger_df, gamut_df, k):
    """merge Granger and Gamut data and output as Excel file"""
    
    grainger_df['CATEGORY_NAME'] = modify_name(grainger_df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names   
 
    #if gamut data is present for these skus, merge with grainger data
    if gamut_df.empty == False:
        grainger_df = grainger_df.merge(gamut_df, how="left", on=["Grainger_SKU"])
        order = [0, 9, 1, 2, 3, 6, 4, 5, 10, 11, 12, 8, 7]
        grainger_df = col_order(grainger_df, order)
        outfile = Path(directory_name)/"{} {}.xlsx".format(k, grainger_df.iloc[0,4])    #set directory path and name output file
    else:
        outfile = Path(directory_name)/"{} {}.xlsx".format(k, grainger_df.iloc[0,3])

    grainger_df.to_excel (outfile, index=None, header=True, encoding='utf-8')
    
    
#output for attribute values for Grainger
def attr_data_out(directory_name, df, df_stats, df_fill, k):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    df['CATEGORY_NAME'] = modify_name(df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names   
    df.drop(columns=['Count', 'Fill_Rate %'], inplace=True)
    outfile = Path(directory_name)/"{} {} ATTRIBUTES.xlsx".format(k, df.iloc[0,2])   #set directory path and name output file
    
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


#output for specific sample pull
def sample_data_out(directory_name, sku_count, audit_df, df, sample):
    """Create the Audit Analysis spreadsheet. 'Audit List' (sheet 1) = the list of SKUs to be audited)"""
    outfile = Path(directory_name)/"{} AUDIT LIST.xlsx".format(df.iloc[0,2])   #set directory path and name output file

    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')

    order = [0, 1, 2, 3, 4, 10, 5, 6, 7, 8, 9]
    audit_df = col_order(audit_df, order)
    # Write each dataframe to a different worksheet.
    audit_df.to_excel(writer, sheet_name='Audit List', index=False)
    sku_count.to_excel(writer, sheet_name='L3 SKU Counts', index=False)
    df.to_excel(writer, sheet_name='Original Data', index=False)
    
    if type(sample) == dict:
        weightedSample = pd.DataFrame([sample]).T
        weightedSample.to_excel(writer, sheet_name='Weighted Sample Counts')
            
    workbook  = writer.book

    worksheet1 = writer.sheets['Audit List']
    worksheet2 = writer.sheets['L3 SKU Counts']
    
    layout = workbook.add_format({'align': 'left',
                                  'text_wrap': True})

    worksheet1.set_column('A:A', 15, layout)
    worksheet1.set_column('B:B', 10, layout)
    worksheet1.set_column('C:C', 25, layout)
    worksheet1.set_column('E:E', 35, layout)
    worksheet1.set_column('G:G', 30, layout)
    worksheet1.set_column('I:I', 15, layout)
    worksheet1.set_column('J:J', 30, layout)
    worksheet1.set_column('K:K', 30, layout)
       
    worksheet2.set_column('A:A', 20, layout)
    worksheet2.set_column('B:B', 20, layout)

    writer.save()