/************************************************************************************/
/*	FILENAME:	00_MACRO															*/
/*	PURPOSE:	DEFINE L1 GAMUT CATEGORIES TO INCLUDE IN PULL.  THE PDP DATAPULL	*/
/*				MUST BE RUN WITH ONLY A FEW CATEGORIES AT ONCE, SO THE CATEGORIES 	*/
/*				ARE SPLIT ACROSS SEVERAL MACRO VARIABLES.							*/
/*																					*/
/*				NOTE THAT AN OPTION EXISTS TO ONLY RUN A FEW CATEGORIES AT ONCE		*/
/************************************************************************************/
/*	AUTHOR:		JACQUELINE RICE														*/
/*	CREATED:	JUNE 2017															*/
/************************************************************************************/


/*	DEFINING LIBRARY TO SAVE QUERY RESULTS -----------------------------------------*/
/*	THIS WILL VARY BY USER															*/
LIBNAME LIB 'F:/LabUsers/CGabriel/Gamut_ShortDesc/';

/* PRINTING/SETTING OPTIONS	--------------------------------------------------------*/
proc options group=memory; run;
proc options option=utilloc; run;
proc options option=threads; run;
options threads fullstimer msglevel=i ;

/*	STANDARD RUN OPTION	------------------------------------------------------------*/
/*	DUE TO THE LARGE VOLUME OF DATA, RUNNING ALL L1S AT ONCE IN THE PDP QUERY IS	*/
/* 	NOT FEASIBLE.  THUS, THE CATEGORIES ARE SPLIT INTO 6 GROUPS.  EACH GROUP IS RUN	*/
/*	SEPARATELY AND THE RESULTS ARE COMBINED IN THE FINAL OUTPUT		 				*/
/*																					*/
/*	THE MERCHWHERE VARIABLE IS A PLACEHOLDER HERE CONTAINING ALL CATEGORIES 		*/
/*	EXCLUDING L1S.  IT IS USED IN THE STANDARD DATAPULL OF TABLE ATTRIBUTES			*/
/*	AND THE QUERY FOR DIFFERENTIATED ATTRIBUTES FOR PRODUCT GROUPS.  IN THE 		*/
/*	ALTERNATIVE OPTION, IT IS USED TO LIST SPECIFIC CATEGORIES ONLY					*/
/*	--------------------------------------------------------------------------------*/

%LET MERCHWHERE  = MERCH.ANCESTORS IS NOT NULL;
%LET MERCHWHERE1 = (
	 4 = any(merch.ancestors)
	OR 37 = any(merch.ancestors)
	OR 42 = any(merch.ancestors)
	OR 185 = any(merch.ancestors)
	OR 476 = any(merch.ancestors)
	);
%LET MERCHWHERE2 = (
	 554 = any(merch.ancestors)
	OR 558 = any(merch.ancestors)
	OR 561 = any(merch.ancestors)
	OR 835 = any(merch.ancestors)
	OR 997 = any(merch.ancestors)
	OR 1725 = any(merch.ancestors)
);

%LET MERCHWHERE3 = (
	 2080 = any(merch.ancestors)
	OR 2214 = any(merch.ancestors)
	OR 2944 = any(merch.ancestors)
	OR 3167 = any(merch.ancestors)
	OR 3452 = any(merch.ancestors)
	OR 3581 = any(merch.ancestors)
);

%LET MERCHWHERE4 = (
	 3702 = any(merch.ancestors)
	OR 3805 = any(merch.ancestors)
	OR 4000 = any(merch.ancestors)
	OR 4238 = any(merch.ancestors)
	OR 4429 = any(merch.ancestors)
	OR 4646 = any(merch.ancestors)
);

%LET MERCHWHERE5 = (
	 4816 = any(merch.ancestors)
	OR 5456 = any(merch.ancestors)
	OR 5461 = any(merch.ancestors)
	OR 5550 = any(merch.ancestors)
	OR 6000 = any(merch.ancestors)
	OR 6693 = any(merch.ancestors)
);

%LET MERCHWHERE6 = (
	 6890 = any(merch.ancestors)
	OR 7301 = any(merch.ancestors)
	OR 448 = any(merch.ancestors)
	OR 6506 = any(merch.ancestors)
	OR 8346 = any(merch.ancestors)
);


/*	ALTERNATIVE RUN OPTION	--------------------------------------------------------*/
/*	IF ONLY WANT TO RUN A FEW CATEGORIES, LIST THEM IN THE "MERCHWHERE" VARIABLE.	*/
/* 	THEN UNCOMMENBT THE MERCHWHERE1-MERCHWHERE6 VARIABLES HERE.  THE CODE WILL		*/
/*	STILL RUN ALL 6 QUERIES, BUT ONLY THE 1ST WILL RETURN RESULTS					*/
/*	--------------------------------------------------------------------------------*/

/*%LET MERCHWHERE =  (*/
/*554 = any(merch.ancestors)*/
/*OR 4429 = any(merch.ancestors)*/
/*OR 3805 = any(merch.ancestors)*/
/*OR 2214 = any(merch.ancestors)*/
/*OR 3581 = any(merch.ancestors)*/
/*OR 5461 = any(merch.ancestors)*/
/*OR 6693 = any(merch.ancestors)*/
/*OR 7301 = any(merch.ancestors)*/
/*);*/
/**/
/*%LET MERCHWHERE1 = &merchwhere;*/
/*%LET MERCHWHERE2 =  (0 = any(merch.ancestors));*/
/*%LET MERCHWHERE3 =  (0 = any(merch.ancestors));*/
/*%LET MERCHWHERE4 =  (0 = any(merch.ancestors));*/
/*%LET MERCHWHERE5 =  (0 = any(merch.ancestors));*/
/*%LET MERCHWHERE6 =  (0 = any(merch.ancestors));*/


/*	PRINTING MACRO VARIABLES TO LOG	--------------------------------------------------*/
%PUT &MERCHWHERE;
%PUT &MERCHWHERE1;
%PUT &MERCHWHERE2;
%PUT &MERCHWHERE3;
%PUT &MERCHWHERE4;
%PUT &MERCHWHERE5;
%PUT &MERCHWHERE6;