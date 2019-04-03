/************************************************************************************/
/*	FILENAME:	01_DATAPULL_DIFFATTR												*/
/*	PURPOSE:	QUERIES FROM AZURE PIM THE DIFFERENTIATING ATTRIBUTES FOR 			*/
/*				PRODUCTS IN PRODUCT GROUPS											*/
/************************************************************************************/
/*	AUTHOR:		JACQUELINE RICE														*/
/*	CREATED:	JUNE 2017															*/
/************************************************************************************/

/*	QUERING AZURE VIA PASSTHROUGH	------------------------------------------------*/
/*	RESULTS SAVED TO LIBRARY DEFINED IN 00_MACRO (LIB.)								*/

PROC SQL noprint ;
CONNECT TO ODBC (user=readwrite password="mpNj00eYh08gLbjlgItb" DSN=PostgreSQL35W );
CREATE TABLE LIB.DIFF_DATA AS
/*CREATE TABLE LIB.PDP_DIFF_DATA10 AS*/
	SELECT  *
	FROM CONNECTION TO ODBC 	(

WITH RECURSIVE merch AS (

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
,  merch2 as(select * from merch where &MERCHWHERE)
, brand AS (
		SELECT
			pim_prod_id
			, brandedness
			, CASE WHEN brandedness in (1,2,3) THEN
				CASE brand_config 
					WHEN 1 THEN brand
					WHEN 2 THEN subbrand
					WHEN 3 THEN brand || ' ' || COALESCE(subbrand,'')
					WHEN 4 THEN brand || ' ' || COALESCE(subbrand,'')|| ' ' || COALESCE(series,'')
					WHEN 5 THEN brand || ' ' || COALESCE(series,'')
					WHEN 6 THEN COALESCE(subbrand,'') || ' ' || COALESCE(series,'')
					WHEN 7 THEN brand || ' ' || COALESCE(series,'') || ' ' || COALESCE(subbrand,'') 
					END 

				WHEN brandedness in (4,5,6) THEN
				CASE unbrand_config 
					WHEN 1 THEN 'Gamut Standard'
					WHEN 2 THEN 'Gamut Premium'
					WHEN 3 THEN 'Gamut Value'
					END 

				END AS display_brand
		FROM	(
			SELECT 
				pim_prod_id
				, tppvbrand.value::integer as brandedness
				, brcon.value::integer as brand_config
				, unbrcon.value::integer as unbrand_config
				, max(brand) as brand
				, max(subbrand) as subbrand
				, max(series) as series
				, max(mfr_part_nbr) as mfr_part_nbr
			FROM	(
				SELECT
					tprod.id as pim_prod_id			
					, tppv."propertyId" as brand_type
					, tppv.value as brand_value
					, CASE WHEN tppv."propertyId" = 1 THEN
						tppv.value END as brand
					, CASE WHEN tppv."propertyId" = 2 THEN
						tppv.value END as subbrand
					, CASE WHEN tppv."propertyId" = 3 THEN
						tppv.value END as series
					, CASE WHEN tppv."propertyId" = 4 THEN
						tppv.value END as mfr_part_nbr
				FROM taxonomy_product tprod
				LEFT JOIN taxonomy_product_property_value tppv
					ON tppv."productId" = tprod.id
					AND tppv.deleted = 'f'
					AND tppv."propertyId" BETWEEN 1 AND 4
				WHERE tprod.deleted = 'f'
				)  inner_brand
			INNER JOIN taxonomy_product_property_value tppvbrand
				on tppvbrand."productId" = inner_brand.pim_prod_id
				AND tppvbrand.deleted = 'f' AND tppvbrand."propertyId" = 23		
			LEFT JOIN taxonomy_product_property_value brcon
				on brcon."productId" = inner_brand.pim_prod_id
				AND brcon.deleted = 'f' AND brcon."propertyId" = 24
			LEFT JOIN taxonomy_product_property_value unbrcon
				on unbrcon."productId" = inner_brand.pim_prod_id
				AND unbrcon.deleted = 'f' AND unbrcon."propertyId" = 25		
			GROUP BY
				pim_prod_id
				, tppvbrand.value
				, brcon.value
				, unbrcon.value
			) outer_brand
			)

SELECT
	array_to_string(merch2.ancestor_names || merch2.name,' > ') as "merch_term_node_path"
	, merch2.ancestors[1] as merch_cat_id
	, merch2.ancestor_names[1] as merch_cat_name
	, merch2.id as "node_ID"
	, tprod."categoryId" as "PIM_source_ID"
	, CASE WHEN mcat."templateStyleType" = 1 then 'stacked collections'
		WHEN mcat."templateStyleType" = 2 then 'left rail'
		WHEN mcat."templateStyleType" = 3 then 'top rail'
		WHEN mcat."templateStyleType" = 4 then 'product card'
		WHEN mcat."templateStyleType" IS NULL then 'left rail'
		END AS template_style_type
	, mcoll.id as collection_id
	, mcoll.name as collection_name
	, case when mcoll.visible = 't' then 'show'
		else 'hidden'
		end AS collection_visibility
	, prodgroup.merch_prod_id as merch_product_id
	, tprod.id as "PIM_product_id"
	, tprod."gtPartNumber" as gamut_part_number
	, tprod."supplierSku" as supplier_part_number
	, tppn."primaryNoun" as primary_noun
	, brand.brandedness
	, brand.display_brand	
	, prodgroup.attr_id as attribute_id
	, mattr."productPageDisplay" as attribute_name
	, mattr."dataType" as data_type
	, tattr."multiValue" as multivalue
	, CASE mattr."attributeType" 
		WHEN 0 THEN 'PIM'
		WHEN 1 THEN 'Broad'
		WHEN 2 THEN 'Elevated'
		WHEN 3 THEN 'Brand'
		WHEN 4 THEN 'Compliance'
		WHEN 5 THEN 'Sales'
		END as attribute_source 
	,  CASE WHEN mattr."numericDisplayType" = 'fraction' THEN
		CASE WHEN mpv.denominator = 1 THEN mpv.value 
			ELSE CASE WHEN mpv.numerator < mpv.denominator THEN
				mpv.numerator % mpv.denominator || '/' || mpv.denominator
				ELSE floor(mpv.numerator / mpv.denominator) || ' ' || mpv.numerator % mpv.denominator || '/' || mpv.denominator
				END
			END
		ELSE mpv.value
		END AS attribute_value
	, unit.name as unit
	, prodgroup.product_group
	, prodgroup.attr_type as usage
	, prodgroup.relative_rank
	, '' as stack_label
	, '' as stack_prefix
	, '' as stack_suffix
	, tpsales."displaySellUnitQty" as sell_quantity
	, tpsales."displaySellUom" as sell_uom

FROM merch2
INNER JOIN ( 
	SELECT
		mprod."merchandisingCategoryId" as merch_node_id
		, mprod.id as merch_prod_id
		, mprod."merchandisingProductGroupId" as product_group
		, 'differing'::text as attr_type	
		, dattr."merchandisingAttributeId"  as attr_id	
		, row_number() OVER(Partition by mprod."merchandisingCategoryId", mprod.id, dattr."merchandisingProductGroupId" ORDER BY dattr."merchandisingAttributeId" ASC) AS relative_rank
	FROM merchandising_product mprod
	INNER JOIN merchandising_product_group_differing_attribute dattr
		ON dattr."merchandisingProductGroupId" = mprod."merchandisingProductGroupId"
		AND dattr.deleted = 'f'
	WHERE	mprod.deleted = 'f'		
	) prodgroup
	ON prodgroup.merch_node_id = merch2.id
INNER JOIN merchandising_category mcat	
	ON mcat.id = merch2.id
	AND mcat.visible = 't'
INNER JOIN merchandising_product mprod 
	ON mprod.id = prodgroup.merch_prod_id
	AND mprod.deleted = 'f'
LEFT JOIN taxonomy_product tprod
	ON tprod.id = mprod."taxonomyProductId"
	and tprod.deleted = 'f'

LEFT JOIN taxonomy_product_sales_data as tpsales
	ON tpsales."taxonomyProductId" = tprod.id
	AND tpsales.deleted = 'f'
LEFT JOIN taxonomy_product_primary_noun as tppn
	ON tppn."supplierSku" = tprod."supplierSku"
LEFT JOIN brand
	ON brand.pim_prod_id = tprod.id

LEFT JOIN merchandising_attribute mattr
	ON mattr.id = prodgroup.attr_id
	AND mattr.deleted = 'f'
LEFT JOIN merchandising_attribute__taxonomy_attribute mata
	ON mattr.id = mata."merchandisingAttributeId"
	AND mata."taxonomyCategoryId" = tprod."categoryId"
	AND mata.deleted = 'f'
LEFT JOIN taxonomy_attribute tattr
	ON tattr.id = mata."attributeId"
	AND tattr.deleted = 'f'

INNER JOIN merchandising_collection_product mcp
	ON mcp."merchandisingProductId" = prodgroup.merch_prod_id
INNER JOIN merchandising_collection mcoll
	ON mcoll.id = mcp."collectionId"
	AND mcoll.deleted = 'f'
	AND mcoll.visible = 't'
LEFT JOIN merchandising_product_value mpv
	ON mpv."merchandisingProductId" = prodgroup.merch_prod_id
	AND mpv."merchandisingAttributeId" = prodgroup.attr_id
	AND mpv.deleted = 'f'
LEFT JOIN unit
	ON unit.id = mpv."unitId"
	AND unit.deleted = 'f'

	);
DISCONNECT FROM ODBC ;
QUIT ;

