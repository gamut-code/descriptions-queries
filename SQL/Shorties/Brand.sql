select
	"id"
	, "gtPartNumber"
	, "supplierSku"
	, max("brand") as "brand"
	, max("subbrand") as "subbrand"
	, max("series") as "series"
	, max("brandedness") as "brandedness"
	, max("brandconfig") as "brandconfig"
	, max("unbrandconfig") as "unbrandconfig"
from
(
select
	taxonomy_product."supplierSku"
	, taxonomy_product."gtPartNumber"
	, taxonomy_product."id"
	, case 
		when "propertyId" = '1' and "value" <> ' ' then "value"
		end as "brand"
	, case 
		when "propertyId" = '2' and "value" <> ' ' then "value"
		end as "subbrand"
	, case 
		when "propertyId" = '3' and "value" <> ' ' then "value"
		end as "series"
	, case 
		when "propertyId" = '23' and "value" <> ' ' then "value"
		end as "brandedness"
	, case 
		when "propertyId" = '24' and "value" <> ' ' then "value"
		end as "brandconfig"
	, case 
		when "propertyId" = '25' and "value" <> ' ' then "value"
		end as "unbrandconfig"	
from
	taxonomy_product_property_Value
left join
	taxonomy_product
on taxonomy_product_property_Value."productId" = taxonomy_product."id" 
where
	taxonomy_product_property_Value."deleted" = 'f' 
	and taxonomy_product."deleted" = 'f'
	and "propertyId" in ('1','2','3','23','24','25')
) as a

group by 1,2,3