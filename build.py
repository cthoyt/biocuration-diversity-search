from pathlib import Path
import pandas as pd

import pyalex
from pyalex import Works
from collections import defaultdict
from tabulate import tabulate

HERE = Path(__file__).parent.resolve()
EXCLUDE_PATH = HERE.joinpath("exclude_countries.tsv")
VENUES = HERE.joinpath("venues.tsv")
KEYWORDS = HERE.joinpath("keywords.txt")
CURATED = HERE.joinpath("curations.tsv")
UNCURATED = HERE.joinpath("uncurated.tsv")

pyalex.config.email = "cthoyt@gmail.com"

usual_suspects = dict(pd.read_csv(EXCLUDE_PATH, sep='\t').values)
curated_df = pd.read_csv(CURATED, sep='\t')
curated_dois = set(curated_df["doi"])

skip_keys = {'unknown'}
country_code_to_name = {
    r['key']: r['key_display_name']
    for r in (
        Works()
        .filter(institutions={"is_global_south": True})
        .group_by("institutions.country_code")
        .get()
    )
    if r['key'] not in skip_keys
}


class Accumulator:
    def __init__(self):
        self.results = defaultdict(dict)

    def append(self, works) -> None:
        for work in works:
            doi = work.get("doi")
            if not doi:
                continue
            doi = doi.strip().removeprefix("https://doi.org/")
            title = work['title']
            if not doi or not title or doi in curated_dois:
                continue
            for country, institutions in get_underrepresented_countries(work).items():
                key = (
                    doi, title,  # work['published_year'],
                )
                self.results[country][key] = institutions

    def tabulate(self, tablefmt: str = "github") -> str:
        df = pd.DataFrame(self.results)
        df.index.set_names(["doi", "title"], inplace=True)
        df = df.reset_index().fillna("")
        # Add doi link back
        df.sort_values("doi", inplace=True)
        first = "doi", "title"
        df = df[[*first, *sorted(c for c in df.columns if c not in first)]]
        df.to_csv(UNCURATED, sep='\t', index=False)
        df["doi"] = df["doi"].map(lambda s: f"https://doi.org/{s}")
        return tabulate(df, headers=df.columns, tablefmt=tablefmt,
                        showindex=False) + f"\n\nThere are {len(df.index)} rows."

    def print(self):
        print(self.tabulate())


def get_underrepresented_countries(work):
    dd = defaultdict(dict)
    for authorships in work['authorships']:
        for institution in authorships['institutions']:
            iid = institution.get('id')
            country_code = institution.get('country_code')
            if not iid or not country_code or country_code in usual_suspects:
                continue
            iid = iid.removeprefix("https://openalex.org/")
            country_display = country_code_to_name[country_code]
            dd[country_display][iid] = institution['display_name']
    return dict(dd)


def main():
    accumulator = Accumulator()

    venues = dict(pd.read_csv(VENUES, sep='\t').values)
    for issn in venues:
        accumulator.append(
            Works()
            .filter(institutions={"is_global_south": True}, host_venue={"issn": issn})
            .get()
        )

    keywords = KEYWORDS.read_text().splitlines(keepends=False)
    for keyword in keywords:
        accumulator.append(
            Works()
            .search(keyword)
            .filter(institutions={"is_global_south": True})
            .get()
        )

    accumulator.print()


if __name__ == '__main__':
    main()
