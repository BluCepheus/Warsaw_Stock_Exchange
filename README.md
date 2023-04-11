# Warsaw_Stock_Exchange

Benjamin Graham, the author of *The Intelligent Investor* and the proponent of value investing, taught that the returns an investor could expect were not proportional to the risk he was willing to assume, but rather, to the effort he was willing to put into his investments. This idea guided me while investing in the stock market and mobilized me to look for a strategy that would be stripped of the emotions that torment the stock market, and would be a set of clear rules pointing to companies worthy of interest.

The purpose of this repo is to gather all possible information about Warsaw Stock Exchange companies and assess whether it is possible to find financial and economic indices, which influence increase in share prices of each company.

TLDR: between Q4 2004 and Q4 2021, the best guru strategy (modified Kirkpatrick's) gave an average return of 18%, the classification model (random forest) gave a return of 25%, and the regression models (stacked models) gave returns of 27% and 29% (all values after inflation and taxes).

This repo contains four major features:

1. Web scrapping of Warsaw Stock Exchange companies' data from https://www.biznesradar.pl. This website provides - at least to my knowledge - all data from financial reports of each company present at WSE.
2. Using NYSE gurus' strategies against WSE.
3. Analysis of final dataset for finding financial indices which could predict y/y dynamics of company.
4. Script for getting predictions from regression stacked models on the latest data.

### In addition to this repo, download these trained models and put this folder in analysis folder: 
https://drive.google.com/drive/folders/1EAuTwkFK0eR8P52B2hA4vSq9Z2rCfBBJ?usp=share_link

Repo content:
- analysis folder contains:
  - models folder (content available at https://drive.google.com/drive/folders/1EAuTwkFK0eR8P52B2hA4vSq9Z2rCfBBJ?usp=share_link - put it in the analysis folder):
    - classification folder:
      - trained classification models (random_forest_classifier_fixed used as final model in classification analysis);
    - regression folder:
      - trained regression models (stacked_model_small and stacked_model_large used as final models in regression analysis);
    ### WARNING: the folder contains only the models used in the last phase of a given analysis!
  - transformers folder:
    - classification folder:
      - transformers used in classification (IMPUTER and SCALER);
    - regression folder:
       - transformer used in regression (SCALER);
  - analysis of gurus' strategies;
  - regression analysis predicting final price dynamics of given investment (i.e. the best price dynamics obtained within a year of buying the shares after taking inflation and tax into account);
  - classification analysis predicting whether given investment is able to provide return of at least 50% (after taking inflation and tax into account).
- data folder contains:
  - companies folder with files with information from WSE companies' financial reports;
  - eco folder with files with economic indices;
  - full_datasets folder with merged companies' financial reports and economic indices;
  - dictionary of variable names and their full names in Polish and English;
  - dictionary of industry names.
- reports folder contains:
  - raw data for prediction downloaded from https://www.biznesradar.pl;
  - report with predictions from regression model.
- src folder contains:
  - data_import.py handling web scrapping for analysis;
  - report_import.py handling web scrapping for prediction;
    - func folder with:
      - importer.py with various functions helping with web scrapping for analysis;
      - last_data_importer.py with various functions helping with web scrapping for prediction.
