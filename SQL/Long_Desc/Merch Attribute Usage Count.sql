
WITH RECURSIVE merch AS (
                SELECT  id,
			name,
                    ARRAY[]::INTEGER[] AS ancestors,
                    ARRAY[]::character varying[] AS ancestor_names
                FROM    merchandising_category as category
                WHERE   "parentId" IS NULL
                AND category.deleted = false

                UNION ALL

                SELECT  category.id,
			category.name,
                    merch.ancestors || category."parentId",
                    merch.ancestor_names || parent_category.name
                FROM    merchandising_category as category
                    JOIN merch on category."parentId" = merch.id
                    JOIN merchandising_category parent_category on category."parentId" = parent_category.id
                WHERE   category.deleted = false                  
            ) 

SELECT 
	merchatt.name AS "Attribute Name"
	, COUNT (merchatt.name) AS "Use Count"
	, array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Node Path"
	, merch.id as "Merchandising Terminal Node ID"
	, merchatt."dataType" as "Data Type"

FROM merch

INNER JOIN merchandising_attribute merchatt
  ON merch.id = merchatt."merchandisingCategoryId"
  AND merchatt.deleted = 'f'

GROUP BY
	"Merchandising Node Path"
	, "Merchandising Terminal Node ID"
	, "Attribute Name"
	, "Data Type"

ORDER BY
 "Attribute Name"
 , "Merchandising Terminal Node ID"