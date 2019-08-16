# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 20:44:56 2019

@author: xcxg109
"""
from tkinter.filedialog import askopenfilename
import re



def get_file_data():
    file_name = askopenfilename(initialdir = directory_name)
    #file_path = Path(directory_name)/file_name  #setup the data file to read
#        file_path = os.path.join(directory_name, file_name)
    file_data = [re.split('\s+', i.strip('\n')) for i in open(file_name)]
    return file_data
#file_name = 'DATA.csv'  #read in SKUs or node list


directory_name = "F:/CGabriel/Grainger_Shorties/OUTPUT"