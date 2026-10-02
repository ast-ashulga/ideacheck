### Per-column scan cost (SELECT <column> FROM table)
| Column | Scan |
|---|---|
| patents.publications.publication_number | 2.7 GB |
| patents.publications.family_id | 1.7 GB |
| patents.publications.country_code | 0.7 GB |
| patents.publications.kind_code | 0.6 GB |
| patents.publications.publication_date | 1.4 GB |
| patents.publications.filing_date | 1.4 GB |
| patents.publications.priority_date | 1.4 GB |
| patents.publications.title_localized | 17.3 GB |
| patents.publications.abstract_localized | 214.0 GB |
| patents.publications.claims_localized | 125.0 GB |
| patents.publications.description_localized | 1154.8 GB |
| patents.publications.cpc | 15.5 GB |
| patents.publications.ipc | 6.7 GB |
| patents.publications.assignee_harmonized | 4.5 GB |
| patents.publications.inventor_harmonized | 6.5 GB |
| patents.publications.citation | 38.8 GB |
| research.publications.publication_number | 2.7 GB |
| research.publications.title | 9.3 GB |
| research.publications.abstract | 117.7 GB |
| research.publications.cpc | 74.1 GB |
| research.publications.top_terms | 18.4 GB |
| research.publications.similar | 124.7 GB |
| research.publications.cited_by | 21.0 GB |
| research.publications.embedding_v1 | 88.7 GB |
| research.publications.url | 8.3 GB |
| research.publications.country | 1.8 GB |

### Planned query patterns
| Query | Scan |
|---|---|
| Keyword search, English title+abstract (LIKE) | 232.4 GB |
| Keyword search over claims (LIKE) | 127.6 GB |
| similar[] lookup for one publication | 64.2 GB |
| embedding_v1 k-NN from one seed (full scan) | 91.4 GB |
| Detail lookup for 25 publications incl. claims | 127.7 GB |
| Extract A: metadata + abstract, one CPC prefix (H05K7/20) | 261.2 GB |
| Extract B: Extract A + research (similar, embedding_v1, top_terms) | 495.6 GB |
| Extract C: Extract B + English claims | 620.6 GB |
| Research-table-only extract (title, abstract, cpc, similar, embedding_v1, top_terms) | 437.4 GB |

### Lean variants (read only the nested sub-fields needed)
| Query | Scan |
|---|---|
| cpc.code only | 13.3 GB |
| title_localized.text only | 16.0 GB |
| abstract_localized.text only | 212.8 GB |
| assignee_harmonized.name only | 4.0 GB |
| research similar.publication_number only | 61.5 GB |
| research cpc.code only | 13.3 GB |
| Lean index extract: ids, dates, cpc.code, title.text, assignee.name (pub table) | 42.8 GB |
| Lean semantic extract: research pub_no, cpc.code, similar.publication_number, embedding_v1 | 166.2 GB |
| Lean index + semantic (join) | 195.7 GB |
