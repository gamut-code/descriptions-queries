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
            ),
	
	merch AS (
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
	  array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Position"
        , tprod."gtPartNumber" AS "GT Part #"
	, tprod."supplierSku" AS "Supplier Part #"
	, noun."primaryNoun" AS "Primary Noun"


FROM taxonomy_product tprod
INNER JOIN tax
    ON tax.id = tprod."categoryId"
    AND tprod.deleted = 'f'

INNER JOIN merchandising_product mprod
  ON tprod.id = mprod."taxonomyProductId"
    
INNER JOIN  merch
    ON merch.id = mprod."merchandisingCategoryId"
 --   AND (228 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

LEFT JOIN taxonomy_product_primary_noun noun
    ON noun."supplierSku" = tprod."supplierSku"


INNER JOIN merchandising_category mcat
  ON mcat.id = mprod."merchandisingCategoryId"


WHERE tprod.deleted = 'f'
--  AND tprod."gtPartNumber" IN ('
--  AND mcat.id IN (
--  AND LOWER(noun."primaryNoun") LIKE LOWER('% For %')
--  AND mprod."merchandisingCategoryId" IN (435)