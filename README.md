# Research impact evaluation based on effective authorship contribution sensitivity: h-leadership index
Traditional bibliometric measures like the h-index have long been used to evaluate research performance. However, they often overlook the nuances of collaborative authorship, particularly the varying contributions of co-authors based on their position in the author list. This has led to inflated metrics and academic integrity concerns. This project introduces the h-leadership index, a novel metric that assigns weighted citations based on authorship position using a modified complementary unit Gaussian curve. It offers a fairer and more nuanced evaluation of academic contributions, especially in multi-authored publications. We apply this metric to analyze the top 50 researchers across Australia’s Group of Eight (Go8) universities and provide open-source tools for further exploration.

## Table of Contents
* [Overview](#overview)
* [Methodology](#methodology)
* [Results](#results)
* [Usage](#usage)
* [Citation](#citation)

## Overview
The h-leadership index addresses key limitations of traditional metrics:
* accounts for authorship position beyond just first and last authors.
* uses a modified complementary unit Gaussian distribution to assign weights.
* ensures middle authors receive appropriate recognition.
* avoids penalising large collaborative studies.

This metric is especially relevant in the context of Stanford’s Top 2% Scientists list, which emphasises first and last authorship but overlooks middle contributors. Our approach provides a more balanced and equitable assessment of research impact.

## Methodology
The project follows a four-step pipeline:

1. Review of Existing Metrics
    * We analyze h-index, hm-index, g-index, AR-index, and composite indicators like the c-score.

2. Design of the h-Leadership Index
    * Weights are assigned using a modified complementary unit Gaussian curve.
    * First and last authors receive the highest weights (up to 1.0).
    * Middle authors receive gradually decreasing weights, with a minimum of 0.3 beyond the 50th position.

3. Data Retrieval from Scopus
    * Top 50 researchers from each Go8 university were identified via Google Scholar.
    * Publication metadata was retrieved using Scopus APIs.
    * Data includes titles, citations, authorship, venues, and affiliations.

4. Metric Computation
    * Weighted citations are calculated per author.
    * The h-leadership index is computed as the maximum number of papers with weighted citations ≥ h.

For reproducibility, the pipeline is modular and configurable via affiliations.json.

## Results
We analyzed 400 researchers across Go8 universities, covering 168,563 publications:
* Journal Articles: 91.56%
* Conference Proceedings: 5.05%
* Books/Book Series: 3.25%

Key files
1. `results/{inst}/metrics.csv`
    * Contains author-wise data on number of publications, citations, h-index, h-frac-index, hm-index, h-leadership-index, author position and coauthor count.

2. `results/{inst}/h-leadership-index.csv`
    * Aggregate stats on institutional h-leadership. 

3. `results/{inst}/correlation_matrix.csv`
    * Pairwise Pearson correlation between bibliometrics under evaluation.

4. `results/{inst}/correlation_authorship_position.csv`
    * Pearson correlation between bibliometrics and authorship position.

## Usage
TO use our code for Scopus dataset preparation or analysis, follow below steps:
1. Install Python 3.9 or higher on your system
2. Clone this project
```
git clone https://github.com/nepython/metrics.git
cd metrics
```
3. Install dependencies
```python
pip install -r requirements.txt
```
4. Preparing bibliometric dataset
* [`scopus.py`](scopus.py)
    - Contains the code for fetching data from Scopus.
* [`metrics.py`](metrics.py)
    - Contains the various bibliometrics evaluated in this study.
* [`calculate.py`](calculate.py)
    - Contains the various utility methods for calculating the metrics for an author.
5. Performing bibliometric analysis
* [`data_analysis.ipynb`](data_analysis.ipynb)
    - Contains aggregate plots for bibliometrics vs affiliation.
* [`h_leadership design iteration.ipynb`](h_leadership%20design%20iteration.ipynb)
    - Contains a comparison of the different ways h-leadership index could have been implemented

## Citation
If you use this dataset or code in your research, please cite our paper:
```
@article{jain2025research,
  title={Research impact evaluation based on effective authorship contribution sensitivity: h-leadership index},
  author={Jain, Hardik A and Chandra, Rohitash},
  journal={arXiv preprint arXiv:2503.18236},
  year={2025}
}
```
