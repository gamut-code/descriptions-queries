/************************************************************************************/
/*	FILENAME:	02 LOOP_ALL															*/
/*	PURPOSE:	CREATE INDIVIDUAL FILES WITH SHORT DESCRIPTION INPUTS FOR EACH		*/
/* 				L1 CATEGORY.  														*/
/*																					*/
/*				PROGRAM FIRST COMBINES ALL QUERY RESULTS INTO ONE DATASET AND 		*/
/*				DEDUPES RECORDS.  THE LOOPS THROUGH ALL L1 CATEGORIES AND EXPORTS	*/
/*				CSV FILE WITH RECORDS FOR THAT CATEGORY.  FILES ARE SAVED TO 		*/
/*				SUBFOLDER OF LIBNAME.												*/
/*				MERCH PRODUCTS AND RANK ORDERS THEM									*/
/************************************************************************************/
/*	AUTHOR:		JACQUELINE RICE														*/
/*	CREATED:	JUNE 2017															*/
/************************************************************************************/

/*	PREPPING QUERY RESULTS FOR FINAL OUTPUT	----------------------------------------*/
/*	COMBINING ALL INDIVIDUAL QUERY RESULTS INTO ONE DATASET	*/
DATA ALL_DATA;
SET		LIB.TABLE_DATA
		LIB.DIFF_DATA
		LIB.PDP_DATA1-LIB.PDP_DATA6;
RUN;

/*	DEDUPING RECORDS AND SORTING BY CATEGORY ID	*/
PROC SORT DATA = ALL_DATA NODUPRECS;
BY MERCH_CAT_ID;
RUN;


/*	CREATING MACRO VARIABLES	----------------------------------------------------*/
/*	INDIVIDUAL MACRO VARS ARE CREATED TO HOUSE CAT ID AND NAME. THESE VARS			*/
/*	ARE USED TO SUBSET DATASET AND TO NAME FINAL OUTPUT FILES.						*/
/* -------------------------------------------------------------------------------- */
PROC SQL;
	/*	FINDING COUNT OF CATEGORIES IN ALL_DATA	*/
	SELECT 	COUNT(DISTINCT MERCH_CAT_ID) INTO :NUM_CAT
	FROM ALL_DATA
	;

	/*	CREATING VARS FOR EACH CAT ID IN ALL_DATA	*/
	SELECT DISTINCT	MERCH_CAT_ID
			INTO :CAT_ID1-:CAT_ID%TRIM(&NUM_CAT)
	FROM ALL_DATA
	ORDER BY MERCH_CAT_ID
	;

	/*	CREATING VARS FOR EACH CAT NAME IN ALL_DATA	*/
	SELECT DISTINCT	MERCH_CAT_NAME
			INTO :CAT_NAME1-:CAT_NAME%TRIM(&NUM_CAT)
	FROM ALL_DATA
	ORDER BY MERCH_CAT_ID
	;
QUIT;

/*PRINTING MACRO VARS FOR VERIFICATION*/
%PUT &CAT_ID1;
%PUT &CAT_NAME1;
%PUT &NUM_CAT;


/*	WRITING MACRO TO LOOP THROUGH CATEGORIES	------------------------------------*/
/*	MACRO LOOPS THROUGH EACH CATEGORY ID IN ORDER.  THE FULL DATASET IS FILTERED	*/
/*	TO SPECIFIC CATEGORY ID, THEN EXPORTED AS A CSV.  THE CSV INCLUDES THE CATEGORY	*/
/*	ID AND NAME IN THE FILENAME.  THESE FIELDS ARE NOT PART OF THE OUTPUT FILE, 	*/
/*	SO THEY ARE DROPPED PRIOR TO EXPORT												*/
/* -------------------------------------------------------------------------------- */
%MACRO DOLOOP_TABLE;
%DO i = 1 %TO &NUM_CAT;

/* SUBSET OF DATA TO EXPORT    */
    DATA SD_TABLE
        (drop = merch_cat_id merch_cat_name);
    SET ALL_DATA
        (WHERE= (MERCH_CAT_ID IN (&&CAT_ID&i)));    
    RUN;

    /* MARCRO VARIABLE SILLINESS TO GET THE FILENAME JUST RIGHT                */
    /* REMOVING SPACES, AMPERSANDS, AND DOUBLE UNDERSCORES FROM FILENAME    */
    %LET FN1 = %SYSFUNC(PATHNAME(LIB))\OUTPUT\SD_INPUT_&&CAT_ID&i.._&&CAT_NAME&i...csv;
    %LET FN2=%sysfunc(TRANWRD(%quote(&FN1),%str(& ),));
    %LET FN3=%sysfunc(TRANWRD(%quote(&FN2),%str(,),));
    %LET FN4=%sysfunc(tranwrd(%quote(&FN3),%str( ),_));
    %LET FN5=%sysfunc(tranwrd(%quote(&FN4),%str(__),%str(_)));
    %LET FILENAME=%sysfunc(tranwrd(%quote(&FN5),%str(__),%str(_)));
    %PUT &FILENAME;

    /*    EXPORTING DATASET AND REPLACING ANY EXISTING FILE WITH SAME NAME    */
    PROC EXPORT REPLACE
        DATA = SD_TABLE
        OUTFILE = "&FILENAME";
        ;
    RUN;
%END;
%MEND;


/*	EXECUTE MACRO TO LOOP THROUGH CATEGORIES	------------------------------------*/
%DOLOOP_TABLE;
