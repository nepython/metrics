# `Metrics project`

## Setup
* Python 3.9 or above is recommended
* Clone this project
* Install the dependencies
```python
cd metrics
pip install -r requirements.txt
```

## Data
* `Table_1_Authors_career_2022_pubs_since_1788_wopp_extracted_202310.xlsx`
Contains the latest Stanford top 2% researchers list released on October 2023 which has a cutoff year of 2022.

* `results/top_CS_researcher_by_h_index.json`
    - Contains the data mined for the top Computer Science researchers fetched from Scopus based on their
`h-index` specified in the Stanford list.
    - Currently contains top 300 researchers
    - Note some of the researchers might be incorrectly mined due to same names and affiliation

* `results/metrics.csv`
    - Contains a detailed analysis for the top 50 Computer science researchers across 16 metrics using their top 100 publications.
    - Kindly note that although we mined the top 300 researchers, the list beyond 50 is missing authors data as Scopus API might have reached its weekly retrieval limit.

## Code
* `scopus.ipynb`
    - Contains the code for fetching data from Scopus
    - Displays the different metrics for authors
* `plots.ipynb`
    - Contains a comparision of the different ways h-leadership index could have been implemented
* `calculate.py`
    * Contains the various utility methods for calculating the metrics for an author
