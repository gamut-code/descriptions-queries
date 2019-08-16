# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 12:07:23 2019

@author: xcxg109
"""

import pandas as pd
from math import ceil
import file_data as fd
import settings
import hierarchy as hier


def sample_type(sku_count):
    """Ask user whether to pull straight percentage or weighted sample based on number of SKUs in each L3 node"""
    sample_type = input('Choose sapmle type:\n    1. Straight percentage\n    2. Weighted average\n')

    if sample_type in ['1', '%', '5', 'percent', 'percentage']:
        sample = percentage_sample()
    elif sample_type in ['2', 'weighted', 'weight']:
        sample = percentage_sample()
        sample = weighted_sample(sample, sku_count)
    
    return sample
    

def percentage_sample():
    """Determine number of SKUs based on a straight percenage"""
    samp_size = input('Input sample size as a percentage: ')
    sample = float(samp_size)/100

    return sample


def weighted_sample(samp_size, sku_count):
    """Determine the number of SKUs to pull for each node weighted by node size. Change 'samp_size' variable to desired sample percentage"""
        
    sample = dict()
    #Weighted sample size (stratified sampling); choose a smaller number of SKUs from larger nodes for efficiency sake
    #NOTE: ceil(num *100)/100 is a way to force Python to round up
    for index, row in sku_count.iterrows():
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
        if count <= 3:
            if row['SKU Count']>=3:
                count = 3
            else:
                count = row['SKU Count']
        sample[row['L3']] = count
                
    return sample


def create_sample(sample, skus):
    """Pull random SKUs based on the sample size (determined in sample_size function). Create a dataframe holding just the sample SKUs"""
    sample_df = pd.DataFrame()

    if type(sample) == dict:
        for key, value in sample.items():
            filter = skus['L3'] == key  #create a filter by node, used in the next line to generate a temporary dataframe
            temp_df = skus[filter].sample(n=value)   #temporary dataframe of n number of SKUs from the given node (filter)
            sample_df = pd.concat([sample_df, temp_df], axis=0)  #add the temp dataframe to the master sample list     
    elif type(sample) == float:
        sample_df = skus.sample(frac=sample)
        sample_df = sample_df.filter(['L3', 'Grainger_SKU'])

    return sample_df


grainger_df, search_level = hier.generate_data()

#create datafrome of SKU count by node
sku_count = grainger_df.groupby('L3')['Grainger_SKU'].nunique().reset_index(name='SKU Count')
sku_count = sku_count.reset_index(drop=True)

sample = sample_type(sku_count)
    
#create dataframe of all SKUs and their related Category ID, plus the number of attributes for each SKU
skus = grainger_df.groupby('L3')['Grainger_SKU'].value_counts().reset_index(name='count')
skus = skus.reset_index(drop=True)
skus.drop(['count'], axis=1, inplace=True)

#generate a dataframe of random SKUs based on the stratified sample numbers generated in the 'sample_size' function
sample_df = create_sample(sample, skus)  #sample can be either a percent entered by the user OR a dictionary of weighted counts by node size
    #skus = database of nodes and sku count per node, used to calculate the weighted sample if chosen
if sample_df.empty:
    print('Sample size too small to get a result')
else:
    audit_df = grainger_df.merge(sample_df, on='Grainger_SKU', how='inner', suffixes=('_',''))
    audit_df.drop('L3_', axis=1, inplace=True)
    print('audit_df size: {}'.format(audit_df.shape))
    fd.sample_data_out(settings.directory_name, sku_count, audit_df, grainger_df, sample, search_level)
