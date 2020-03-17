 # -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd

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
            
, merch AS (
    SELECT  id,
    		name,
            ARRAY[]::INTEGER[] AS ancestors,
            ARRAY[]::character varying[] AS ancestor_names
            
    FROM    merchandising_category as category
    
    WHERE   "parentId" IS NULL
        AND category.deleted = false
        AND category.visible = true

    UNION ALL

    SELECT  category.id,
			category.name,
            merch.ancestors || category."parentId",
            merch.ancestor_names || parent_category.name
            
    FROM    merchandising_category as category
    
    JOIN merch on category."parentId" = merch.id
    JOIN merchandising_category parent_category on category."parentId" = parent_category.id
    
    WHERE   category.deleted = false
        AND category.visible = true		
    )

, _tmp_attrs AS (
/*			--stack pivots*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'stack' as attr_type
		, collord.attribute_id
        
	FROM	( 
        SELECT
			coll."merchandisingCategoryId" as node_id
			, coll.id as collection_id
			, coll.name as collection_name
			, coll.visible as collection_visible
			, json_extract_path_text(json_array_elements(json_extract_path(json_array_elements("stacksConfiguration"), 'groupSelections')),'merchandisingAttributeId')::integer as attribute_id	
            , row_number() over() as coll_order

        FROM merchandising_collection coll
        
        WHERE coll.deleted = 'f'	
            AND coll.visible = 't'
	) collord	

	UNION
/*	--Table attributes*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'table' as attr_type
		, collord.attribute_id
        
	FROM	( 
        SELECT
			coll."merchandisingCategoryId" as node_id
			, coll.id as collection_id
			, coll.name as collection_name
			, coll.visible as collection_visible
			, json_extract_path_text(json_array_elements("orderedVisibleMerchandisingAttributes"), 'merchandisingAttributeId')::integer  as attribute_id
            , row_number() over() as coll_order
            
        FROM merchandising_collection coll
        
        WHERE coll.deleted = 'f' 	
            AND coll.visible = 't'
    ) collord

	UNION
/*	--Column groups*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'column group' as attr_type
		, collord.attribute_id
        
	FROM	( 
        SELECT
			coll."merchandisingCategoryId" as node_id
			, coll.id as collection_id
			, coll.name as collection_name
			, coll.visible as collection_visible
			, (json_extract_path(json_array_elements("columnGroupsConfiguration"), 'merchandisingAttributeId')::text)::integer as attribute_id	
            , row_number() over() as coll_order
            
        FROM merchandising_collection coll
        
        WHERE coll.deleted = 'f'	
            AND coll.visible = 't'
    ) collord

	UNION
/*	-- filters*/
	SELECT 
		z.node_id
		, coll.id  as collection_id
		, coll.name as collection_name
		, coll.visible as collection_visible
		, attr_type
		, attribute_id
        
	FROM (
		SELECT
			 node_id
			, 'filter'::text as attr_type
			, attribute_id
            
		FROM	(
            SELECT
                cat.id as node_id
				, unnest("sortedFiltersKeys")::integer  as attribute_id
				, "sortedFiltersKeys"
                
            FROM merchandising_category cat	
            
            WHERE cat.deleted = 'f'
                AND cat.visible = 't'
			) y		   
		)z 
    
	LEFT JOIN merchandising_collection coll
		ON coll."merchandisingCategoryId" = z.node_id
        AND coll.visible = 't'
        
    UNION
/*	-- PDP attributes*/
	SELECT 
		b.node_id
		, coll.id  as collection_id
		, coll.name as collection_name
		, coll.visible as collection_visible
		, attr_type
		, attribute_id
        
	FROM (
		SELECT
			 node_id
			, 'pdp'::text as attr_type
			, attribute_id
		FROM (  
			 SELECT
				cat.id as node_id
				, unnest("sortedVisiblePdpAttributeIds")::integer  as attribute_id
				, "sortedVisiblePdpAttributeIds"
                    
            FROM merchandising_category cat
            
            WHERE cat.deleted = 'f' AND cat.visible = 't'
            ) a		      
        ) b			
    
	LEFT JOIN merchandising_collection coll
			ON coll."merchandisingCategoryId" = b.node_id AND coll.visible = 't'
	)

            

    SELECT DISTINCT ON (_tmp_attrs.attr_type, merchatt.name)
          array_to_string(tax.ancestor_names || tax.name,' > ') as "Gamut_PIM_Path"
        , tax.ancestors[1] as "Gamut_Category_ID"  
        , tax.ancestor_names[1] as "Gamut_Category_Name"
        , tax_att."categoryId" AS "Gamut_Node_ID"
        , tax.name as "Gamut_Node_Name"
        , tax_att.id as "Gamut_Attr_ID"
        , tax_att.name as "Gamut_Attribute_Name"
        , tax_att.description as "Gamut_Attribute_Definition"
        , _tmp_attrs.attr_type as "Gamut_MERCH_Usage"
		
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
 -- AND (5550 = ANY(merch.ancestors)) --OR 2267 = ANY(merch.ancestors) OR 2268 = ANY(merch.ancestors) OR 2271 = ANY(merch.ancestors) OR 2215 = ANY(merch.ancestors) OR 2272 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN taxonomy_product as tprod
  ON tprod.id = mprod."taxonomyProductId"
	AND mprod.deleted = 'f'

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"

INNER JOIN _tmp_attrs
	ON _tmp_attrs.collection_id = mcollprod."collectionId"
	  
INNER JOIN  merchandising_product_value mprodvalue
    ON mprodvalue."merchandisingProductId" = mcollprod."merchandisingProductId"
    AND mprodvalue."merchandisingAttributeId" = _tmp_attrs.attribute_id
    AND mprodvalue.deleted = 'f'
  --  AND mprodvalue.value NOT IN ('-', '<null>', '?', 'Discontinued', 'N', 'N/aA', 'NA', 'No', 'None', 'Not Applicable', 'Not Available', 'Not Included', 'Not Rated')

INNER JOIN merchandising_attribute merchatt
    ON merchatt.id = _tmp_attrs.attribute_id
    AND merchatt.deleted = 'f'
 --   AND merchatt.name NOT IN ('Accessory Type', 'Also Known As', 'Application', 'Brand', 'Country of Origin', 'Country Of Origin', 'Features', 'For Use With', 'Includes', 'Package Quantity', 'System of Measure', 'System of Measurement', 'Warnings & Restrictions', 'Magnetism', 'Type')

INNER JOIN merchandising_attribute__taxonomy_attribute merchAtt_taxAtt
    ON merchAtt_taxAtt."merchandisingAttributeId" = merchatt.id

INNER JOIN taxonomy_attribute tax_att
    ON tax_att.id = merchAtt_taxAtt."attributeId"

INNER JOIN tax
    ON tax.id = tax_att."categoryId"

WHERE tprod.deleted = 'f'
  AND mcoll.visible = 't'
  AND {term} IN ({k})
""".format(term='tax_att."categoryId"', k=8786)


gamut_df = db.query(test_q)

gamut_df = gamut_df.groupby(['Gamut_PIM_Path', 'Gamut_Category_ID', 'Gamut_Category_Name', 'Gamut_Node_ID', \
                             'Gamut_Node_Name', 'Gamut_Attr_ID', 'Gamut_Attribute_Name', \
                             'Gamut_Attribute_Definition'])['Gamut_MERCH_Usage'].apply('; '.join).reset_index()
