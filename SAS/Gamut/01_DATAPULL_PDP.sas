/************************************************************************************/
/*	FILENAME:	01_DATAPULL_PDP														*/
/*	PURPOSE:	QUERIES FROM AZURE PIM ATTRIBUTES ON PDP FOR ALL SNB PRODUCTS AND 	*/
/*				ALL PRODUCTS WITH A PRODUCT CARD TEMPLATE.  ONLY TOP 20 ATTRIBUTES	*/
/*				IN DISPLAY ORDER ARE RETURNED.										*/ 
/*																					*/
/*				THE QUERY ITSELF IS WRITTEN AS A MACRO.  THE MACRO THEN RUNS		*/
/*				6 DIFFERENT TIMES, EACH TIME FOR A DIFFERENT SET OF CATEGORIES.		*/
/*				THIS IS NECESSARY DUE TO THE VOLUME OF DATA AND COMPLEXITY OF 		*/
/*				QUERY.  AZURE WILL NOT RETURN RESULTS IF ALL CATEGORIES ARE RUN		*/
/*				TOGETHER IN ONE QUERY.												*/
/************************************************************************************/
/*	AUTHOR:		JACQUELINE RICE														*/
/*	CREATED:	JUNE 2017															*/
/************************************************************************************/



/*	MACRO DEFINITION OF QUERY TO AZURE	--------------------------------------------*/
/*	MACRO TAKES AS ARGUMENTS:														*/
/*		DS_NAME = NAME OF DATASET TO SAVE RESULTS OF QUERY							*/
/*		WHERE_CRITERIA = LIST OF CATEGORY IDS TO QUERY (DEFINED IN 00_MACRO)		*/
%MACRO PDP_DATAPULL(DS_NAME,WHERE_CRITERIA);
PROC SQL noprint ;
CONNECT TO ODBC (user=readwrite password="mpNj00eYh08gLbjlgItb" DSN=PostgreSQL35W );
CREATE TABLE &DS_NAME AS
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
,  merch2 as(select * from merch where &WHERE_CRITERIA)
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
	, pdpvals.template_style_type
	, pdpvals.collection_id
	, pdpvals.collection_name
	, pdpvals.collection_visibility
	, pdpvals.merch_product_id
	, tprod.id as "PIM_product_id"
	, tprod."gtPartNumber" as gamut_part_number
	, tprod."supplierSku" as supplier_part_number
	, tppn."primaryNoun" as primary_noun
	, brand.brandedness
	, brand.display_brand	
	, pdpvals.attribute_id	
	, pdpvals.attribute_name
	, pdpvals.data_type
	, tattr."multiValue" as multivalue
	, pdpvals.attribute_source 
	, pdpvals.attribute_value
	, pdpvals.unit
	, pdpvals.product_group
	, pdpvals.usage
	, pdpvals.relative_rank
	, '' as stack_label
	, '' as stack_prefix
	, '' as stack_suffix
	, tpsales."displaySellUnitQty" as sell_quantity
	, tpsales."displaySellUom" as sell_uom
 FROM merch2
 INNER JOIN (	
	SELECT
		merch2.id as "node_ID"
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
		, mprod.id as merch_product_id
		, mprod."taxonomyProductId"
		, pdpord.attribute_id	
		, mattr."productPageDisplay" as attribute_name
		, mattr."dataType" as data_type
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
		, mprod."merchandisingProductGroupId" as product_group
		, unit.name as unit
		, pdpord.attr_type as usage
		, pdpord.relative_rank
		, '' as stack_label
		, '' as stack_prefix
		, '' as stack_suffix
		, row_number() OVER(Partition by mcoll.id, mprod.id ORDER BY relative_rank ASC) AS abs_rank
	FROM merch2
	INNER JOIN (
		SELECT
			merch_node_id
			, 'pdp'::text as attr_type
			, attribute_id
			, "sortedVisiblePdpAttributeIds"
			, row_number() OVER(Partition by merch_node_id ORDER BY rattr ASC) AS relative_rank
		FROM	(
			SELECT *, row_number() over() as rattr
			FROM
			    (   SELECT
					cat.id as merch_node_id
					, unnest("sortedVisiblePdpAttributeIds")  as attribute_id
					, "sortedVisiblePdpAttributeIds"
			       FROM merchandising_category cat
			       WHERE cat.deleted = 'f'
			       AND cat.visible = 't'
			      ) y
			) x
		) pdpord
		ON pdpord.merch_node_id = merch2.id
	INNER JOIN merchandising_collection mcoll
		ON mcoll."merchandisingCategoryId" = merch2.id
		AND mcoll.deleted = 'f'
		AND mcoll.visible = 'f'
	LEFT JOIN merchandising_collection_product mcp
		ON mcp."collectionId" = mcoll.id
	INNER JOIN merchandising_product mprod 
		ON mprod.id = mcp."merchandisingProductId"
		AND mprod.deleted = 'f'

	LEFT JOIN merchandising_attribute mattr
		ON mattr.id = pdpord.attribute_id
		AND mattr.deleted = 'f'
	INNER JOIN merchandising_product_value mpv
		ON mpv."merchandisingProductId" = mprod.id
		AND mpv."merchandisingAttributeId" = mattr.id
		AND mpv.deleted = 'f'
		AND mpv.value IS NOT NULL
	LEFT JOIN unit
		ON unit.id = mpv."unitId"
		AND unit.deleted = 'f'
	LEFT JOIN merchandising_category as mcat
		ON merch2.id = mcat.id
		AND mcat.deleted = 'f'

	UNION ALL


	SELECT
		merch2.id as "node_ID"
		, CASE WHEN mcat."templateStyleType" = 1 then 'stacked collections'
		WHEN mcat."templateStyleType" = 2 then 'left rail'
		WHEN mcat."templateStyleType" = 3 then 'top rail'
		WHEN mcat."templateStyleType" = 4 then 'product card'
		ELSE 'blank'
		END AS template_style_type
		, mcoll.id as collection_id
		, mcoll.name as collection_name
		, case when mcoll.visible = 't' then 'show'
			else 'hidden'
			end AS collection_visibility
		, mprod.id as merch_product_id
		, mprod."taxonomyProductId"
		, pdpord.attribute_id	
		, mattr.name as attribute_name
		, mattr."dataType" as data_type
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
		, mprod."merchandisingProductGroupId" as product_group
		, unit.name as unit
		, pdpord.attr_type as usage
		, pdpord.relative_rank
		, '' as stack_label
		, '' as stack_prefix
		, '' as stack_suffix
		, row_number() OVER(Partition by mcoll.id, mprod.id ORDER BY relative_rank ASC) AS abs_rank
	FROM merch2
	INNER JOIN (
		SELECT
			merch_node_id
			, 'pdp'::text as attr_type
			, attribute_id
			, "sortedVisiblePdpAttributeIds"
			, row_number() OVER(Partition by merch_node_id ORDER BY rattr ASC) AS relative_rank
		FROM	(
			SELECT *, row_number() over() as rattr
			FROM
			    (   SELECT
					cat.id as merch_node_id
					, unnest("sortedVisiblePdpAttributeIds")  as attribute_id
					, "sortedVisiblePdpAttributeIds"
			       FROM merchandising_category cat
			       WHERE cat.deleted = 'f'
			       AND cat.visible = 't'
			       AND (cat."templateStyleType" = 4)
			      ) y
			) x
		) pdpord
		ON pdpord.merch_node_id = merch2.id
	INNER JOIN merchandising_collection mcoll
		ON mcoll."merchandisingCategoryId" = merch2.id
		AND mcoll.deleted = 'f'
	LEFT JOIN merchandising_collection_product mcp
		ON mcp."collectionId" = mcoll.id
	INNER JOIN merchandising_product mprod 
		ON mprod.id = mcp."merchandisingProductId"
		AND mprod.deleted = 'f'

	LEFT JOIN merchandising_attribute mattr
		ON mattr.id = pdpord.attribute_id
		AND mattr.deleted = 'f'
	INNER JOIN merchandising_product_value mpv
		ON mpv."merchandisingProductId" = mprod.id
		AND mpv."merchandisingAttributeId" = mattr.id
		AND mpv.deleted = 'f'
		AND mpv.value IS NOT NULL
	LEFT JOIN unit
		ON unit.id = mpv."unitId"
		AND unit.deleted = 'f'
	LEFT JOIN merchandising_category as mcat
		ON merch2.id = mcat.id
		AND mcat.deleted = 'f'

	) pdpvals
	ON pdpvals."node_ID" = merch2.id
	AND  abs_rank < 21
	AND (pdpvals.collection_visibility = 'hidden' OR pdpvals.template_style_type in ( 'product card', 'blank'))


