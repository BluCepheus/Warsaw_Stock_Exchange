"""The main module handling the scrapping the data."""

from datetime import datetime as dt
from func.last_data_importer import company_importer as cimp
from func.last_data_importer import CompanyDF
import glob
import os
import pandas as pd
from requests.exceptions import ConnectionError as ce
from requests.exceptions import ReadTimeout as rt
import joblib
import sklearn

def main_import():
    """Import of main data - financial reports of WSE companies."""

    url_main = 'https://www.biznesradar.pl/gielda/akcje_gpw'

    # Importing list of companies
    comp_dict = cimp(url_main)
    # Empty company code causing duplicated rows
    comp_dict.pop('NNGA', None)

    # Loading of variables dict.
    features_df = pd.read_csv('data\\features_dict.csv', header=0)

    all_companies_df = pd.DataFrame()

    # Importing data of companies

    code_iter = 0
    for code in comp_dict:
        code_iter += 1
        # Initialization of company data frame
        importer = CompanyDF(
            code,
            dict(zip(features_df['PL'], features_df['Variable']))
        )

        # List of urls
        url_list = [
            'https://www.biznesradar.pl/raporty-finansowe-bilans/' +
            code + ',Q,0',
            'https://www.biznesradar.pl/notowania/' + code
        ]

        # Importing data
        temp_data_dict = importer.regular_importer(url_list[0])
        company_df = pd.DataFrame(temp_data_dict, index=[code])
        if not company_df.empty:
            company_df = importer.price_share_importer(url_list[-1], company_df, code)

            if all_companies_df.empty:
                all_companies_df = company_df
            else:
                all_companies_df = pd.concat(
                    [all_companies_df, company_df]
                )

        print(f'Importing {code} is finished! ({int(100 * code_iter / len(comp_dict))}%)')

    all_companies_df.to_csv(
        'reports\\raw_data_' + dt.now().strftime('%d_%m_%Y') +'.csv'
    )

    print('Importing raw data is finished!')

def prediction():
    """Prediction based on raw data"""
        
    model_small = joblib.load('analysis\\models\\regression\\stacked_model_small')
    model_large = joblib.load('analysis\\models\\regression\\stacked_model_large')
    scaler = joblib.load('analysis\\transformers\\regression\\scaler')

    # Dataset loading (the newest raw data)
    dataset = pd.read_csv(
        max(
            glob.glob('reports\\*.csv'),
            key = os.path.getctime
        ),
        index_col=0,
        low_memory=False
    )

    dataset.dropna(inplace=True)

    dataset = dataset[[
        'capitalization', 'core_capital', 'number_of_shares', 'price', 'supplementary_capital',
        'core_capital_per_share', 'supplementary_capital_per_share'
    ]]

    data_scaled = pd.DataFrame(
        scaler.transform(dataset),
        columns=dataset.columns,
        index=dataset.index
    )

    prediction_small = model_small.predict(data_scaled)
    prediction_large = model_large.predict(data_scaled)

    final_report = pd.concat(
        [
            dataset,
            pd.DataFrame(prediction_small, columns=['small_pred'], index=dataset.index),
            pd.DataFrame(prediction_large, columns=['large_pred'], index=dataset.index)
        ],
        axis=1
    )

    final_report.to_csv(
        'reports\\report_' + dt.now().strftime('%d_%m_%Y') +'.csv'
    )

# Run the import
try:
    # main_import()
    prediction()
except ce :
    print('Failed to connect to the website.')
    print('Check your internet connection and website availability.')
    print('Main website is https://www.biznesradar.pl')
except rt:
    print('Read timed out.')
    print('Check your internet connection and website availability.')
    print('Main website is https://www.biznesradar.pl')
finally:
    print('The procedure has ended.')
