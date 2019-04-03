/* Remove duplicates and keep only one sample value for each attribute value within EACH L3*/

PROC SUMMARY DATA=LIB.ATTR
		NWAY;
  CLASS L3
		Attribute
		Attribute_Value;

  ID 	L1
        L2
        Category_name
		L3
		Grainger_SKU
        Attribute
		Attribute_Value
		PM_Code
		Yellow_ID
		;

  OUTPUT OUT=Attributes_No_Dups (DROP=_type_);

RUN;

DATA Attributes_No_Dups;
	RETAIN Grainger_SKU
		L1
        L2
        L3
        Category_name
        Attribute
		Attribute_Value
		PM_Code
		Yellow_ID;
	SET Attributes_No_Dups;

RUN;

PROC EXPORT DATA=Attributes_No_Dups OUTFILE="F:/LabUsers/CGabriel/Grainger_Shorties/OUTPUT/attributes_NO_DUP"
	DBMS=XLSX REPLACE;