LEFT JOIN taxonomy_product tprod
	ON tprod.id = pdpvals."taxonomyProductId"
	AND tprod.deleted = 'f'

LEFT JOIN taxonomy_category as tcat
	ON tprod."categoryId" = tcat.id
LEFT JOIN merchandising_attribute__taxonomy_attribute mata
	ON pdpvals.attribute_id = mata."merchandisingAttributeId"
	AND mata."taxonomyCategoryId" = tcat.id
	AND mata.deleted = 'f'
LEFT JOIN taxonomy_attribute tattr
	ON tattr.id = mata."attributeId"
	AND tattr.deleted = 'f'
LEFT JOIN merchandising_category as mcat
	ON merch2.id = mcat.id
	AND mcat.deleted = 'f'
LEFT JOIN taxonomy_product_primary_noun as tppn
	ON tppn."supplierSku" = tprod."supplierSku"
LEFT JOIN taxonomy_product_sales_data as tpsales
	ON tpsales."taxonomyProductId" = tprod.id
	AND tpsales.deleted = 'f'
LEFT JOIN brand
	ON brand.pim_prod_id = tprod.id


	);
DISCONNECT FROM ODBC ;
QUIT ;

%MEND;


/*	EXECUTING QUERY FOR EACH SET OF CATEGORY IDS	--------------------------------*/
%PDP_DATAPULL(LIB.PDP_DATA1,&MERCHWHERE1);
%PDP_DATAPULL(LIB.PDP_DATA2,&MERCHWHERE2);
%PDP_DATAPULL(LIB.PDP_DATA3,&MERCHWHERE3);
%PDP_DATAPULL(LIB.PDP_DATA4,&MERCHWHERE4);
%PDP_DATAPULL(LIB.PDP_DATA5,&MERCHWHERE5);
%PDP_DATAPULL(LIB.PDP_DATA6,&MERCHWHERE6);