# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 12:07:23 2019

@author: xcxg109
"""

import pandas as pd
from tkinter.filedialog import askopenfilename
from math import ceil
import file_data as fd
import settings
import heirarchy as h


def report_type():
    """choose whether to sample by node or supplier"""
    report_type = input('Sample by node or supplier? ')

    if report_type in ['blue', 'Blue', 'BLUE', 'node', 'Node', 'NODE']:
        report_type = 'node'
    elif report_type in ['supplier', 'Supplier', 'SUPPLIER', 's', 'S']:
        report_type = 'supplier'
    else:
        raise ValueError('Invalid search type')
        
    return report_type


def percentage_sample():
    """Determine number of SKUs based on a straight percenage"""
    samp_size = input('Input sample size as a percentage: ')
    sample = int(samp_size)/100

    return sample


def weighted_sample(sample_constant, report_type, supplier_count, sku_count):
    """Determine the number of SKUs to pull for each node weighted by node size. Change 'samp_size' variable to desired sample percentage"""
        
    sample = dict()
    #Weighted sample size (stratified sampling); choose a smaller number of SKUs from larger nodes for efficiency sake
    #NOTE: ceil(num *100)/100 is a way to force Python to round up
    if report_type == 'node':
        for index, row in sku_count.iterrows():
            samp_size = sample_constant
            if row['SKU Count']<100:
                samp_size = samp_size
            elif (row['SKU Count']>=100) & (row['SKU Count']<200):
                samp_size = ceil((samp_size*0.5)*100)/100
            elif (row['SKU Count']>200) & (row['SKU Count']<500):
                samp_size = ceil((samp_size*0.3)*100)/100
            elif row['SKU Count']>=500:
                samp_size = round(samp_size*0.2, 2)    
            count = (int(row['SKU Count']*samp_size))
            #Deal with small sample sizes -- if sample percentage as calculated above is <1, choose 2 SKUs from the sample if possible, or 1 if there is only one present
            if count <= 1:
                if row['SKU Count'] >= 2:
                    count = 2
                else:
                    count = 1
            sample[row['Category ID']] = count
    elif report_type == 'supplier':
        for index, row in supplier_count.iterrows():
            samp_size = sample_constant
            if row['SKU Count']<100:
                samp_size = samp_size
            elif (row['SKU Count']>=100) & (row['SKU Count']<200):
                samp_size = ceil((samp_size*0.5)*100)/100
            elif (row['SKU Count']>200) & (row['SKU Count']<500):
                samp_size = ceil((samp_size*0.3)*100)/100
            elif row['SKU Count']>=500:
                samp_size = round(samp_size*0.2, 2)    
            count = (int(row['SKU Count']*samp_size))
            #Deal with small sample sizes -- if sample percentage as calculated above is <1, choose 2 SKUs from the sample if possible, or 1 if there is only one present
            if count <= 1:
                if row['SKU Count'] >= 2:
                    count = 2
                else:
                    count = 1
            sample[row['Supplier Name']] = count
                
    return sample


def create_sample(sample, report_type, skus):
    """Pull random SKUs based on the sample size (determined in sample_size function). Create a dataframe holding just the sample SKUs"""
    sample_df = pd.DataFrame()

    if type(sample) == dict:
        if report_type == 'node':
            for key, value in sample.items():
                filter = skus['Category ID'] == key  #create a filter by node, used in the next line to generate a temporary dataframe
                temp_df = skus[filter].sample(n=value)   #temporary dataframe of n number of SKUs from the given node (filter)
                sample_df = pd.concat([sample_df, temp_df], axis=0)  #add the temp dataframe to the master sample list
        elif report_type == 'supplier':
            for key, value in sample.items():
                filter = skus_sup['Supplier Name'] == key  #create a filter by node, used in the next line to generate a temporary dataframe
                temp_df = skus_sup[filter].sample(n=value)   #temporary dataframe of n number of SKUs from the given node (filter)
                sample_df = pd.concat([sample_df, temp_df], axis=0)  #add the temp dataframe to the master sample list      
    elif type(sample) == float:
        sample_df = df.sample(frac=sample)
        sample_df = sample_df.filter(['Category ID', 'Material No'])

    return sample_df
    

filename = askopenfilename()
df = pd.read_csv(filename)

#create dataframe that lists all possible attributes, along with counts of how many times they are used
#atts = pd.value_counts(df['Attribute Name'].values, sort=True)
#atts = pd.DataFrame(data=atts, columns=['Counts for all Nodes']).rename_axis('Attribute Name').reset_index()

#create datafrome of SKU count by node
#sku_count = df.groupby('Category ID')['Material No'].nunique().reset_index(name='SKU Count')
sku_count = df.groupby('L3')['Grainger_SKU'].nunique().reset_index(name='SKU Count')
sku_count = sku_count.reset_index(drop=True)

#create datafrome of SKU count by supplier
#supplier_count = df.groupby('Supplier Name')['Material No'].nunique().reset_index(name='SKU Count')
#supplier_count = supplier_count.reset_index(drop=True)

sample_type = input('Choose sapmle type:\n    1. Straight percentage\n    2. Weighted average\n')

if sample_type in ['1', '%', '5', 'percent', 'percentage']:
    sample = percentage_sample()
elif sample_type in ['2', 'weighted', 'weight']:
    sample = percentage_sample()
    report_type = report_type()
    sample = weighted_sample(sample, report_type, supplier_count, sku_count)

    
#create dataframe of all SKUs and their related Category ID, plus the number of attributes for each SKU
#skus = df.groupby('Category ID')['Material No'].value_counts().reset_index(name='# of Attributes')
skus = df.groupby('L3')['Grainger_SKU'].value_counts().reset_index(name='count')
skus = skus.reset_index(drop=True)
skus.drop(['count'], axis=1, inplace=True)

#create dataframe of all SKUs and the Supplier Name, plus the number of attributes for each SKU
#skus_sup = df.groupby('Supplier Name')['Material No'].value_counts().reset_index(name='# of Attributes')

#generate a dataframe of random SKUs based on the stratified sample numbers generated in the 'sample_size' function
sample_df = create_sample(sample, report_type, skus)  #sample can be either a percent entered by the user OR a dictionary of weighted counts by node size
    #df = original datafram passed in for straight percentage random sample (when sample = percent entered by user)
    #skus = database of nodes and sku count per node, used to calculate the weighted sample if chosen

#fd.sample_data_out(settings.directory_name, sample_df, atts, skus_sup, skus, supplier_count, sku_count, df)