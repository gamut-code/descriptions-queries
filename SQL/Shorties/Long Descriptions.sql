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

SELECT
array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
,  mprod."merchandisingCategoryId" as "Merchandising Terminal Node ID"
, mprod.id as "Merchandising Product ID"
, tprod."gtPartNumber" as "Gamut Part Number"
, tprod."supplierSku" as "Supplier Part Number"
, mprod.description as "Short Description"
, tprod."longDescription" as "Long Description"
, tprod.id as taxId
, mprod."updatedOn" as merchUpdate
, tprod."updatedOn" as taxUpdate
, mprod.visible as webVisible

FROM merchandising_product AS mprod


INNER JOIN merch
    ON merch.id = mprod."merchandisingCategoryId"
    AND (94 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***
inner join taxonomy_product as tprod
	on tprod.id = mprod."taxonomyProductId"
	and tprod.deleted = 'f'

where mprod.deleted = 'f'
--AND tprod.status = 3		--*ONLY PULL ACTIVE SKUS*--

--AND mprod.description ILIKE 'boots%' OR mprod.description ILIKE '% boots%'
--AND tprod."gtPartNumber" IN ('
--AND mprod."merchandisingCategoryId" IN (	--*PULL BY MERCH CATEGORY88--

ORDER BY tprod."gtPartNumber"