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

select 
array_to_string(merch.ancestor_names || merch.name,' > ') as "Merchandising Terminal Node Path"
, mprod."merchandisingCategoryId" as "Merchandising Terminal Node ID"
, group_nd.id as "Merchandising Product Group"
, mprod.id as "Merchandising Product ID"
, tprod."gtPartNumber" as "Gamut Part Number"
, tprod."supplierSku" as "Supplier Part Number"
, mprod.description as "Short Description"
, tprod.id as taxId
, mprod."updatedOn" as merchUpdate
, tprod."updatedOn" as taxUpdate
, mprod.visible as webVisible
, tprod.status

from merchandising_product as mprod
inner join

(
select id, "merchandisingCategoryId" from merchandising_product where deleted = 'f' and "isGroup" = 't' and description IS NULL 
)group_nd

on group_nd.id = mprod."merchandisingProductGroupId"

inner join merch
	on merch.id = mprod."merchandisingCategoryId"

inner join taxonomy_product as tprod
	on tprod.id = mprod."taxonomyProductId"
	and tprod.deleted = 'f'

where mprod.deleted = 'f'
AND tprod.status = 3

--order by group_nd.id
