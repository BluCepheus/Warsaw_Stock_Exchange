# Warsaw_Stock_Exchange

Benjamin Graham, the author of *The Intelligent Investor* and the proponent of value investing, taught that the returns an investor could expect were not proportional to the risk he was willing to assume, but rather, to the effort he was willing to put into his investments. This idea guided me while investing in the stock market and mobilized me to look for a strategy that would be stripped of the emotions that torment the stock market, and would be a set of clear rules pointing to companies worthy of interest.

The purpose of this repo is to gather all possible information about Warsaw Stock Exchange companies and assess whether it is possible to find financial and economic indices, which influence increase in share prices of each company.

This repo would contain three major features:

1. Web scrapping of Warsaw Stock Exchange companies' data from https://www.biznesradar.pl. This website provides - at least to my knowledge - all data from financial reports of each company present at WSE.
2. Using NYSE guru strategies against WSE - in progress.
3. Analysis of final dataset for finding financial indices which could predict y/y dynamics of company - in progress.

Repo content:
- requirements.txt contains list of all packages used.
- analysis folder contains:
  - analysis of guru strategies.
- data folder contains:
	- dictionary of variable names and their full names in Polish and English;
	- dictionary of industry names;
	- companies folder with files with information from WSE companies' financial reports;
	- eco folder with files with economic indices;
	- full_datasets folder with merged companies' financial reports and economic indices.
- src folder contains:
  - data_import.py handling web scrapping;
	- func folder with:
		- importer.py with various functions helping with web scrapping.
