# Third-party data and code

| Source | Use | License | Access date |
|---|---|---|---|
| Google Books Ngram data, version 3 (20200217): `eng` (24 shards) and `eng-fiction` 1-grams and their `totalcounts-1` files, https://storage.googleapis.com/books/ngrams/books/datasetsv3.html | All word counts. The check streams them; they are not stored in this folder. `data/expected*.json` hold numbers derived from them. | CC BY 3.0 (stated on the dataset page) | 2026-11-26 |
| Repository `jbollen/rise_and_fall_of_rationality_in_language` (GitHub) by Scheffer, van de Leemput, Weinans and Bollen | The word lists are copied as facts into `checks/wordsets.py`, with citation. The check clones the repository and reads its 5000-word tables for the known-answer check only. Nothing from it is redistributed. | No license file in the repository | 2026-11-26 |
| Scheffer et al., PNAS 118(51) e2107848118 (2021), doi:10.1073/pnas.2107848118 | The claim under test; short quotes in the paper | Cited | 2026-11-26 |
| Google Ngram Viewer JSON series (`books.google.com/ngrams/json`) | Outside check of six word series in the verification stage; not redistributed and not part of the rerun | Google terms of service | 2026-11-26 |
