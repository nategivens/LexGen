# Project Plan

## Corpora Acquisition

Need some large corpora to work from. For starters, I'm using Hermit Dave's word lists, which covers a lot of languages. Eventually I'll want to find some more sources for the existing languages, but also find some interesting new languages / word sets. Would love to get some constructed languages (such as Klingon and various Middle Earth languages). 

## Corpora Ingestion

This is the process from loading a corpus (long list of words) through to creating the transition matrices for it. 

1. Load words - Should handle either a 1-column text file with one word per line or a 2-column text file with one word, a delimeter (to be specified) and then a frequency count)
2. Clean words

## Tables

The following tables are needed to make this project run:

### Corpora

All the corpora that have been successfully ingested (and not removed).

| field name       | key type | data type | notes |
| ----             | ---      | ---       | ---   | 
| corpus_filename  | primary  | str       | the filename for this corpus |
| language_code    | foreign  | str       | language code for the corpus |
| source_url       |          | str       | url from which the corpus was obtained |
| note             |          | str       | brief description of the corpus |

### Activity Logs

Record of selected user activities and links to detailed logs.

| field name      | key type | data type | notes |
| ---             | ---      | ---       | ---   |
| log_filename    | primary  | str       | filename of log |
| activity_type   |          | str       | activity type: ingest_corpus, generate_words, etc. |
| activity_status |          | str       | activity status: processing, completed, completed with warnings, errored |
| start_dtime     |          | dtime     | activity start dtime |
| end_dtime       |          | dtime     | activity end dtime |
| corpus_filename | foreign  | str       | the filename for this corpus (if it was ingest_corpus) |
| output_filename | foreign  | str       | the filename for the output (if it was generateWords) |

* Logged activities include: ingest corpus, delete corpus, generate words
* User is not logged at this point because there's no user-validation. This isn't a security feature at present. It's a data feature.

### Languages

A table of all the languages that LexGen recognizes.

| field name            | key type | data type | notes |
| ---                   | ---      | ---       | ---   |
| language_code         | primary  | str       | The 2-digit ISO code for real languages, or an invented 2-digit code for constructed ones |
| language_name         |          | str       | Full name of the language |
| native_letter_set     | 
| valid_latin_letters   |          | str       | pipe-delimited list of valid letters for the Latinized version of the language |
