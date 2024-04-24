'''
The data for uncited publication's authors wasn't fetched thus being ignored in the calculations below.
'''
from copy import deepcopy
from typing import List, Union
import matplotlib.pyplot as plt
import numpy as np


def total_citations(publications: List):
    '''
    The total number of citations of an author is the sum of the citations of all
    their papers.
    '''
    return sum([int(pub['citations']) for pub in publications])


def median_citations(publications: List):
    '''
    The median number of citations of an author's papers.
    '''
    return np.median([int(pub['citations']) for pub in publications])


def percent_first_author(scopus_id, publications: List):
    '''
    The percentage of papers for which the author is the first author.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    first_author = len(list(filter(lambda x: x['authors'] and x['authors'][0]['scopus_id'] == scopus_id, pubs)))
    return first_author/len(pubs)*100 if len(pubs) > 0 else 0


def percent_last_author(scopus_id, publications: List):
    '''
    The percentage of papers for which the author is the last author.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    last_author = len(list(filter(lambda x: x['authors'] and x['authors'][-1]['scopus_id'] == scopus_id, pubs)))
    return last_author/len(pubs)*100 if len(pubs) > 0 else 0


def percent_single_author(publications: List):
    '''
    The percentage of papers for which the author is the sole author.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    single_author = len(list(filter(lambda x: len(x['authors']) == 1, pubs)))
    return single_author/len(pubs)*100 if len(pubs) > 0 else 0


def percent_single_or_first_author(scopus_id, publications: List):
    '''
    The percentage of papers for which the author is the sole author or the first author.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    single_or_first_author = len(list(filter(lambda x: x['authors'] and (len(x['authors']) == 1 or x['authors'][0]['scopus_id'] == scopus_id), pubs)))
    return single_or_first_author/len(pubs)*100 if len(pubs) > 0 else 0


def percent_single_or_first_or_last_author(scopus_id, publications: List):
    '''
    The percentage of papers for which the author is the sole author, the first author or the last author.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    single_or_first_or_last_author = len(list(filter(lambda x: x['authors'] and (len(x['authors']) == 1 or x['authors'][0]['scopus_id'] == scopus_id or x['authors'][-1]['scopus_id'] == scopus_id), pubs)))
    return single_or_first_or_last_author/len(pubs)*100 if len(pubs) > 0 else 0


def median_author_position(scopus_id, publications: List):
    '''
    The median position of the author in the author list.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    author_positions = []
    for pub in pubs:
        authors = list(map(lambda x: x['scopus_id'], pub['authors']))
        if scopus_id not in authors:
            continue
        author_positions.append(authors.index(scopus_id)+1)
    return np.median(author_positions)


