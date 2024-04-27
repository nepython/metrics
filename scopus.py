'''
Contains code related to fetching data from the Scopus API.
'''
import os
import pandas as pd
import requests
import xmltodict

from datetime import datetime
from functools import partial
from utils import read_data, store_data, get_author_names, get_country_name

# Set up your Scopus API key
api_key = '5aa908d24ec7e71ef0cf68cb3bff134d'

# Define the Scopus API endpoint for author search
scopus_search_url = 'https://api.elsevier.com/content/search/author'

# Define the Scopus API endpoint for retrieving author's publications
scopus_search_publications_url = 'https://api.elsevier.com/content/search/scopus'

# Define the Scopus Abstract Retrieval API to get detailed information about the publication
scopus_abstract_url = f'https://api.elsevier.com/content/abstract/eid'

# Set up headers with your API key
headers = {
    'X-ELS-APIKey': api_key,
}

# Store top 2% researchers data in a JSON file
data_dir = 'data'
top_2pc_filepath = f'{data_dir}/top_CS_researcher_by_h_index.json'

# Define the list of affiliations to search for authors
affiliations = [
    {'affiliation': 'UNSW', 'city': 'Sydney', 'country': 'Australia'},
    {'affiliation': 'University of Sydney', 'city': 'Sydney', 'country': 'Australia'},
]

def sort_author(author, country, affiliation):
    '''
    This method allows sorting the author based on the number of documents,
    affiliation country, and affiliation name.
    '''
    articles_published = int(author.get('document-count', 0))
    same_country = author.get('affiliation-current', {}).get('affiliation-country', '') == country
    same_affiliation = author.get('affiliation-current', {}).get('affiliation-name', '') == affiliation
    return articles_published, same_country, same_affiliation

def search_author_by_name(first_name, last_name, affiliation, country, field, exclude=list()):
    '''
    This method searches for an author in Scopus using the author's name,
    affiliation, country, and field of research. It returns the author
    with the highest number of documents based on the search results.
    '''
    query = f'AUTHLASTNAME({last_name}) AND AUTHFIRST({first_name}) AND {" OR ".join(map(lambda s: f"SUBJAREA({s})", field))}'
    response = requests.get(scopus_search_url, params={'query': query, 'count': 200}, headers=headers)

    if response.status_code == 200:
        results = response.json().get('search-results', {}).get('entry', [])
        # exclude authors already in the list
        results = [r for r in results if r.get('dc:identifier') not in exclude]
        # sort the authors based on the number of documents, affiliation country, and affiliation name
        sort_key = partial(sort_author, country=country, affiliation=affiliation)
        results.sort(key=sort_key, reverse=True)

        return results[0] if results else None
    else:
        return None

def search_author_by_affiliation(affiliation, city, country, limit=20):
    '''
    This method searches for an author in Scopus using the affiliation name,
    city, and country. It returns the author with the highest number of documents
    based on the search results.
    '''
    query = f'AFFIL("{affiliation}") AND AFFILCITY("{city}") AND AFFILCOUNTRY("{country}")'
    response = requests.get(scopus_search_url, params={'query': query, 'count': 200, 'sort': 'citedby-count'}, headers=headers)

    if response.status_code == 200:
        results = response.json().get('search-results', {}).get('entry', [])

        return results[:limit] if results else None
    else:
        return None

def fetch_author_publications(author_id, publications=None, start_index=0, top=200):
    '''
    This method fetches all publications for an author using the Scopus Author ID.
    It recursively fetches publications until the total number of publications
    is reached and returns the most cited publications as specified by `top`.
    '''
    if not publications:
        publications = []

    query = f'AU-ID({author_id})'
    response = requests.get(scopus_search_publications_url, params={
        'query': query,
        'start': start_index,
        'count': 200, # Maximum can be 200
        # 'sort': '-citedby-count' # Scopus API sort does not work
    }, headers=headers)

    if response.status_code == 200:
        search_results = response.json().get('search-results', {}).get('entry', [])

        for entry in search_results:
            publication_data = {
                'title': entry.get('dc:title', ''),
                'eid': entry.get('eid', ''),
                'citations': int(entry.get('citedby-count', 0)),
                'publication_name': entry.get('prism:publicationName', ''),
                'issn': entry.get('prism:issn', ''),
                'cover_date': entry.get('prism:coverDate', ''),
                'venue': entry.get('prism:aggregationType', ''),
                'volume': entry.get('prism:volume', ''),
                'issue': entry.get('prism:issueIdentifier', ''),
                'page_range': entry.get('prism:pageRange', ''),
                'doi': entry.get('prism:doi', ''),
            }
            publications.append(publication_data)

        # Fetch the next set of publications if available and limit is not reached
        start_index += len(search_results)
        if start_index < int(response.json().get('search-results', {}).get('opensearch:totalResults', 0)):
            return fetch_author_publications(author_id, publications, start_index, top)
        else:
            # We return the top publications based on citations
            publications.sort(key=lambda p: p['citations'], reverse=True)
            publications = publications[:100]
            for publication in publications:
                authors = []
                abstract_url = f'{scopus_abstract_url}/{entry.get("eid", "")}'
                response_abstract = requests.get(abstract_url, headers=headers)
                if response_abstract.status_code == 200:
                    author_data = xmltodict.parse(response_abstract.text).get('abstracts-retrieval-response', {}).get('authors', []).get('author', [])
                    if not isinstance(author_data, list): # If only one author
                        author_data = [author_data]
                    authors = list(map(lambda a: {
                            'scopus_id': a['@auid'],
                            'name': a.get('ce:indexed-name', ''),
                        }, author_data))
                publication['authors'] = authors

    return publications

