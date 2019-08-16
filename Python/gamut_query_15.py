# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:53:56 2019

@author: xcxg109
"""

from postgres_gamut_15 import PostgresDatabase_15

db = PostgresDatabase_15()


class GamutQuery_15:
    def gamut_q15(self, query, attribute, data):
        """Query Postgres database using GAMUT merch nodes or SKUs"""
        
        gamut_q15 = query.format(attribute, data)  #aattribute = SQL table
  
        query_df15 = db.query(gamut_q15)       
        return query_df15

    
    def __repr__(self):
        return str(self)