def mean_coauthors(publications: List):
    '''
    The average number of authors per paper.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    return np.mean([len(pub['authors']) for pub in pubs])


def median_coauthors(publications: List):
    '''
    The median number of authors per paper.
    '''
    pubs = list(filter(lambda x: len(x['authors']) > 0, publications))
    return np.median([len(pub['authors']) for pub in pubs])


def i10_index(publications: List):
    '''
    The i10-index of an author is the number of papers with at least 10 citations.
    '''
    return len(list(filter(lambda x: int(x['citations']) >= 10, publications)))


def h_index(publications: List):
    '''
    H-index of an author is the largest
    number `h` such that the given author has published at least `h` papers
    that have each been cited at least `h` times.
    '''
    pubs = deepcopy(publications)
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)
    h = 0
    for i, pub in enumerate(pubs, start=1):
        if int(pub['citations']) >= i:
            h = i
        else:
            break
    return h


def h_frac_index(publications: List):
    '''
    This is a variant of the h-index that allocates citations fractionally
    among co-authors. In other words, when using the citations to
    calculate the h-index of an author, they divide each paper's number of
    citations by its total number of authors.
    '''
    pubs = deepcopy(publications)
    pubs = list(filter(lambda x: len(x['authors']) > 0, pubs))
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)
    h_frac = 0
    for i, pub in enumerate(pubs, start=1):
        if (int(pub['citations']) / len(pub['authors'])) >= i:
            h_frac = i
        else:
            break
    return h_frac


def hm_index(publications: List):
    '''
    This is a variant of the h-index that addresses the challenges of multiple
    authorship by utilizing fractionalized counting of papers. The hm-index
    represents the reduced number of papers that have been cited hm or more times,
    where hm is a threshold, while other papers in the set have been cited not
    more than hm times.
    '''
    pubs = deepcopy(publications)
    pubs = list(filter(lambda x: len(x['authors']) > 0, pubs))
    pubs.sort(key=lambda x: int(x['citations']))

    cumulative_weights = 0
    for pub in pubs:
        weight = 1/len(pub['authors'])
        cumulative_weights += weight

    hm = 0
    for pub in pubs:
        if int(pub['citations']) < cumulative_weights:
            hm = int(pub['citations']) # modified logic
        else:
            break
    return hm


def hp_index(publications: List):
    '''
    Consider a paper p and the set of papers citing p be the set
    C = [c1,c2,c3, ...,cn]. The h-index of a paper is equal to the largest number
    `h` such that at least `h` papers from p have at least `h` citations each.

    The hp-index of an author is the h-index of the h-index of all the
    author's papers.
    '''
    pubs = deepcopy(publications)
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)

    h_papers = []
    for pub in pubs:
        h_paper = h_index(pub['cited by'])
        h_papers.append({'citations': h_paper})

    return h_index(h_papers)


def hp_frac_index(publications: List):
    '''
    Consider a paper p and the set of papers citing p be the set
    C = [c1,c2,c3, ...,cn]. The h-index of a paper is equal to the largest number
    `h` such that at least `h` papers from p have at least `h` citations each.

    The hp-frac-index of an author is the h-frac-index of the h-index of all the
    author's papers.
    '''
    pubs = deepcopy(publications)
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)

    h_papers = []
    for pub in pubs:
        h_paper = h_index(pub['cited by'])
        h_papers.append({
            'citations': h_paper,
            'number of authors': len(pub['authors'])
        })

    return h_frac_index(h_papers)


def cscore(scopus_id, publications: List):
    '''
    The c-score is a sum of the normalised logarithms of total citations,
    h-index, hm-index, number of single-authored papers, number of
    single-first authored papers and number of single-first-last authored papers.
    '''
    # TODO: Cscore is calculated on normalised c_metrics
    total_cites = total_citations(publications)
    h = h_index(publications)
    hm = hm_index(publications)
    single_authored = percent_single_author(publications)
    single_or_first_authored = percent_single_or_first_author(scopus_id, publications)
    single_or_first_or_last_authored = percent_single_or_first_or_last_author(scopus_id, publications)

    c_metrics = np.array([
        total_cites,
        h,
        hm,
        single_authored,
        single_or_first_authored,
        single_or_first_or_last_authored
    ])
    cscore = np.log(c_metrics).sum()
    return cscore

def h_leadership_index(scopus_id, publications: List):
    '''
    The h-leadership index is a variant of the h-index that allocates citations
    fractionally among co-authors, but also takes into account the position of
    the author in the author list. The h-leadership index is the largest number
    `h` such that the given author has published at least `h` papers that have
    each been cited at least `h` times, and the author's position in the author
    list is taken into account.
    '''
    pubs = deepcopy(publications)
    weighted_citations = []
    cum_l_weight = 0
    for pub in pubs:
        authors = list(map(lambda x: x['scopus_id'], pub['authors']))
        if int(pub['citations']) == 0:
            weighted_citations.append(0)
        elif scopus_id in authors:
            author_position = authors.index(scopus_id)+1
            l_weight = leadership_weight(author_position=author_position, n=len(pub['authors']))
            cum_l_weight += l_weight
            weighted_citations.append(int(pub['citations']) * l_weight)
    weighted_citations.sort(reverse=True)
    h_leadership = 0
    for i, w_cite in enumerate(weighted_citations, start=1):
        if w_cite >= i:
            h_leadership = i
        else:
            break
    return h_leadership


def leadership_weight(author_position=1, n=1, mean=0, std_dev=1):
    '''
    The leadership weight of an author based on their position in the author list
    using a normalised inverse gaussian curve. The first author's leadership weight
    reduces logarithmically with the increase in the number of authors.
    '''
    if author_position > n/2: # We assign the same weights to the first and last authors
        author_position = n-author_position+1

    ideal_max_authors = 100
    # Gaussian curve
    x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, ideal_max_authors)
    y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-(x_values - mean)**2 / (2 * std_dev**2))
    y_values = y_values[:len(y_values)//2] # Gaussian plot is symmetric, so we only need half of it
    # Inverse Gaussian
    inv_gaussian = 1 - y_values
    # Normalisation
    inv_gaussian = (inv_gaussian - np.min(inv_gaussian))/ (np.max(inv_gaussian) - np.min(inv_gaussian)) # first author weight becomes 1
    inv_gaussian = 0.3 + 0.7* inv_gaussian * (1-min(np.log(n)/(4*np.log(ideal_max_authors)), 1)) # first author contribution reduces logarithmically with increase in number of authors
    inv_gaussian_x = np.arange(1, len(inv_gaussian)+1)

    author_positions = np.arange(1, n+1)
    author_weights = np.interp(author_positions, inv_gaussian_x, inv_gaussian)
    author_weight = author_weights[author_position-1]
    return author_weight


def plot_leadership_weight(author_position=1, n=1, mean=0, std_dev=1, annotate:Union[bool,str]=False):
    '''
    Plot the leadership weight of an author based on their position in the author list using a normalised inverse gaussian curve.
    The first author's leadership weight reduces logarithmically with the increase in the number of authors.
    '''
    if author_position > n/2: # We assign the same weights to the first and last authors
        author_position = n-author_position+1

    ideal_max_authors = 100
    # Gaussian curve
    x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, ideal_max_authors)
    y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-(x_values - mean)**2 / (2 * std_dev**2))
    y_values = y_values[:len(y_values)//2] # Gaussian plot is symmetric, so we only need half of it
    # Inverse Gaussian
    inv_gaussian = 1 - y_values
    # Normalisation
    inv_gaussian = (inv_gaussian - np.min(inv_gaussian))/ (np.max(inv_gaussian) - np.min(inv_gaussian)) # first author weight becomes 1
    inv_gaussian = 0.3 + 0.7* inv_gaussian * (1-min(np.log(n)/(4*np.log(ideal_max_authors)), 1)) # first author contribution reduces logarithmically with increase in number of authors
    inv_gaussian_x = np.arange(1, len(inv_gaussian)+1)

    author_positions = np.arange(1, n+1)
    author_weights = np.interp(author_positions, inv_gaussian_x, inv_gaussian)
    author_weight = author_weights[author_position-1]

    plt.plot(inv_gaussian_x, inv_gaussian, label='Leadership weight curve')

    # Plot all authors' weights
    plt.scatter(author_positions, author_weights, label='Leadership weight')
    if annotate == 'all':
        for x, y in zip(author_positions, author_weights):
            plt.annotate(f'{y:.2f}', (x, y), textcoords="offset points", xytext=(0,5), ha='center')
    elif annotate is True:
        plt.annotate(f'{author_weight:.2f}', (author_position, author_weight), textcoords="offset points", xytext=(0,5), ha='center')

    plt.scatter(author_position, author_weight, label='Author weight', color='red')
    plt.xlabel('Author position')
    plt.ylabel('Weight')
    plt.title('Leadership weight')
    plt.legend()
    plt.show()
