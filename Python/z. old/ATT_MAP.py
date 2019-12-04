# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:10:22 2019

@author: xcxg109
"""

from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd



Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file

df = pd.read_csv(filename, dtype='unicode')
df.columns = df.columns.str.replace(' ', '_')