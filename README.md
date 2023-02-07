# biocuration-diversity-search

Find biocurators that aren't from Australia, Canada, USA, or western Europe

## Phase 1: Identifying Papers

Help with curation:

1. Add additional keywords to `keywords.txt` (one per line) that you think are likely to get biocuration papers
2. Add venues that are specific for biocuration to `venues.tsv` based on their ISSN
3. Look at the uncurated sheet (`uncurated.tsv`). Follow the DOI. Check if any of the authors really are from an
   underrepresented country. Move to `curated.tsv` and add a note on the author names if it's only a few, say there's a
   lot if it's a big consortium paper, or say that there are none.

## Phase 2: Using Papers to Identify Authors

Checking into the papers that have been marked as `true` in the `curated.tsv` file, it's time to identify
exact authors along with their OpenAlex ID, ORCID (if available), and most importantly, email. The idea
is to make it possible to get in touch with these people.
