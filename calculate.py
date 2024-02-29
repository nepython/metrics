from copy import deepcopy
from typing import List


def h_index(publications: List):
    '''
    H-index of an author is the largest
    number `h` such that the given author has published at least `h` papers
    that have each been cited at least `h` times.
    '''
    pubs = deepcopy(publications)
    pubs.sort(key=lambda x: x['number of citations'], reverse=True)
    h = 0
    for i, pub in enumerate(pubs, start=1):
        if pub['number of citations'] >= i:
            h = i
        else:
            break
    return h


def h_frac_index(publications: List):
    '''
    This is a variant of the h-index that allocates citations fractionally
    among co-authors. In other words, when using the number of citations to
    calculate the h-index of an author, they divide each paper's number of
    citations by its total number of authors.
    '''
    pubs = deepcopy(publications)
    pubs.sort(key=lambda x: x['number of citations'], reverse=True)
    h_frac = 0
    for i, pub in enumerate(pubs, start=1):
        if pub['number of citations'] / pub['number of authors'] >= i:
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
    pubs.sort(key=lambda x: x['number of citations'], reverse=True)

    cumulative_weights = 0
    for pub in pubs:
        weight = 1/pub['number of authors']
        cumulative_weights += weight

    hm = 0
    for pub in pubs:
        if pub['number of citations'] >= cumulative_weights:
            continue
        else:
            hm = pub['number of citations']
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
    pubs.sort(key=lambda x: x['number of citations'], reverse=True)

    h_papers = []
    for pub in pubs:
        h_paper = h_index(pub['cited by'])
        h_papers.append({'number of citations': h_paper})

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
    pubs.sort(key=lambda x: x['number of citations'], reverse=True)

    h_papers = []
    for pub in pubs:
        h_paper = h_index(pub['cited by'])
        h_papers.append({
            'number of citations': h_paper,
            'number of authors': pub['number of authors']
        })

    return h_frac_index(h_papers)
