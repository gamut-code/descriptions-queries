# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:53:56 2019

@author: xcxg109
"""

from postgres_GWS import PostgresDatabase_GWS

db = PostgresDatabase_GWS()


class GWSQuery:
    def gws_q(self, query, attribute, data):
        """Query Postgres database using new GWS login"""
        
        gws_q = query.format(attribute, data)  #aattribute = SQL table
  
        query_df = db.query(gws_q)       
        return query_df

    
    def __repr__(self):
        return str(self)