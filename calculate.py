from copy import deepcopy
from typing import List
import matplotlib.pyplot as plt
import numpy as np

def total_citations(publications: List):
    '''
    The total number of citations of an author is the sum of the citations of all
    their papers.
    '''
    return sum([int(pub['citations']) for pub in publications])


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
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)
    h_frac = 0
    for i, pub in enumerate(pubs, start=1):
        if int(pub['citations']) / len(pub['authors']) >= i:
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
    pubs = list(filter(lambda x: int(x['citations']) > 0, pubs))
    pubs.sort(key=lambda x: int(x['citations']), reverse=True)

    cumulative_weights = 0
    for pub in pubs:
        weight = 1/len(pub['authors'])
        cumulative_weights += weight

    hm = 0
    for pub in pubs:
        if int(pub['citations']) >= cumulative_weights:
            continue
        else:
            hm = int(pub['citations'])
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


def h_leadership_index(scopus_id, publications: List):
    pubs = deepcopy(publications)
    weighted_citations = []
    for pub in pubs:
        if int(pub['citations']) == 0:
            weighted_citations.append(0)
        else:
            weighted_citations.append(int(pub['citations']) * leadership_weight(author_position=list(map(lambda x: x['scopus_id'], pub['authors'])).index(scopus_id), n=len(pub['authors'])))
    weighted_citations.sort(reverse=True)
    h_leadership = 0
    for i, w_cite in enumerate(weighted_citations, start=1):
        if w_cite >= i:
            h_leadership = i
        else:
            break
    return h_leadership


def leadership_weight(author_position, n=1, mean=0, std_dev=1):
    # Gaussian: we generate three extra points in the center for exclusion
    extra_center_points = 3
    x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, n+extra_center_points)
    y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-(x_values - mean)**2 / (2 * std_dev**2))
    # Inverse Gaussian
    inv_gaussian = 1 - y_values
    # Normalize so that the maximum weight is 1 for first and last author
    inv_gaussian = (inv_gaussian - np.min(inv_gaussian))/ (np.max(inv_gaussian) - np.min(inv_gaussian))

    weight_index = author_position if author_position < n/2 else author_position+extra_center_points
    weight = inv_gaussian[weight_index]
    return weight


def plot_leadership_weight(author_position, n=1, mean=0, std_dev=1, annotate=False):
    # Gaussian: we generate three extra points in the center for exclusion
    extra_center_points = 3
    x_values = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, n+extra_center_points)
    y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-(x_values - mean)**2 / (2 * std_dev**2))
    # Inverse Gaussian
    inv_gaussian = 1 - y_values
    # Normalize so that the maximum weight is 1 for first and last author
    inv_gaussian = (inv_gaussian - np.min(inv_gaussian))/ (np.max(inv_gaussian) - np.min(inv_gaussian))

    weight_index = author_position if author_position < n/2 else author_position+extra_center_points
    weight = inv_gaussian[weight_index]

    plt.plot(range(1, len(inv_gaussian)+1), inv_gaussian, label='Leadership weight curve')

    # Plot the exclusion three points range at the center
    exclusion_range = np.array(range(int(n/2), int(n/2)+extra_center_points))
    plt.plot(exclusion_range+1, inv_gaussian[exclusion_range], color='yellow', label='Exclusion range')

    # Plot all authors' weights
    x_range = np.delete(range(1, len(inv_gaussian)+1), exclusion_range)
    y_range = np.delete(inv_gaussian, exclusion_range)
    plt.scatter(x_range, y_range, label='Leadership weight')
    if annotate:
        for x, y in zip(x_range, y_range):
            plt.annotate(f'{y:.2f}', (x, y), textcoords="offset points", xytext=(0,5), ha='center')

    plt.scatter(weight_index+1, weight, label='Author weight', color='red')
    plt.xlabel('Author position')
    plt.ylabel('Weight')
    plt.title('Leadership weight')
    plt.legend()
    plt.show()









# import json
# with open('top_10_CS_researcher_all_publications.json', 'r') as f:
#     authors = json.load(f)
# author = authors[0]
# h_leadership_index(author["scopus_id"], author["publications"])

# # Broken
# # 1) Incorrect authors
# # 2) Linear distribution of weights

# print('No.\tTitle\tAuthors\tW Citation')
# pubs = deepcopy(publications)
# pubs.sort(key=lambda x: int(x['citations']), reverse=True)
# for i, (p, w_c) in enumerate(zip(pubs, weighted_citations)):
#     print(f'{i}\t{p["title"][:16].ljust(16)}\t{len(p["authors"])}\t{p["citations"]}\t{np.ceil(w_c)}')