 # -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:53:56 2019

@author: xcxg109
"""

from graingerio import TeraClient

tc = TeraClient()

class GraingerQuery:
    def grainger_q(self, query, attribute, data):
        """Query Teradata database using GRAINGER blue nodes, yellow nodes, or SKUs"""

        grainger_q = query.format(attribute, data)     #aattribute = SQL table
                
        query_df = tc.query(grainger_q)
        return query_df

    
    def __repr__(self):
        return str(self)