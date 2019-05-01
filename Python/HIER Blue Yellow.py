1# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 17:00:31 2019

@author: xcxg109
"""

import file_data as fd
import settings
import hierarchy as hier


grainger_df, search_level = hier.generate_data()


fd.data_out(settings.directory_name, grainger_df, search_level)