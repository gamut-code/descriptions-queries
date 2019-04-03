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

SELECT DISTINCT ON (tax_att.name, tprodvalue.value)
  array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Terminal Node Path"
  , tprod."categoryId" AS "PIM Terminal Node ID"
  , tprod."gtPartNumber" as "Gamut Part Number"
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
  
LEFT JOIN  taxonomy_product_attribute_value tprodvalue
  ON tprod.id = tprodvalue."productId"

LEFT JOIN taxonomy_attribute tax_att
  ON tax_att.id = tprodvalue."attributeId"

WHERE tprod.deleted = 'f'
--AND tprod."categoryId" IN (4544)
--AND tprod."gtPartNumber" IN ('
--AND LOWER(tprodvalue.value) LIKE LOWER('%rpm%')
--AND LOWER(tprodvalue.unit) LIKE LOWER ('%rpm%')
--AND LOWER(tax_att.name) LIKE LOWER('%Run%')
--AND tax_chatt.id IN (
--AND tprod."merchandisingCategoryId" IN (7337)

ORDER BY tax_att.name
       , tprodvalue.value
       , tprod."categoryId" 