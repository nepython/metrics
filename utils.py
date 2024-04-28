'''
Contains utility functions used by the scopus script to read and store data,
'''
import json
import os
import pandas as pd
import pycountry

top_2pc_dataset = 'data/Table_1_Authors_career_2022_pubs_since_1788_wopp_extracted_202310.xlsx'

# Reading and storing data utility methods
def read_data(filepath):
    try:
        with open(filepath, 'r') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return []

def store_data(data, filepath):
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filepath, 'w') as fp:
        fp.write(json.dumps(data, indent=4))

def get_author_names(author_full_name, separator=', ', reverse=True):
    '''
    This is a utility method to get the first and last names of an author
    from the full name provided
    '''
    if reverse:
        names = author_full_name.split(separator, 1)
        first_name = names[-1]
        last_name = names[0] if len(names)==2 else ''
    else:
        names = author_full_name.rsplit(separator, 1)
        first_name = names[0]
        last_name = names[-1] if len(names)==2 else ''
    return first_name, last_name

def get_country_name(country_code):
    '''
    This is a utility method to get the country name from the country code
    in the top 2% researchers dataset using the pycountry library.
    '''
    try:
        country_name = pycountry.countries.get(alpha_3=country_code).name
        return country_name
    except AttributeError:
        # Handle cases where the country code is not found
        return ''

def get_top_2pc_df(filter_condition=dict()):
    df = pd.read_excel(top_2pc_dataset, sheet_name='Data', engine='openpyxl')
    # Filter the DataFrame based on the provided condition
    for key, value in filter_condition.items():
        df = df.loc[df[key] == value]

def get_cscore(first_name, last_name, affiliation, country, authors_df=get_top_2pc_df()):
    '''
    This is a utility method to get the c-score of an author based on the
    provided first name, last name, affiliation, and country.
    '''
    author_name = f'{last_name}, {first_name}'
    # Filter the DataFrame based on the provided condition
    authors_df = authors_df.loc[
        (authors_df['authfull'] == author_name) &
        (authors_df['inst_name'] == affiliation) &
        (authors_df['cntry'] == country)
    ]
    if not authors_df.empty:
        return authors_df.iloc[0]['c']
    return None
