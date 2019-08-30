 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#ORIGINAL Gamut Test
#from postgres_client import PostgresDatabase
#db = PostgresDatabase()

#1.5 ADMIN Gamut Test
from postgres_client import PostgresDatabase
db = PostgresDatabase()



# no need for an open connection,
# as we're only doing a single query
#engine.dispose()


#def test_query(search, k):
test_q="""
   WITH RECURSIVE tax AS (
                SELECT  id,
            name,
            ARRAY[]::INTEGER[] AS ancestors,
            ARRAY[]::character varying[] AS ancestor_names
                FROM    taxonomy_category as category
                WHERE   "parentId" IS NULL
                AND category.deleted = false

                UNION ALL

                SELECT  category.id,
            category.name,
            tax.ancestors || tax.id,
            tax.ancestor_names || tax.name
                FROM    taxonomy_category as category
                INNER JOIN tax ON category."parentId" = tax.id
                WHERE   category.deleted = false

            )

    SELECT
          array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Terminal Node Path"
        , tprod."categoryId" AS "PIM Terminal Node ID"
        , tprod."gtPartNumber" as "Gamut Part Number"
        , tprod."supplierSku" as "Grainger SKU"
        , tax_att.name as "Attribute Name"
        , tax_att.description as "Attribute Definition"
        , tax_att."unitGroupId" AS "UOM ID"
        , tax_att."dataType" as "Data Type"
        , tprodvalue.value as "Original Value"
        , tprodvalue.unit as "UOM"
        , tprodvalue."valueNormalized" as "Normalized Value"
        , tprodvalue."unitNormalized" as "UOM"
   
    FROM  taxonomy_product tprod

    INNER JOIN tax
        ON tax.id = tprod."categoryId"
        --  AND (4458 = ANY(tax.ancestors)) --OR 8215 = ANY(tax.ancestors) OR 7739 = ANY(tax.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

    INNER JOIN taxonomy_attribute tax_att
        ON tax_att."categoryId" = tprod."categoryId"

    INNER JOIN  taxonomy_product_attribute_value tprodvalue
        ON tprod.id = tprodvalue."productId"
	AND tax_att.id = tprodvalue."attributeId"
        
    WHERE tprod.deleted = 'f'
           AND {term} IN ({k})
""".format(term='tprod."categoryId"', k=1510)


gamut_df = db.query(test_q)