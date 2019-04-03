/************************************************************************************/
/*	FILENAME:	01_DATAPULL_TABLE													*/
/*	PURPOSE:	QUERIES FROM AZURE PIM FILTER AND TABLE ATTRIBUTES FOR BROWSABLE 	*/
/*				MERCH PRODUCTS AND RANK ORDERS THEM									*/
/************************************************************************************/
/*	AUTHOR:		JACQUELINE RICE														*/
/*	CREATED:	JUNE 2017															*/
/************************************************************************************/

/*	QUERING AZURE VIA PASSTHROUGH	------------------------------------------------*/
/*	RESULTS SAVED TO LIBRARY DEFINED IN 00_MACRO (LIB.)								*/
PROC SQL ;
CONNECT TO ODBC (user=readwrite password="mpNj00eYh08gLbjlgItb" DSN=PostgreSQL35W );
CREATE TABLE LIB.TABLE_DATA AS
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
, _tmp_attrs AS (
/*			--stack pivots*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'stack' as attr_type
		, collord.attribute_id
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, json_extract_path_text(json_array_elements(json_extract_path(json_array_elements("stacksConfiguration"), 'groupSelections')),'merchandisingAttributeId')::integer as attribute_id	
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f'	AND coll.visible = 't'
		       ) y
		) collord	
	UNION
/*	--Table attributes*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'table' as attr_type
		, collord.attribute_id
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, json_extract_path_text(json_array_elements("orderedVisibleMerchandisingAttributes"), 'merchandisingAttributeId')::integer  as attribute_id
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f' 	AND coll.visible = 't'
		       ) y
		) collord
	UNION
/*	--Column groups*/
	SELECT
		collord.node_id
		, collord.collection_id
		, collord.collection_name
		, collord.collection_visible
		, 'column group' as attr_type
		, collord.attribute_id
		, row_number() OVER(Partition by collection_id ORDER BY rm ASC) AS relative_rank
	FROM	( 
		SELECT *,row_number() over() as rm
		       FROM (
		       SELECT
				coll."merchandisingCategoryId" as node_id
				, coll.id as collection_id
				, coll.name as collection_name
				, coll.visible as collection_visible
				, (json_extract_path(json_array_elements("columnGroupsConfiguration"), 'merchandisingAttributeId')::text)::integer as attribute_id	
				, row_number() over() as coll_order
		       FROM merchandising_collection coll
		       WHERE coll.deleted = 'f'	AND coll.visible = 't'
		       ) y
		) collord
	UNION
/*	-- filters*/
	SELECT 
		z.node_id
		, coll.id  as collection_id
		, coll.name as collection_name
		, coll.visible as collection_visible
		, attr_type
		, attribute_id
		, relative_rank
	FROM (
		SELECT
			
			 node_id
			, 'filter'::text as attr_type
			, attribute_id
			, row_number() OVER(Partition by node_id ORDER BY rattr ASC) AS relative_rank
		FROM	(
			SELECT *, row_number() over() as rattr
			FROM
			    (  
			     SELECT
					cat.id as node_id
					, unnest("sortedFiltersKeys")::integer  as attribute_id
					, "sortedFiltersKeys"
			       FROM merchandising_category cat
			       WHERE cat.deleted = 'f' AND cat.visible = 't'
			      ) y		      
			) x			
		)z 
	LEFT JOIN merchandising_collection coll
		ON coll."merchandisingCategoryId" = z.node_id AND coll.visible = 't'
	WHERE relative_rank = 1
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
	, _tmp_attrs.collection_id
	, _tmp_attrs.collection_name
	, case when _tmp_attrs.collection_visible = 't' then 'show'
		else 'hidden'
		end AS collection_visibility
	, mcp."merchandisingProductId" as merch_product_id
	, tprod.id as PIM_product_id
	, tprod."gtPartNumber" as gamut_part_number
	, tprod."supplierSku" as supplier_part_number
	, tppn."primaryNoun" as primary_noun
	, brand.brandedness
	, brand.display_brand
	, _tmp_attrs.attribute_id
	, CASE _tmp_attrs.attr_type 
		WHEN 'stack' THEN mattr."collectionStacksDisplay"
		WHEN 'filter' THEN mattr."filterDisplay"
		WHEN 'table' THEN mattr."collectionHeaderDisplay"
		WHEN 'column group' THEN mattr."collectionStacksDisplay"
		END AS attribute_name
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
	, NULL::integer as product_group
	, _tmp_attrs.attr_type as usage
	, _tmp_attrs.relative_rank
	, '' as stack_label
	, '' as stack_prefix
	, '' as stack_suffix
	, tpsales."displaySellUnitQty" as sell_quantity
	, tpsales."displaySellUom" as sell_uom
FROM  merch2
INNER JOIN merchandising_category as mcat
	ON merch2.id = mcat.id
	AND mcat.deleted = 'f'
	AND mcat.visible = 't'
	
INNER JOIN merchandising_product mprod 
	ON mprod."merchandisingCategoryId" = mcat.id
	AND mprod.deleted = 'f'
	AND mprod.visible = 't'
LEFT JOIN taxonomy_product tprod
	ON tprod.id = mprod."taxonomyProductId"
	AND tprod.deleted = 'f'
LEFT JOIN taxonomy_category as tcat
	ON tprod."categoryId" = tcat.id
	AND tcat.deleted = 'f'
LEFT JOIN taxonomy_product_primary_noun as tppn
	ON tppn."supplierSku" = tprod."supplierSku"
LEFT JOIN taxonomy_product_property_value as brandedness
	ON brandedness."productId" = tprod.id
	AND brandedness."propertyId" = 23
	and brandedness.deleted = 'f'
LEFT JOIN brand
	ON brand.pim_prod_id = tprod.id
LEFT JOIN taxonomy_product_sales_data as tpsales
	ON tpsales."taxonomyProductId" = tprod.id
	AND tpsales.deleted = 'f'
	
INNER JOIN merchandising_collection_product mcp
	ON mcp."merchandisingProductId" = mprod.id	
INNER JOIN _tmp_attrs
	ON _tmp_attrs.collection_id = mcp."collectionId"

LEFT JOIN merchandising_attribute mattr
	ON mattr.id = _tmp_attrs.attribute_id
	AND mattr.deleted = 'f'
LEFT JOIN merchandising_attribute__taxonomy_attribute mata
	ON mattr.id = mata."merchandisingAttributeId"
	AND mata."taxonomyCategoryId" = tcat.id
	AND mata.deleted = 'f'
LEFT JOIN taxonomy_attribute tattr
	ON tattr.id = mata."attributeId"
	AND tattr.deleted = 'f'


INNER JOIN merchandising_product_value mpv
	ON mpv."merchandisingProductId" = mcp."merchandisingProductId"
	AND mpv."merchandisingAttributeId" = _tmp_attrs.attribute_id
	AND mpv.deleted = 'f'
	AND mpv.value IS NOT NULL
LEFT JOIN unit
	ON unit.id = mpv."unitId"
	AND unit.deleted = 'f'

ORDER BY
	merch_term_node_path
	, collection_name
	, gamut_part_number
	, merch_product_id
	, usage
	, relative_rank

	);
DISCONNECT FROM ODBC ;
QUIT ;

