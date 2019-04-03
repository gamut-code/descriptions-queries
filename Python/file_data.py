# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 20:58:51 2019

@author: xcxg109
"""
import os
import re
import pandas as pd


def search_type():
 #   data_type = input ('Select data type: ", date_type[0], data_type[1])
     data_type = input("Search by Grainger Node or SKU? ")
     if data_type in ['node', 'Node', 'NODE']:
         data_type = 'node'
     elif data_type in ['sku', 'Sku', 'SKU']:
         data_type = 'sku'
     else:
         raise ValueError('Invalid search type. Expected Node or SKU')
     return data_type


def modify_name(df, replace_char, replace_with):
    return df.str.replace(replace_char, replace_with)


def col_order(df, order):
    """arrange data for output"""
    cols = df.columns.tolist()
    cols = [cols[i] for i in order]
    df = df[cols]
    return df


def data_in(data_type, directory_name, file_name):
#    type_list = ['Node', 'SKU']
    
    if data_type == 'node':
        search_data = input('Input Node or hit ENTER to read from file: ')
    elif data_type == 'sku':
        search_data = input ('Input SKU or hit ENTER to read from file: ')
    
    if search_data != "":
        search_data = [search_data]
        return search_data
    else:
        #read file
        file_path = os.path.join(directory_name, file_name)
        file_data = [re.split('\s+', i.strip('\n')) for i in open(file_path)]
        if data_type == 'node':
            search_data = [int(row[0]) for row in file_data[1:]]
            return search_data
        elif data_type == 'sku':
            search_data = [row[0] for row in file_data[1:]]
            return search_data


def shorties_data_out(grainger_df, gamut_df, k):
    """merge Granger and Gamut data and output as Excel file"""
 
    grainger_df['CATEGORY_NAME'] = modify_name(grainger_df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names   
    #if gamut data is present for these skus, merge with grainger data
    if gamut_df.empty == False:
        grainger_df = grainger_df.merge(gamut_df, how="left", on=["Grainger_SKU"])
        order = [0, 9, 1, 2, 3, 6, 4, 5, 10, 11, 12, 8, 7]
        grainger_df = col_order(grainger_df, order)
        outfile = "{} {}.xlsx".format(k, grainger_df.iloc[0,4])
    else:
        outfile = "{} {}.xlsx".format(k, grainger_df.iloc[0,3])

    grainger_df.to_excel (outfile, index=None, header=True, encoding='utf-8')
    
def attr_data_out (df, df_stats, df_fill, k):
    # Create a Pandas Excel writer using XlsxWriter as the engine.

    df['CATEGORY_NAME'] = modify_name(df['CATEGORY_NAME'], '/', '_') #clean up node names to include them in file names   
    outfile = "{} {} ATTRIBUTES.xlsx".format(k, df.iloc[0,2])
    
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    df_stats.to_excel(writer, sheet_name='Stats', startrow=1, startcol=0)
    df_fill.to_excel(writer, sheet_name='Stats', startrow =5, startcol=5)
    df.to_excel(writer, sheet_name='Data')
    
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
    worksheet1.set_column('F:F', 60, layout)
    worksheet1.set_column('G:G', 15, num_layout)
    #steup display for Data sheet
    worksheet2.set_column('H:H', 30, layout)
    worksheet2.set_column('I:I', 60, layout)
    
    writer.save()

