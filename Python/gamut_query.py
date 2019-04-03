# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:53:56 2019

@author: xcxg109
"""

from postgres_client import PostgresDatabase

db = PostgresDatabase()

class GamutQuery:
    def gamut_q(self, query, attribute, data):
        """Query Postgres database using GAMUT merch nodes or SKUs"""
        
        gamut_q = query.format(attribute, data)  #aattribute = SQL table
  
        query_df = db.query(gamut_q)       
        return query_df

    
    def __repr__(self):
        return str(self)