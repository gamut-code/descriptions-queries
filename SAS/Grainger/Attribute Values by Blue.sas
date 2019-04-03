/************************************************************************************/
/*	FILENAME:	Attribute Values by Blue											*/
/*	PURPOSE:	Pull all attributes by SKU, L1, L2, or L3 (set in WHERE statement) 	*/
/*		This file exports "Attriubtes", which includes all values for all SKUs  	*/
/*      The Attr OUT file creates "Attributes_NO_DUP", which includes distinct		*/
/*			values for each attribute for each included L3 category					*/ 
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


PROC SQL noprint;

LIBNAME TDLMT ODBC USER=xcxg109 PASSWORD=gr8m!ndset DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_MTRL ;
LIBNAME TDLMT2 ODBC USER=xcxg109 PASSWORD=gr8m!ndset DSN=TeradataLDAP SCHEMA=PRD_DWH_VIEW_LMT ;

CREATE TABLE LIB.ATTR AS 
   	SELECT	
		cat.SEGMENT_NAME AS L1
        , cat.FAMILY_NAME AS L2
        , cat.CATEGORY_NAME
		, cat.CATEGORY_ID AS L3
        , item.MATERIAL_NO AS Grainger_SKU
 		, item.MFR_MODEL_NO AS Mfr_Part_No
        , attr.DESCRIPTOR_NAME AS Attribute
		, item_attr.ITEM_DESC_VALUE AS Attribute_Value
		, item.PM_CODE AS PM_Code
		, supplier.SUPPLIER_NAME
		, brand.BRAND_NAME
		, yellow.PROD_CLASS_ID AS Yellow_ID


FROM TDLMT.ITEM_DESC_V AS item_attr

INNER JOIN TDLMT2.ITEM_V AS item
	ON 	item_attr.MATERIAL_NO = item.MATERIAL_NO
	AND item_attr.DELETED_FLAG = 'N'
 	AND item_attr.LANG = 'EN'
	AND item.PRODUCT_APPROVED_US_FLAG = 'Y'

INNER JOIN TDLMT.CATEGORY_V AS cat
	ON cat.CATEGORY_ID = item_attr.CATEGORY_ID
		AND item_attr.DELETED_FLAG = 'N'
		AND item.PM_CODE NOT IN ('R9')

INNER JOIN TDLMT.MAT_DESCRIPTOR_V AS attr
	ON attr.DESCRIPTOR_ID = item_attr.DESCRIPTOR_ID
	AND attr.DELETED_FLAG = 'N'

INNER JOIN TDLMT2.Prod_Yellow_Heir_Class_View AS yellow
    ON yellow.PRODUCT_ID = item.MATERIAL_NO

INNER JOIN TDLMT.BRAND_V AS brand
    ON item.BRAND_NO = brand.BRAND_NO

INNER JOIN TDLMT.SUPPLIER_V AS supplier
	ON supplier.SUPPLIER_NO = item.SUPPLIER_NO

WHERE item.SALES_STATUS NOT IN ('DG', 'DV', 'WV', 'WG')
/*	AND item.MATERIAL_NO IN ('*/
/*	AND cat.SEGMENT_ID IN (*/
/*	AND cat.FAMILY_ID IN (*/
/*	AND cat.category_id IN (*/
/*	AND LOWER(attr.DESCRIPTOR_NAME) LIKE LOWER('%
/*  AND yellow.PROD_CLASS_ID IN ('*/
/*  AND LOWER(supplier.SUPPLIER_NAME) LIKE LOWER('%*/
/*  AND LOWER(brand.BRAND_NAME) LIK LOWER9'%*/

;

PROC EXPORT DATA=LIB.ATTR OUTFILE="F:/LabUsers/CGabriel/Grainger_Shorties/OUTPUT/attributes"
	DBMS=XLSX REPLACE;