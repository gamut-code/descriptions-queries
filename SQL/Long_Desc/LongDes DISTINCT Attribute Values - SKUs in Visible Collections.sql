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

            

SELECT DISTINCT ON (merchatt."productPageDisplay", mprodvalue.value)
  array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
  , tprod."gtPartNumber" as "Gamut Part Number"
  , noun."primaryNoun" as "Primary Noun"
  , merchatt."productPageDisplay" as "Attribute Name"
  , mprodvalue.value as "Attribute Value"
  , mcoll.name as "Collection Name"
  
  
FROM  merchandising_product as mprod

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
 -- AND (3581 = ANY(merch.ancestors)) --OR 129 = ANY(merch.ancestors)) -- OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN taxonomy_product as tprod
  ON tprod.id = mprod."taxonomyProductId"
	AND mprod.deleted = 'f'

LEFT JOIN taxonomy_product_primary_noun noun
  ON noun."supplierSku" = tprod."supplierSku"

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"
  
INNER JOIN  merchandising_product_value mprodvalue
  ON mprod.id = mprodvalue."merchandisingProductId"
  AND mprodvalue.deleted = 'f'
  AND mprodvalue.value NOT IN ('-', '<null>', '?', 'Discontinued', 'N', 'N/aA', 'NA', 'No', 'None', 'Not Applicable', 'Not Available', 'Not Included', 'Not Rated')
  
INNER JOIN merchandising_attribute merchatt
  ON merchatt.id = mprodvalue."merchandisingAttributeId"
  AND merchatt.deleted = 'f'
  AND merchatt.name NOT IN ('Accessory Type', 'Also Known As', 'Application', 'Brand', 'Country of Origin', 'Country Of Origin', 'Features', 'For Use With', 'Includes', 'Package Quantity', 'System of Measure', 'System of Measurement', 'Warnings & Restrictions', 'Magnetism', 'Type', 'California Prop65 Warning Messaging Scenario')

WHERE tprod.deleted = 'f'
  AND mcoll.visible = 't'
--AND mcoll.name LIKE '%Kit%'
--AND mprod."merchandisingCategoryId" IN (
--AND tprod."gtPartNumber" IN ('522Z921')
--AND LOWER(merchatt.name) LIKE LOWER('%Light Output Modes%')
--AND mprodvalue.value LIKE '%Reflexite%'
--AND merchatt.id IN (79961)

ORDER BY merchatt."productPageDisplay"
       , mprodvalue.value
       , merchatt.name
       , mprod."merchandisingCategoryId" 