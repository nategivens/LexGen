# Dev Notes

## 2021

### January

#### Janaury 5, 2021

Still working on en_50k_2018-ingestion.ipynb. Nearly finished, and what I've learned is that there isn't one obvious way to clean the data at the word-level. The logical thing to do is keep multiple versions of a single corpus, I think. So we have a pipeline that looks something like this:

                                |--> version_1
                                | 
raw_corpus --> cleaned_corpus --|--> version_2
                                |
                                |--> version_3
                                
Each version will have it's own set of transition matrices. This changes the underlying data structure for picking corpora to generate new words. Basically, you don't just pick a corpus, you have to pick a _version_, too. I'll need to think about how to store those.

Also, while I'm here, I don't want to forget the overall model I have for building words. What I've got in mind right now is a two-layer approach.

Layer 1 (Base Layer): Pick large corpora that are supposed to represent an entire language, up to 4. Also define blending parameters.

Layer 2 (Specific Layer): Pick a small corpora that is supposed to be much for focused. For example, all the planet names from Star Wars or all made-up language names. 

The idea is emphasize Layer 2 first, but make sure you can sort of fill in the gaps where data is sparse with Layer 1 in order to prevent the problem of just re-generating the same words from the Layer 2 corpus. I think you could do this by basically merging the Layer 2 transition matrices with the Layer 1 transition matrices with some weighting factor to give a big boost to Layer 2.

Of course, if you're merging transition matrices, that doesn't work so great if you keep the language transition matrices separate (which is how I'd envisioned actually cranking through the word-generation process), so you'd have to merge those first.

The advantage is that if you do all this TM-merging, then at the end of the day you have a single TM to iterate through for new word creation, which should make for much simpler logic.

In terms of data structures and actual user interactions, you're going to want to have:

1. a library of corpora with associated variants (Layer 1)
2. a few smaller corpora for specific flavor (Layer 2)
3. the ability to upload small, Layer 2 corpora and do basic cleaning and TM generation
4. ability to define blending parameters

Then the program works by taking all of these TMs, creating one effective TM, and creating new words from that. The words are compared to all the selected corpora to avoid duplication and you output the survivors.