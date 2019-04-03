WITH RECURSIVE merch AS (
                SELECT  id,
			name,
                    ARRAY[]::INTEGER[] AS ancestors,
                    ARRAY[]::character varying[] AS ancestor_names
                FROM    merchandising_category as category
                WHERE   "parentId" IS NULL
                AND category.deleted = false
                 and category.visible = true

                UNION ALL

                SELECT  category.id,
			category.name,
                    merch.ancestors || category."parentId",
                    merch.ancestor_names || parent_category.name
                FROM    merchandising_category as category
                    JOIN merch on category."parentId" = merch.id
                    JOIN merchandising_category parent_category on category."parentId" = parent_category.id
                WHERE   category.deleted = false
			and category.visible = true		
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
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, json_extract_path_text(json_array_elements(json_extract_path(json_array_elements("stacksConfiguration"), 'groupSelections')),'merchandisingAttributeId')::integer as attribute_id	
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f'	AND coll.visible = 't'
		       ) y
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
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, json_extract_path_text(json_array_elements("orderedVisibleMerchandisingAttributes"), 'merchandisingAttributeId')::integer  as attribute_id
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f' 	AND coll.visible = 't'
		       ) y
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
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, (json_extract_path(json_array_elements("columnGroupsConfiguration"), 'merchandisingAttributeId')::text)::integer as attribute_id	
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f'	AND coll.visible = 't'
		       ) y
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
		, relative_rank
	FROM (
		SELECT
			
			 node_id
			, 'filter'::text as attr_type
			, attribute_id
			, row_number() OVER(Partition by node_id ORDER BY rattr ASC) AS relative_rank
		FROM	(
			SELECT *, row_number() over() as rattr
			FROM
			    (  
			     SELECT
					cat.id as node_id
					, unnest("sortedFiltersKeys")::integer  as attribute_id
					, "sortedFiltersKeys"
			       FROM merchandising_category cat
			       WHERE cat.deleted = 'f' AND cat.visible = 't'
			      ) y		      
			) x			
		)z 
	LEFT JOIN merchandising_collection coll
		ON coll."merchandisingCategoryId" = z.node_id AND coll.visible = 't'
--	WHERE relative_rank = 1
	)

            

SELECT DISTINCT ON (_tmp_attrs.attr_type, merchatt.name)
    array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
 -- , mprod.id as "Merchandising Product ID"
 -- , tprod."gtPartNumber" as "Gamut Part Number"
  , merchatt.name as "Attribute Name"
  , merchatt."dataType" as "Data Type"
 -- , mprodvalue.value as "Attribute Value"
  , mcoll.name as "Collection Name"
  , _tmp_attrs.collection_id
  , _tmp_attrs.attr_type as usage
 -- , _tmp_attrs.relative_rank
		
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
  AND (5550 = ANY(merch.ancestors)) --OR 2267 = ANY(merch.ancestors) OR 2268 = ANY(merch.ancestors) OR 2271 = ANY(merch.ancestors) OR 2215 = ANY(merch.ancestors) OR 2272 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
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

WHERE tprod.deleted = 'f'
  AND mcoll.visible = 't'
 -- AND mprod."merchandisingCategoryId" IN (4917)


ORDER BY _tmp_attrs.attr_type
    , merchatt.name
    , mprod."merchandisingCategoryId"

 