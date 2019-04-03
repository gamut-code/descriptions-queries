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
                    tax.ancestors || category."parentId",
                    tax.ancestor_names || parent_category.name
                FROM    taxonomy_category as category
                    JOIN tax on category."parentId" = tax.id
                    JOIN taxonomy_category parent_category on category."parentId" = parent_category.id
                WHERE   category.deleted = false
                
            ),
           
 merch AS (
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

           

SELECT
  tprod."gtPartNumber" as "Gamut Part Number"
  , tprod."supplierSku" as "Grainger Part Number"
  , array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
  , array_to_string(tax.ancestor_names || tax.name,' > ') as "tax_path"  
  , mprod."merchandisingCategoryId" AS "Merchandising Terminal Node ID"
  , tprod."categoryId" as "PIM Node ID"
  , mcoll.name as "Collection Name"
  , tprod."updatedOn" as "PIM Update"
  , mprod."updatedOn" as "Merch Update"

FROM taxonomy_product tprod

INNER JOIN tax
  ON tax.id = tprod."categoryId"
  -- AND (10006 = ANY(tax.ancestors)) --OR 8215 = ANY(tax.ancestors) OR 7739 = ANY(tax.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
	
LEFT JOIN  merchandising_product mprod
  ON tprod.id = mprod."taxonomyProductId"
  AND mprod.deleted = 'f'

INNER JOIN merch
  ON merch.id = mprod."merchandisingCategoryId"
  --AND (8575 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
  
INNER JOIN merchandising_category mcat
  ON mcat.id = mprod."merchandisingCategoryId"
  
INNER JOIN merchandising_collection_product mcollprod
  ON mcollprod."merchandisingProductId" = mprod.id
  
INNER JOIN merchandising_collection mcoll
  ON mcoll.id = mcollprod."collectionId"

WHERE tprod.deleted = 'f'
-- AND tprod."gtPartNumber" IN ('
-- AND mprod."merchandisingCategoryId" IN (
-- AND tax.id IN (

ORDER BY
  mprod."merchandisingCategoryId"
  , mcoll.name