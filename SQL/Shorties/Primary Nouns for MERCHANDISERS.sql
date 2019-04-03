--Primary Nouns with all visible and hidden cats and collections. As well as product status.
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

SELECT -- DISTINCT ON (tpn."primaryNoun")
        array_to_string(tax.ancestor_names || tax.name,' > ') as "tax_path"   
        , array_to_string(merch.ancestor_names || merch.name,' > ') as "merch_path"
	, tpn."primaryNoun"
        , merch.id as merch_term_node_id
	, mcat."isTerminal"
        , mcat.visible as merch_term_node_visible
	, coll.id as collection_id
        , coll.name as collection_name
	, coll.visible as coll_visible
	, tprod.id as pim_prod_id
	, tprod."gtPartNumber"
	, tprod."supplierSku"
	, tprod.status

FROM taxonomy_product tprod
	
INNER JOIN tax
	ON tax.id = tprod."categoryId"
INNER JOIN merchandising_product mprod
	ON mprod."taxonomyProductId" = tprod.id
	AND mprod.deleted = 'f'
INNER JOIN  merch
	ON merch.id = mprod."merchandisingCategoryId"
	AND (131 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
INNER JOIN merchandising_category as mcat
	ON mcat.id = mprod."merchandisingCategoryId"
	AND mcat.deleted = 'f'
	--AND mcat.visible = 't'
INNER JOIN merchandising_collection_product mcp
	ON mcp."merchandisingProductId" = mprod.id
INNER JOIN merchandising_collection coll
	ON coll.id = mcp."collectionId"
	AND coll.deleted = 'f'
	--AND coll.visible = 't'
LEFT JOIN taxonomy_product_primary_noun tpn
	ON tpn."supplierSku" = tprod."supplierSku"

WHERE tprod.deleted = 'f'

ORDER BY tpn."primaryNoun"
	, tax_path
	, merch_path