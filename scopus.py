'''
Contains code related to fetching data from the Scopus API.
'''
import os
import pandas as pd
import requests
import xmltodict

from datetime import datetime
from functools import partial
from utils import read_data, store_data, get_author_names, get_country_name, get_top_2pc_df, get_cscore

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
affiliations = read_data(f'{data_dir}/affiliations.json')

def ensure_ratelimit(response):
    '''
    This method checks the rate limit headers in the response
    and sleeps if the rate limit is exceeded.
    '''
    if 'X-RateLimit-Remaining' in response.headers:
        total = int(response.headers['X-RateLimit-Limit'])
        remaining = int(response.headers['X-RateLimit-Remaining'])
        if remaining == 0:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            sleep_days = (reset_time - datetime.now().timestamp()) // (24 * 3600)
            raise Exception(f'Scopus API rate limit of {total} exceeded. Try again in {sleep_days} days.')

def sort_author(author, country, affiliation):
    '''
    This method allows sorting the author based on the number of documents,
    affiliation country, and affiliation name.
    '''
    articles_published = int(author.get('document-count', 0))
    same_country = author.get('affiliation-current', {}).get('affiliation-country', '') == country
    same_affiliation = author.get('affiliation-current', {}).get('affiliation-name', '') == affiliation
    return articles_published, same_country, same_affiliation

def search_author(first_name, last_name, affiliation, country, field=list(), exclude=list()):
    '''
    This method searches for an author in Scopus using the author's name,
    affiliation, country, and field of research. It returns the author
    with the highest number of documents based on the search results.
    '''
    query = f'AUTHLASTNAME({last_name}) AND AUTHFIRST({first_name}) AND {" OR ".join(map(lambda s: f"SUBJAREA({s})", field))}'
    response = requests.get(scopus_search_url, params={'query': query, 'count': 200}, headers=headers)
    ensure_ratelimit(response)

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
    ensure_ratelimit(response)

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
            publications = publications[:top-start_index]
            for publication in publications:
                authors = []
                abstract_url = f'{scopus_abstract_url}/{entry.get("eid", "")}'
                response_abstract = requests.get(abstract_url, headers=headers)
                ensure_ratelimit(response_abstract)
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

def fetch_author(kwargs):
    # Search for the author in Scopus
    author_search_result = search_author(**kwargs)

    # Process the search result as needed
    if author_search_result is not None:
        author_id = author_search_result.get('dc:identifier', '').split(':')[-1]
        author_publications = fetch_author_publications(author_id)
        return ({
            'scopus_id': author_search_result.get('dc:identifier', '').split(':')[-1],
            'name': f'{author_search_result['preferred-name']['surname']}, {author_search_result['preferred-name']['given-name']}',
            'publications': author_publications,
            'affiliation': author_search_result.get('affiliation-current', {}).get('affiliation-name', ''),
            'city': author_search_result.get('affiliation-current', {}).get('affiliation-city', ''),
            'country': author_search_result.get('affiliation-current', {}).get('affiliation-country', ''),
            'document_count': int(author_search_result.get('document-count', 0)),
            'subject_area': author_search_result.get('subject-area', list()),
            'date fetched': datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        raise Exception(f"Author not found for: {kwargs['author_name']}, Affiliation: {kwargs['affiliation']}, Country: {kwargs['country']}, Field: {kwargs['field']}")

def fetch_authors_top_2_percent(stop_at=100, scopus_results=list(), store_filepath=None):
    df = get_top_2pc_df(filter_condition={'sm-field': 'Information & Communication Technologies'})
    df = df.sort_values(by='h22', ascending=False)
    # A mapping between top 2% ranking `sm-field` and Scopus API `SUBJECTAREA`
    subject_areas_mapping = {
        'Information & Communication Technologies': ['COMP', 'MULT']
    }
    # Iterate through the rows of the DataFrame
    for index, (row_index, row) in enumerate(df.iterrows()):
        author_name = row['authfull']
        if index < len(scopus_results):
            # Since data was previously obtained for these authors, we can skip them
            continue

        try:
            first_name, last_name = get_author_names(author_name)
            author_cscore = row['c']
            affiliation = row['inst_name']
            country = get_country_name(row['cntry'])
            field = field = subject_areas_mapping.get(row['sm-field'], [])

            # Search for the author in Scopus
            author = fetch_author(
                first_name=first_name,
                last_name=last_name,
                affiliation=affiliation,
                country=country,
                field=field,
                exclude=map(lambda x: x['scopus_id'], scopus_results)
            )
            author['c-score'] = author_cscore
            scopus_results.append(author)

            if index >= stop_at-1:
                break
        except Exception as e:
            print(e)

    if store_filepath:
        store_data(scopus_results, store_filepath)

    return scopus_results

def fetch_authors_by_affiliation(affiliation, exclude=list(), store_dir=None):
    affiliation_name = affiliation['affiliation']
    country = affiliation['country']

    scopus_results = []

    for author_name in affiliation['researchers']:
        first_name, last_name = get_author_names(author_name, separator=' ', reverse=False)
        author = fetch_author(
            first_name=first_name,
            last_name=last_name,
            affiliation=affiliation_name,
            country=country,
            exclude=exclude
        )
        author['c-score'] = get_cscore(first_name, last_name, affiliation_name, country)
        scopus_results.append(author)

    if store_dir:
        for author in scopus_results:
            filepath = f'{store_dir}/{author["scopus_id"]}.json'
            store_data(author, filepath)

    return scopus_results

if __name__ == '__main__':
    # Fetch the top 2% researchers in Computer Science
    # scopus_results=read_data(top_2pc_filepath)
    # scopus_results = fetch_authors_top_2_percent(stop_at=300, store_filepath=top_2pc_filepath)

    # Fetch the top authors based on affiliation
    for affiliation in affiliations:
        file_dir = f'{data_dir}/{affiliation["affiliation"]}'
        exclude = [r.split('.json')[0] for r in os.listdir(file_dir) if '.json' in r] if os.path.exists(file_dir) else []
        scopus_results = fetch_authors_by_affiliation(affiliation, exclude=exclude, store_dir=file_dir)