def fetch_authors_top_2_percent(stop_at=100, scopus_results=list()):
    # Read the top 2% ranking excel file
    df = pd.read_excel(f'{data_dir}/Table_1_Authors_career_2022_pubs_since_1788_wopp_extracted_202310.xlsx', sheet_name='Data', engine='openpyxl')
    # We are only considering the Computer Science subject for this study
    df = df.loc[df['sm-field'] == 'Information & Communication Technologies']
    # NOTE: The cutoff year is 2022,and h column name changes based on cutoff year
    df = df.sort_values(by='h22', ascending=False)

    # A mapping between top 2% ranking `sm-field` and Scopus API `SUBJECTAREA`
    subject_areas_mapping = {
        'Information & Communication Technologies': ['COMP', 'MULT']
    }
    # Iterate through the rows of the DataFrame
    for index, (row_index, row) in enumerate(df.iterrows()):
        if index < len(scopus_results):
            # Since data was previously obtained for these authors, we can skip them
            print(f'{row["authfull"]}: Skipped')
            continue

        try:
            author_name = row['authfull']
            first_name, last_name = get_author_names(author_name)
            author_cscore = row['c']
            affiliation = row['inst_name']
            country = get_country_name(row['cntry'])
            field = field = subject_areas_mapping.get(row['sm-field'], [])

            # Search for the author in Scopus
            author_search_result = search_author_by_name(
                first_name=first_name,
                last_name=last_name,
                affiliation=affiliation,
                country=country,
                field=field,
                exclude=map(lambda x: x['scopus_id'], scopus_results)
            )

            # Process the search result as needed
            if author_search_result is not None:
                author_id = author_search_result.get('dc:identifier', '').split(':')[-1]
                author_publications = fetch_author_publications(author_id)
                scopus_results.append({
                    'scopus_id': author_id,
                    'name': author_name,
                    'cscore': author_cscore,
                    'publications': author_publications
                })
                if index >= stop_at-1:
                    break
            else:
                raise Exception(f"Author not found for: {author_name}, Affiliation: {affiliation}, Country: {country}, Field: {field}")
        except Exception as e:
            print(e)

    return scopus_results

def fetch_authors_by_affiliation(affiliation, limit=20, exclude=list()):
    affiliation_name = affiliation['affiliation']
    city = affiliation['city']
    country = affiliation['country']

    # Search for the authors in Scopus
    authors_search_results = search_author_by_affiliation(
        affiliation=affiliation_name,
        city=city,
        country=country,
        limit=limit
    )

    # Process the search results as needed
    scopus_results = []
    if authors_search_results is not None:
        for author_search_result in authors_search_results:
            author_id = author_search_result.get('dc:identifier', '').split(':')[-1]
            if author_id in exclude:
                continue
            author_name = author_search_result.get('preferred-name', {}).get('ce:indexed-name', '')
            author_publications = fetch_author_publications(author_id)
            scopus_results.append({
                'scopus_id': author_id,
                'name': author_name,
                'publications': author_publications,
                'affiliation': affiliation_name,
                'city': city,
                'country': country,
                'date fetched': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            })

    return scopus_results

if __name__ == '__main__':
    # Fetch the top 2% researchers in Computer Science
    # scopus_results=read_data(top_2pc_filepath)
    # scopus_results = fetch_authors_top_2_percent(stop_at=300)
    # store_data(scopus_results, top_2pc_filepath)

    # Fetch the top authors based on affiliation
    for affiliation in affiliations:
        file_dir = f'{data_dir}/{affiliation["affiliation"]}'
        exclude = [r.split('.json')[0] for r in os.listdir(file_dir) if '.json' in r] if os.path.exists(file_dir) else []
        scopus_results = fetch_authors_by_affiliation(affiliations, limit=20, scopus_results=scopus_results)
        for author in scopus_results:
            filepath = f'{file_dir}/{author["scopus_id"]}.json'
            store_data(scopus_results, filepath)
