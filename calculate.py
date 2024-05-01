'''
Calculate metrics for the author
'''
import os
import pandas as pd

from metrics import *
from scopus import data_dir, top_2pc_filepath, affiliations
from utils import read_data

def metrics(author, rows=list()):
    '''
    Calculate metrics for the author and append the results to the rows list.
    '''
    try:
        rows.append({
            'Name': author['name'],
            'Publications': len(author['publications']),
            'Total citations': total_citations(author['publications']),
            'Median citations': median_citations(author['publications']),
            'h-index': h_index(author['publications']),
            'h-frac-index': h_frac_index(author['publications']),
            'hm-index': hm_index(author['publications']),
            'h-leadership-index': h_leadership_index(author['scopus_id'], author['publications']),
            '% first author': percent_first_author(author['scopus_id'], author['publications']),
            '% last author': percent_last_author(author['scopus_id'], author['publications']),
            '% single author': percent_single_author(author['publications']),
            'Median author position': median_author_position(author['scopus_id'], author['publications']),
            # 'cscore': author['c-score'],
            'i10-index': i10_index(author['publications']),
            'Average number of Authors': mean_coauthors(author['publications']),
            'Median number of Authors': median_coauthors(author['publications']),
        })
    except Exception as e:
        raise e
        print(f"Error processing author: {author['name']}")

def metric_summary(authors_df, metric, store_dir=None):
    '''
    Calculate the summary statistics for the metric.
    '''
    metric_summary = authors_df[metric].describe()
    if store_dir:
        metric_name = metric.replace('-', '_').replace('%', '').replace(' ', '_').lower().strip()
        metric_summary.to_csv(f'{store_dir}/{metric_name}.csv', sep=',', header=True)
    return metric_summary

def correlation_analysis(authors_df, store_dir=None):
    '''
    Perform correlation analysis for the author metrics.
    '''
    # Select all columns except Name
    cols_to_correlate = authors_df.columns[1:]
    position_col = 'Median author position'

    # Calculate the correlation matrix
    correlation_matrix = authors_df[cols_to_correlate].corr()

    # Extract the correlation values between an author's median position and other metrics
    correlation_with_position = correlation_matrix[position_col].drop(position_col)

    # Save the correlation matrix to a CSV file
    if store_dir:
        correlation_matrix.to_csv(f'{store_dir}/correlation_matrix.csv', sep=',')
        correlation_with_position.to_csv(f'{store_dir}/correlation_authorship_position.csv', sep=',')

    # Print or use the correlation values as needed
    return correlation_with_position

if __name__ == '__main__':
    results_dir = 'results'

    # # Read the top 2% researchers dataset
    # rows = []
    # authors = read_data(top_2pc_filepath)
    # for author in authors:
    #     metrics(author, rows)
    # authors_df = pd.DataFrame(rows)

    # # Store the metrics in a CSV file
    # store_dir = f'{results_dir}/top_2pc'
    # authors_df.to_csv(f'{store_dir}/metrics.csv', sep=',', index=False)
    # metric_summary(authors_df, 'h-leadership-index', store_dir)
    # correlation_analysis(authors_df, store_dir)

    # Read reseachers fetched using affiliation
    for affiliation in affiliations:
        file_dir = f'{data_dir}/{affiliation["affiliation"]}'
        files = os.listdir(file_dir)
        rows = []
        for file in files:
            author = read_data(f'{file_dir}/{file}')
            metrics(author, rows)

        authors_df = pd.DataFrame(rows)
        authors_df.sort_values(by='h-leadership-index', ascending=False, inplace=True)

        # Store the metrics in a CSV file
        store_dir = f'{results_dir}/{affiliation["affiliation"]}'
        if not os.path.exists(store_dir):
            os.makedirs(store_dir)
        authors_df.to_csv(f'{store_dir}/metrics.csv', sep=',', index=False)
        metric_summary(authors_df, 'h-leadership-index', store_dir)
        correlation_analysis(authors_df, store_dir)
