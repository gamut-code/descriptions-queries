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
, group_nd.id as "Merchandising Group ID"
, mprod.id as "Merchandising Product ID"
, tprod."gtPartNumber" as "Gamut Part Number"
, tprod."supplierSku" as "Supplier Part Number"
, mprod.description as "Short Description"
, mcoll.name as "Collection Name"

from merchandising_product as mprod
inner join

(
select id, "merchandisingCategoryId" from merchandising_product where deleted = 'f' and "isGroup" = 't' -- and description IS NULL 
)group_nd

on group_nd.id = mprod."merchandisingProductGroupId"

inner join merch
	on merch.id = mprod."merchandisingCategoryId"
--	AND (7334 = ANY(merch.ancestors)) --OR 8215 = ANY(merch.ancestors) OR 7739 = ANY(merch.ancestors))  -- *** ADD TOP LEVEL NODES HERE ***

inner join taxonomy_product as tprod
	on tprod.id = mprod."taxonomyProductId"
	and tprod.deleted = 'f'
	and tprod.status NOT IN (5)   --eliminate inactive product groups from reporting

INNER JOIN merchandising_collection_product mcollprod
  ON mprod.id = mcollprod."merchandisingProductId"

INNER JOIN merchandising_collection as mcoll
  ON mcoll.id = mcollprod."collectionId"
  
where mprod.deleted = 'f'
--AND mprod."merchandisingCategoryId" IN (
--AND tprod."gtPartNumber" IN ('
--AND tprod."categoryId" IN (
--AND tprod."supplierSku" IN ('

order by group_nd.id
