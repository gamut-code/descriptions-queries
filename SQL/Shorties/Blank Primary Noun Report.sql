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
	  array_to_string(tax.ancestor_names || tax.name,' > ') as "PIM Position"
        , tprod."gtPartNumber" AS "GT Part #"
	, tprod."supplierSku" AS "Supplier Part #"
	, noun."primaryNoun" AS "Primary Noun"


FROM taxonomy_product tprod
INNER JOIN tax
    ON tax.id = tprod."categoryId"
    AND tprod.deleted = 'f'

LEFT JOIN taxonomy_product_primary_noun noun
    ON noun."supplierSku" = tprod."supplierSku"


WHERE noun."primaryNoun" IS NULL
