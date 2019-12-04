# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 17:30:17 2019

@author: xcxg109
"""
from grainger_query import GraingerQuery
from queries import grainger_sales_query
import pandas as pd
import file_data as fd
import settings
import datetime


gcom = GraingerQuery()

def get_sales(grainger_df):
    #groupby L3 to get sums of sales by category
    sales_df = grainger_df.groupby(['L3'])['Sales'].sum().reset_index()
    #grab 1 row for each L3 to add back into sales_df
    cat_l3 = grainger_df.drop_duplicates(subset='L3')
    cat_l3 = cat_l3.drop(['Sales', 'Grainger_SKU', 'Sales_Status', 'Supplier_ID', 'Supplier', 'GP'], axis=1)
    #merge the two databases

    sales_df = cat_l3.merge(sales_df, how="left", on=['L3'])
    sales_df = sales_df.sort_values(by=['Sales'], ascending=False)
    
    #create dictionary of L3s and their sales ranking
    rank = sales_df['L3'].tolist()
    sales_rank = dict()
    
    for i in range(len(rank)):
        sales_rank[i] = rank[i]

    rank = {v: k for k, v in sales_rank.items()}
    
    return sales_df, rank


def get_supplier(grainger_df, rank):
    #create the df that becomes the SKUs by supplier tab
    
    supplier_df = grainger_df.groupby(['L3', 'Supplier_ID'])['Grainger_SKU'].count().reset_index()
    
    #get unique values of all L3 rows and keep only seg/familiy/cat values
    cat_l3 = grainger_df.drop_duplicates(subset=['L3', 'Supplier_ID'])
    cat_l3 = cat_l3.drop(['Sales', 'Grainger_SKU', 'Sales_Status', 'GP'], axis=1)

    #merge the two dfs to end up with SKU_Count for each supplier grouped by L3
    supplier_df = cat_l3.merge(supplier_df, how="inner", on=['L3', 'Supplier_ID'])
    #sales_df = sales_df.sort_values(by=['Sales'], ascending=False)
    supplier_df.rename(columns={'Grainger_SKU':'SKU_Count'}, inplace=True)
    
    #order by sales rank then drop that column
    supplier_df['Sales_Rank'] = supplier_df['L3'].apply(lambda x: rank.get(x))
    supplier_df = supplier_df.sort_values(by=['Sales_Rank', 'SKU_Count'], ascending=[True, False])
    supplier_df.drop('Sales_Rank', axis=1, inplace=True)

    return supplier_df


def supplier_skus(grainger_df, rank, top_cats):
    #rank suppliers based on the number of SKUs in the top 10 saels categories
    #this df is printed on the right hand of the Sales tab
    grainger_df['Sales_Rank'] = grainger_df['L3'].apply(lambda x: rank.get(x))
    
    top_suppliers = grainger_df[grainger_df.Sales_Rank < top_cats]
    top_suppliers = top_suppliers.sort_values(by=['Sales_Rank'], ascending=[True])

    top_suppliers = top_suppliers.groupby(['Supplier_ID'])['Grainger_SKU'].count().reset_index()
       
    cat_supp = grainger_df.drop_duplicates(subset=['Supplier_ID'])
    cat_supp = cat_supp.drop(['Grainger_SKU', 'L1', 'SEGMENT_NAME', 'L2', 'FAMILY_NAME', 'L3',
                              'CATEGORY_NAME', 'Sales', 'Sales_Status', 'GP', 'Sales_Rank'], axis=1)
    
    top_suppliers.rename(columns={'Grainger_SKU':'SKU_Count'}, inplace=True)

    top_suppliers = cat_supp.merge(top_suppliers, how="inner", on=['Supplier_ID'])
    top_suppliers = top_suppliers.sort_values(by=['SKU_Count'], ascending=False).head(5)
    
    return top_suppliers
    

def vendor_data(supplier_df, rank, top_cats, min_skus):
    #collect data to send to vendors, printed in a separate spreadsheet from other outputs
    #output will be top 10 categories with top 5 suppliers by SKU count for each of these top 10 categories
    supplier_df['Sales_Rank'] = supplier_df['L3'].apply(lambda x: rank.get(x))
    
    cat_suppliers = supplier_df[supplier_df.Sales_Rank < top_cats]
    cat_suppliers = cat_suppliers.sort_values(by=['Sales_Rank', 'SKU_Count'], ascending=[True,False])
    cat_suppliers = cat_suppliers.groupby('L3').head(5)
    
    #cat_suppliers = cat_suppliers.groupby('L3').filter(lambda x: (x['SKU_Count'] > min_skus))
    #cat_suppliers = cat_suppliers[cat_suppliers.SKU_Count.gt(min_skus).groupby([cat_suppliers.L3]).transform('any')]
    
    cat_suppliers = cat_suppliers[cat_suppliers['SKU_Count'].apply(lambda x: x > min_skus)]
    
    cat_suppliers.drop('Sales_Rank', axis=1, inplace=True)
    supplier_df.drop('Sales_Rank', axis=1, inplace=True)
    
    return cat_suppliers
        
    

def data_out(grainger_df, sales_df, supplier_df, top_suppliers):
    outfile = 'F:\CGabriel\Grainger_Shorties\OUTPUT\SALES.xlsx'
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')

    sales_df.to_excel(writer, sheet_name='Sales', startrow=1, startcol=0, index=False) 
    top_suppliers.to_excel(writer, sheet_name='Sales', startrow =1, startcol=9, index=False)

    supplier_df.to_excel(writer, sheet_name='SKUs by Supplier', startrow=0, startcol=0, index=False)
    grainger_df.to_excel(writer, sheet_name='Sales by SKU', startrow=0, startcol=0, index=False)

    workbook  = writer.book
    worksheet1 = writer.sheets['Sales']
    worksheet2 = writer.sheets['SKUs by Supplier']
    worksheet3 = writer.sheets['Sales by SKU']
 
    cell_format = workbook.add_format()
    cell_format.set_font_size(14)
    cell_format.set_bold()
    
    layout = workbook.add_format()
    layout.set_text_wrap('text_wrap')
    layout.set_align('left')
    
    sales_layout = workbook.add_format()
    sales_layout.set_num_format('#,##0.00')

    num_layout = workbook.add_format()
    num_layout.set_num_format('#,##0')

    worksheet1.write(0, 0, 'L3 Categories Ranked by Sales', cell_format)    
    worksheet1.set_column('B:B', 30, layout)
    worksheet1.set_column('D:D', 30, layout)
    worksheet1.set_column('F:F', 40, layout)
    worksheet1.set_column('G:G', 20, num_layout)
    worksheet1.write(0, 9, 'Top 5 Suppliers from top 10 Sales Categories', cell_format)
    worksheet1.set_column('J:J', 20, layout)
    worksheet1.set_column('K:K', 40, layout)
    worksheet1.set_column('L:L', 15, num_layout)
    

    worksheet2.set_column('B:B', 30, layout)
    worksheet2.set_column('D:D', 30, layout)
    worksheet2.set_column('F:F', 40, layout)
    worksheet2.set_column('G:G', 20, layout)
    worksheet2.set_column('H:H', 40, layout)
    worksheet2.set_column('I:I', 15, num_layout)
 
    worksheet3.set_column('A:A', 15, layout)
    worksheet3.set_column('B:B', 15, layout)
    worksheet3.set_column('C:C', 20, sales_layout)
    worksheet3.set_column('D:D', 20, sales_layout)
    worksheet3.set_column('F:F', 25, layout)
    worksheet3.set_column('H:H', 25, layout)
    worksheet3.set_column('J:J', 25, layout)
    worksheet3.set_column('K:K', 15, layout)
    worksheet3.set_column('L:L', 40, layout)
    writer.save()
    

def vendor_data_out(vendor_df):
#output separate spreasheet for TCS
    outfile = 'F:\CGabriel\Grainger_Shorties\OUTPUT\Vendor File.xlsx'
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    
    vendor_df.to_excel(writer, sheet_name='Master List', startrow=1, startcol=0, index=False) 

    workbook  = writer.book
    worksheet1 = writer.sheets['Master List']
    
    layout = workbook.add_format()
    layout.set_text_wrap('text_wrap')

    num_layout = workbook.add_format()
    num_layout.set_num_format('#,##0')
                              
    worksheet1.set_column('B:B', 30, layout)
    worksheet1.set_column('D:D', 30, layout)
    worksheet1.set_column('F:F', 40, layout)
    worksheet1.set_column('G:G', 20, layout)
    worksheet1.set_column('H:H', 40, layout)
    worksheet1.set_column('I:I', 15, num_layout)

    writer.save()
    
    
#determine SKU or node search
data_type = fd.search_type()
search_level = 'cat.CATEGORY_ID'

grainger_df = pd.DataFrame()
temp_df = pd.DataFrame()

if data_type == 'node':
    search_level = fd.blue_search_level()

search_data = fd.data_in(data_type, settings.directory_name)

print('working...')
print(datetime.datetime.now())

if data_type == 'node':
    for k in search_data:
        temp_df = gcom.grainger_q(grainger_sales_query, search_level, k)
        if temp_df.empty == False:
          #  if search_level == 'cat.CATEGORY_ID':
            grainger_df = grainger_df.append(temp_df)
            #else:
             #   pass
        else:
           print('All SKUs are R4, R9, or discontinued')
        print(k)

####################################################################################################################################
#change top_sales to determine how many L3 categories are used to pull the number of SKUs per supplier to determine
#top suppliers in the best selling nodes
top_cats = 10  #number of categories that are considered for sending to Vendors
min_skus = 25  #minimum number of SKUs used for including a supplier in the list sent to Vendors
####################################################################################################################################

if grainger_df.empty == False:
    sales_df, rank = get_sales(grainger_df)
    supplier_df = get_supplier(grainger_df, rank)
    top_suppliers = supplier_skus(grainger_df, rank, top_cats)
    grainger_df.drop('Sales_Rank', axis=1, inplace=True)
    vendor_df = vendor_data(supplier_df, rank, top_cats, min_skus)
    data_out(grainger_df, sales_df, supplier_df, top_suppliers)
    vendor_data_out(vendor_df)

print(datetime.datetime.now())