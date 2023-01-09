"""The main module handling the scrapping the data."""

from datetime import datetime as dt
import glob
import os
from func.importer import company_importer as cimp
from func.importer import tab_finder as tfin
from func.importer import CompanyDF
from func.importer import EcoDF
from func.importer import FinalDF
import pandas as pd
from requests.exceptions import ConnectionError as ce
from requests.exceptions import ReadTimeout as rt

def main_import():
    """Import of main data - financial reports of WSE companies."""

    url_main = 'https://www.biznesradar.pl/gielda/akcje_gpw'

    # Importing list of companies
    comp_dict = cimp(url_main)

    # Loading of variables dict.
    features_df = pd.read_csv('data\\features_dict.csv', header=0)
    features_dict = dict(zip(features_df['PL'], features_df['Variable']))

    # Loading of industry dict.
    industry_df = pd.read_csv(
        'data\\industry_dict.csv',
        header=0,
        encoding = 'utf-8'
    )
    industry_dict = dict(zip(industry_df['PL'], industry_df['Variable']))

    all_companies_df = pd.DataFrame()

    # Importing data of companies

    code_iter = 0
    for code in comp_dict:
        code_iter += 1
        # Initialization of company data frame
        importer = CompanyDF(code, features_dict, industry_dict)

        # List of urls
        url_list = [
            'https://www.biznesradar.pl/wskazniki-wartosci-rynkowej/' + code,
            'https://www.biznesradar.pl/wskazniki-rentownosci/' + code,
            'https://www.biznesradar.pl/wskazniki-przeplywow-pienieznych/' + code,
            'https://www.biznesradar.pl/wskazniki-zadluzenia/' + code,
            'https://www.biznesradar.pl/wskazniki-plynnosci/' + code,
            'https://www.biznesradar.pl/wskazniki-aktywnosci/' + code,
            'https://www.biznesradar.pl/raporty-finansowe-rachunek-zyskow-i-strat/' +
            code +',Q,0',
            'https://www.biznesradar.pl/raporty-finansowe-bilans/' +
            code + ',Q,0',
            'https://www.biznesradar.pl/raporty-finansowe-przeplywy-pieniezne/' +
            code + ',Q,0',
            'https://www.biznesradar.pl/dywidenda/' + code,
            'https://www.biznesradar.pl/notowania/' + code
        ]

        # Importing data
        temp_data_dict, quarters = importer.regular_importer(url_list[0])
        if quarters:
            company_df = pd.DataFrame(temp_data_dict, index=quarters)
            company_df = importer.price_addition(company_df)

            for i, url in enumerate(url_list[1:-1]):
                temp_data_dict, quarters = importer.regular_importer(url)
                company_df = importer.regular_addition(company_df, temp_data_dict, quarters, i + 1)

            company_df = importer.dividend_importer(url_list[-2], company_df)
            company_df = importer.industry_country_importer(url_list[-1], company_df, code)
            company_df.dropna(subset=['best_price_dynamics_y', 'price_dynamics_y'], inplace=True)

        # Adding company's dataframe to final dataframe
        if not company_df.empty:
            if all_companies_df.empty:
                all_companies_df = company_df.reset_index(drop=True)
            else:
                all_companies_df = pd.concat(
                    [all_companies_df, company_df.reset_index(drop=True)]
                )

        print(f'Importing {code} is finished! ({int(100 * code_iter / len(comp_dict))}%)')

    all_companies_df.to_csv(
        'data\\companies\\companies_data_' + dt.now().strftime('%d_%m_%Y') +'.csv'
    )

    print('Gathering data is finished!')

def eco_import():
    """Additional importer - economic data."""

    # Loading of variables dict
    features_df = pd.read_csv('data\\features_dict.csv', header=0)
    features_dict = dict(zip(features_df['PL'], features_df['Variable']))

    # Accessing companies' data file to gather quarters
    quarters = sorted(
        pd.read_csv(
            max(
                glob.glob('data\\companies\\*.csv'),
                key = os.path.getctime
            )
        )['quarter'].unique()
    )

    # Initialization of sub urls dict
    url_dict = {}

    # Gathering sub urls dict
    tab = tfin(
        'https://www.biznesradar.pl/wskazniki-makroekonomiczne/',
        'table', 'qTableFull'
    )
    for row in tab.find_all('tr')[1:]:
        url_dict[
            'https://www.biznesradar.pl' + row.td.a['href'].replace(
                'notowania', 'notowania-historyczne'
            )
        ] = row.td.a.text

    # Initialization of dataframe with economic data
    eco_df = pd.DataFrame(index=quarters)

    # Importing economic data

    url_iter = 0
    for url, row_name in url_dict.items():
        url_iter += 1

        # Initialization of data frame with data from single url
        importer = EcoDF(features_dict)
        eco_df = pd.merge(
            eco_df, importer.eco_importer(url, row_name),
            how='left', left_index=True, right_index=True
        )
        print(
            f'Importing {features_dict[row_name]} is finished! ({int(100*url_iter/len(url_dict))}%)'
        )

    print('Gathering economic data is finished!')

    eco_df = pd.merge(
        eco_df, importer.indices_importer(quarters),
        how='left', left_index=True, right_index=True
    )
    print('Gathering indices data is finished!')

    eco_df.to_csv(
        'data\\eco\\economic_data_' + dt.now().strftime('%d_%m_%Y') +'.csv'
    )

    print('Gathering data is finished!')

def final_merge():
    """Merge of companies and economic data"""
    # Plus other additions

    merger = FinalDF(
        # Accessing companies' data file to gather quarters
        pd.read_csv(
            max(
                glob.glob('data\\companies\\*.csv'),
                key = os.path.getctime
            ),
            index_col=0
        ),
        # Accessing economic data file to gather quarters
        pd.read_csv(
            max(
                glob.glob('data\\eco\\*.csv'),
                key = os.path.getctime
            ),
            index_col=0
        )
    )

    final_df = merger.merger()
    print('Merging files is finished.')
    final_df = merger.guru_features(final_df)
    print('Calculating guru features is finished.')

    final_df.to_csv(
        'data\\full_datasets\\dataset_' + dt.now().strftime('%d_%m_%Y') +'.csv',
        index=False
    )

    print('The final file is ready!')


# Run the import
try:
    # main_import()
    eco_import()
    final_merge()
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
