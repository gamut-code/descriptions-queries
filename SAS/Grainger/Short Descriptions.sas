/************************************************************************************/
/*	FILENAME:	Short Descriptions													*/
/*	PURPOSE:	Pull shorties (Grainger - Item and SEO) + Gamut						*/
/*				by SKU, L1, L2, or L3												*/
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

LIBNAME TDLMT ODBC USER=xcxg109 PASSWORD=gr8m!ndset DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_MTRL ;
LIBNAME TDLMT2 ODBC USER=xcxg109 PASSWORD=gr8m!ndset DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_LMT ;

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
        , item.SHORT_DESCRIPTION AS Item_Description
        , item.GIS_SEO_SHORT_DESC_AUTOGEN AS SEO_Description
/*		, mprod.description AS Gamut_Short_Description*/
        , item.PM_CODE
/*        , item.RELATIONSHIP_MANAGER_CODE*/
/*        , item.SALES_STATUS*/
		, supplier.SUPPLIER_NAME
		, brand.BRAND_NAME
		, yellow.PROD_CLASS_ID AS Yellow_ID
		, flat.Web_Parent_Name


FROM TDLMT2.ITEM_V AS item

INNER JOIN TDLMT.CATEGORY_V AS cat
	ON cat.CATEGORY_ID = item.CATEGORY_ID
		AND item.DELETED_FLAG = 'N'
		AND item.PM_CODE NOT IN ('R9')
		AND item.PM_CODE NOT IN ('R4')

LEFT JOIN GAMUT.taxonomy_product tprod
	ON tprod.supplierSku = item.MATERIAL_NO
	AND tprod.deleted = 'f'

/*LEFT JOIN GAMUT.merchandising_product mprod*/
/*    ON mprod.taxonomyProductId = tprod.id*/

INNER JOIN TDLMT2.Prod_Yellow_Heir_Class_View AS yellow
    ON yellow.PRODUCT_ID = item.MATERIAL_NO

INNER JOIN TDLMT2.Yellow_Heir_Flattend_view AS flat
     ON yellow.PROD_CLASS_ID = flat.Heir_End_Class_Code

INNER JOIN TDLMT.BRAND_V AS brand
    ON item.BRAND_NO = brand.BRAND_NO

INNER JOIN TDLMT.SUPPLIER_V AS supplier
	ON supplier.SUPPLIER_NO = item.SUPPLIER_NO


WHERE 	item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
/*	AND item.MATERIAL_NO IN ('*/
/*	AND tprod.gtPartNumber IN ('*/
/*  AND cat.SEGMENT_ID IN (*/
/*	AND cat.FAMILY_ID IN (*/
/*	AND item.GIS_SEO_SHORT_DESC_AUTOGEN NOT LIKE ('%,%')*/
	AND cat.CATEGORY_ID in (4416)


/*	AND yellow.PROD_CLASS_ID IN ('*/
;

QUIT;