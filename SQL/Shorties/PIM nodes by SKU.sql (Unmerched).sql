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
                
            )
           

SELECT
  tprod."gtPartNumber" as "Gamut Part Number"
  , tprod."supplierSku" as "Grainger Part Number"
  , array_to_string(tax.ancestor_names || tax.name,' > ') as "tax_path"  
  , tprod."categoryId" as "PIM Node ID"
  , tprod."updatedOn" as "PIM Update"

FROM taxonomy_product tprod

INNER JOIN tax
  ON tax.id = tprod."categoryId"
  -- AND (10006 = ANY(tax.ancestors)) --OR 8215 = ANY(tax.ancestors) OR 7739 = ANY(tax.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

WHERE
--  tprod."gtPartNumber" IN ('
--  tax.id IN (