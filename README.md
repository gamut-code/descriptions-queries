# descriptions-queries
Python, SAS, and SQL queries for Grainger/Gamut descriptions

Python Queries:
The two main queries are SHORTIES and ATTRIBUTES
SHORTIES pulls short descriptions (Item and SEO) for Grainger by Node or SKU and merges them with Gamut short descriptions,
creating and Excel sheet for each node.
ATTRIBUTES queries Grainger attributes and creates an Excel sheet with all data points on the second sheet. The first 'Stats' sheet
lists unique values/value counts by attribute and presents a fill rate for each attribute.

SAS Queries
Gamut: Open the SHORT_DESC_INPUTS.egp in SAS and run the sequence of files to generate all short descriptions each week. Read in-file
comments on how to run specific nodes.
Grainger: Shorties.egp functionality has been elicpised by the Python funcionality (see above), but you can still use this to pull
Grainger descrpitions along with Gamut SKU numbers. Monthly Sales.egp pulls sales on all Grainger nodes based on a given sales time
(see in-file notes for how to update).

SQL: A collection of queries short and long description (used for Gamut NLG experiment) needs just for the Gamut Postgres database.
