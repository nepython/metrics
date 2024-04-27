'''

'''
import json
import os
import pycountry

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

# Top 2% researchers dataset utility methods
def get_author_names(author_full_name):
    '''
    This is a utility method to get the first and last names of an author
    from the full name provided in the top 2% researchers dataset.
    '''
    # Split the full name into first and last names
    names = author_full_name.split(', ', 1)
    first_name = names[-1]
    last_name = names[0] if len(names)==2 else ''
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
