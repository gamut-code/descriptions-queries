/************************************************************************************/
/*	FILENAME:	Short Descriptions													*/
/*	PURPOSE:	Pull shorties (Item and SEO) by SKU, L1, L2, or L3					*/
/*				 																	*/
/************************************************************************************/
/*	AUTHOR:		Colette Gabriel														*/
/*	CREATED:	October 2018														*/
/************************************************************************************/
LIBNAME LIB 'F:/LabUsers/CGabriel/Grainger_Shorties/';

/* PRINTING/SETTING OPTIONS	--------------------------------------------------------*/
proc options group=memory; run;
proc options option=utilloc; run;
proc options option=threads; run;
options threads fullstimer msglevel=i ;



PROC SQL;

LIBNAME TDLMT ODBC USER=xcxg109 PASSWORD=N3wlife! DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_MTRL ;
LIBNAME TDLMT2 ODBC USER=xcxg109 PASSWORD=N3wlife! DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_LMT ;

LIBNAME GAMUT ODBC user=readwrite password=mpNj00eYh08gLbjlgItb DSN=PostgreSQL35W ;

CREATE TABLE LIB.SHORTIES AS
   SELECT item.MATERIAL_NO AS Grainger_SKU
   		, tprod.gtPartNumber AS Gamut_SKU
        , cat.SEGMENT_NAME AS L1
/*		, cat.SEGMENT_ID*/
        , cat.FAMILY_NAME AS L2
/*		, cat.FAMILY_ID*/
        , cat.CATEGORY_ID AS L3
        , cat.CATEGORY_NAME
		, item.BRAND_NO
		, brand.BRAND_NAME
		, brand.Private_Label
		, BRAND_ALIAS
/*        , item.PM_CODE*/
/*        , item.RELATIONSHIP_MANAGER_CODE*/
/*        , item.SALES_STATUS*/
		, yellow.PROD_CLASS_ID AS Yellow_ID


FROM TDLMT2.ITEM_V AS item

INNER JOIN TDLMT.CATEGORY_V AS cat
	ON cat.CATEGORY_ID = item.CATEGORY_ID
		AND item.DELETED_FLAG = 'N'
		AND item.PM_CODE NOT IN ('R9')

LEFT JOIN GAMUT.taxonomy_product tprod
	ON tprod.supplierSku = item.MATERIAL_NO
	AND tprod.deleted = 'f'

LEFT JOIN GAMUT.merchandising_product mprod
    ON mprod.taxonomyProductId = tprod.id
	AND tprod.deleted = 'f'

INNER JOIN TDLMT2.Prod_Yellow_Heir_Class_View AS yellow
    ON yellow.PRODUCT_ID = item.MATERIAL_NO

INNER JOIN TDLMT.BRAND_V AS brand
    ON item.BRAND_NO = brand.BRAND_NO

WHERE 	item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
/*	AND item.MATERIAL_NO IN ('*/
/*	AND tprod.gtPartNumber IN ('*/
  AND cat.SEGMENT_ID IN (1016)
/*	AND cat.FAMILY_ID IN (*/
/*	AND cat.CATEGORY_ID in (*/
/*	AND yellow.PROD_CLASS_ID IN ('*/
	AND LOWER(brand.BRAND_NAME) LIKE LOWER('%Hubbell%')
;

QUIT;