"""The module importing data from websites."""

from ast import literal_eval as leval
import math
import re
from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
from progress.bar import PixelBar as pb
import requests

def company_importer(url):
    """The function importing dictionary of companies' codes from url."""

    # Cooking the soup...
    tab = bs(
        requests.get(
            url,
            timeout = 100
        ).text,
        'lxml'
    ).find('table')

    # Gathering dictionary of companies from table
    comp_dict = {}

    with pb('Gathering companies...', suffix = '%(percent)d%%') as pixel_bar:
        for rows in tab.find_all('a', {'class': 's_tt'}):
            comp_dict[(rows.get('href').replace('/notowania/', ''))] = []
            pixel_bar.next()

    print('Gathering companies is finished!')

    return comp_dict

def tab_finder(url, section_type, class_type):
    """Function looking for table in website."""
    # Input values are URL, section type (e.g. table, div),
    # class type (e.g. report-table, qTableFull)
    # Output is table found in website

    return bs(
        requests.get(url, timeout = 1000).content,
        'lxml'
    ).find(section_type, {'class':class_type})

class CompanyDF():
    """Data frame with single company data"""

    def __init__(self, code, features_dict):
        self.code = code
        self.features_dict = features_dict

    def regular_importer(self, url):
        """Function to deal with regular tabs."""
        # Input is URL for financial report of company

        def cell_cleaner(cell):
            """Subfunction clearing table's cells."""
            # Input is table cell, function extracts only value
            # without comments or unnecessary additions

            temp_cell = cell.text.replace(' ', '').replace('~', '')

            if re.search('[a-zA-Z]', temp_cell):
                temp_cell = temp_cell[:re.search('[a-zA-Z]', temp_cell).start()]

            if not temp_cell:
                result = math.nan
            elif '%' in temp_cell:
                result = leval(temp_cell[:-1]) / 100
            else:
                result = leval(temp_cell)

            return result

        tab = tab_finder(url, 'table', 'report-table')
        # Gathering list of quarters from table
        temp_data_dict, code_data_dict = {}, {}
        if tab:

            # Gathering rest of table
            for row in tab.find_all('tr'):
                # Workaround for omitting row with quarters
                if row.find('td', {'class':'f'}):
                    row_name = row.find('td', {'class':'f'}).text
                else:
                    row_name = ''

                # Gathering data from given row
                if row_name and row_name in [
                    'Kapitał (fundusz) podstawowy',
                    'Kapitał (fundusz) zapasowy'
                ]:
                    temp_data_dict[row_name] = []

                    cell = row.find_all('td', {'class':'h'})[-1]
                    # Some data clearing
                    temp_data_dict[row_name].append(cell_cleaner(cell))

            # Changing column names to codes
            for key, _ in temp_data_dict.items():
                if key in self.features_dict.keys():
                    code_data_dict[self.features_dict[key]] = temp_data_dict[key]
                else:
                    code_data_dict[key] = temp_data_dict[key]

        return code_data_dict

    def price_share_importer(self, url, data_frame, code):
        """Function adding companies' price, number of shares and capitalization"""

        data_dict = {
            'price':[],
            'number_of_shares':[],
            'capitalization':[]
        }

        tab = tab_finder(url, 'div', 'box-left').find('table')
        if tab:
            for row in tab.find_all('tr'):
                if row.find('th').text == 'Liczba akcji:':
                    data_dict['number_of_shares'].append(
                        int(row.find('td').text.replace(' ', ''))
                    )
                if row.find('th').text == 'Kapitalizacja:':
                    data_dict['capitalization'].append(
                        int(row.find('td').text.replace(' ', ''))
                    )
            data_dict['price'].append(
                data_dict['capitalization'][-1] / data_dict['number_of_shares'][-1]
            )

        data_frame = pd.merge(
            data_frame,
            pd.DataFrame(data_dict, index=[code]),
            left_index=True,
            right_index=True
        )

        if 'core_capital' in data_frame:
            data_frame[
                'core_capital_per_share'
            ] = data_frame['core_capital'] / data_frame['number_of_shares']

        if 'supplementary_capital' in data_frame:
            data_frame[
                'supplementary_capital_per_share'
            ] = data_frame['supplementary_capital'] / data_frame['number_of_shares']

        return data_frame
