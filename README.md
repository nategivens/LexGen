# LexGen
LexGen (short of 'lexicon generator') is an app that I'm building to generate sci-fi / fantasy words. I built a tiny prototype model in a Jupyter notebook years ago, but this project is much more ambitious and is also therefore taking a long time to build. At present: it doesn't work yet. If the idea sounds cool, I'm sorry, it's not ready for you to run yet. I realistically hope to have a functional alpha version by 2021 that is capable of generating fake words by blending a variety of languages. I have big plans for what I'd like to do following that, but I'm not even going to try and plan anything out past the alpha.

# Basic Concept
The basic concept of LexGen is to read in large corpora (plural of 'corpus', it means a large body of text) from different languages and use them to construct language-distinctive frequency-weighted transition matrices. Then these transition matrices are used to randomly generate new "words" that follow the overall pattern for that language (or for more than one language).

## Corpora
To find the large corpora, I'm using subtitles from dubbed movies because I was able to find a big ole stack of data that contains lots and lots of words from many different languages. (Link coming, it's in my notes somewhere.) The corpora is basically a really long list of words along with a frequency of occurrence. Common words like "the" and "and" have a high frequency. Uncommon words (like "corpora") have much lower frequency.

## Transiton Matrices
The transition matrices are created by scanning the words and counting the number of times that a pattern of characters (between 1 and 4) transitions to another character. I'm creating 4 transition matrices for each corpus because I know English has distinctive patterns at least 4 characters long (e.g."ough" in "thought" or "drought"). 

I'll walk through a quick example so you see what I mean.

Consider the word "elephant". To create a transition matrix from this one word, the first thing I do is pad it with a leading and a trailing whitespace. (I'll denoate that with an underscore for readability.) Then, I create the 1-character transition matrix as follows:

|from_substr|to_char|
|---|---|
| _ | e |
| e | l |
| l | e |
| e | p |
| p | h |
| h | a |
| a | n |
| n | t |
| t | _ |

this is what the 2-character transition matrix looks like:

|from_substr|to_char|
|---|---|
| \_e | l |
| el | e |
| le | p |
| ep | h |
| ph | a |
| ha | n |
| an | t |
| nt | _ |

When creating a transition matrix for an entire coprus, I add a third column for the frequency. Every time I enter a transition, I also increment the frequency for that transition by the prevalence of the word in the corpus. This is why I call the transition matrices frequency-weighted. When I read in an entire corpus and include the frequency weighting (and then normalize it so that the total frequency for any given from_subst sums to 1), I get something that looks like this:

|from_str|to_char|rel_frequency
|---|---|---|
| _ | y	| 0.058127321
| _ | i	| 0.091154462
| _ | t	| 0.133611652
| _ | a	| 0.08608135
| _ | o	| 0.047640735
| _ | w	| 0.07598231
| _ | m	| 0.047660259
| _ | h	| 0.057666349
| _ | f	| 0.030843106
| _ | d	| 0.039075279

In this case, we're seeing that for this corpus the first character in a word was y about 5.8% of the time, i about 9.1% of the time, etc. The most common was t (13.4%) and the least common was f (3.1%). This is just the first few rows of a much, much bigger transition matrix, obviously.

## New Word Generation
Once I've converted an entire corpus into 4 transition matrices (the 1-, 2-, 3-, and 4-character transition matrices) it's easy to use them to generate new words.

To begin with, start with an empty space as your first character. Since we padded all of our words in the corpus with an empty space, it means we have a transition matrix that includes the empty space as the from_substr and then has all the possible characters that came next in that corpus weighted by their frequency. So we just pick a random number and use that to select the next character which--since it's the first non-whitespace--is actually the first character of our new word.

From that point on, we just continue to randomly sample from the transition matrices until the character that we sample is another whitespace. Remember, we padded the words in the corpus with whitespace at the beginning and end, so we naturally have captured the end-of-word dynamics to that language.

Note that there's a lot of ambiguity around how to sample from four different transition matrices. In addition, we can pick more than one language, in which case we'll have 8 or 12 or more transition matrices. Of course, they won't all be relevant all of the time. For the first letter of the word, only the 1-character transition matrix is relevant. Still, the exact details of how to sample across multiple transition matrices are one of the things I'll be tinkering with.

As a final pass, we will compare all of the words that we generated this way with the original corpus to make sure that we don't accidentally pass along a "new" word that is actually just an already-existing one. 

# Status & Immediate Next Steps
So far I have the logic for creating the transition matrices complete. Unfortunately, the data I'm using has some wonky characters in it. So my next step (next weekend) is to implement the load_corpus function to clean the data to only the characters that I expect for any given language. Once I have that done, I'll read in a few corpora and then begin work on implementing a generate_word function. Again: I implemented a toy version of this a year or two ago, so I know it can be done and yields pretty good results. I should have that done by the end of July 2020. At that point, LexGen will be able to generate new words.

# Future Plans
I have basically three longer-run goals for LexGen beyond the immediate steps
1. Implement more languages - The big challenge here is languages that don't use Latin characters. Russian, Chinese, Japanese, Korean... all of these languages can't be handled by LexGen as-is. I plan to find a way to convert the corpora into their respective Latin representations (for example, [Hepburn romanization](https://en.wikipedia.org/wiki/Hepburn_romanization) for Japanese) so that they can be ingested into LexGen. There's a huge number of related but smaller questions I haven't resolved yet. Suppose, for example, you're mixing Hungarian and English. Hungarian has characteres like é or ő that don't exist in English. If we leave them as-is, then any time you come across one of those characters, the next character *must* follow a Hungarian transition matrix because there will be no corresponding entry in the English transition matrices. This might be fine, but we might also want to consider a mapping so that the English transition matrix for 'e' is used when the 'é' is encountered in Hungarian. Ultimately, I'd love to convert to [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet) and use that instead of characters so that I'm really blending *sounds* instead of just symbols. That's a huge can of worms, however, especially when it comes to converting back from the IPA into letters). It's probably years out. For now, the most I can hope for is to find a programmatic way to Latinize languages with non-Latin letters and then tinker with rules for how to handle Latin-specific cases.
2. Developting software best practices - Right now I'm just writing code that works (mostly) without any testing and with only minimal attention to optimization and other standard best-practices. Because I really enjoy coding but have never been a full-time software developer (my background is in data analytics and data science, mostly), I'd like to take the time to use this project to practice those skills. So... expect unit testing soon after core features are implemented. 
3. Productionizing - I'm writing a sci-fi series that involves a ton of different alien species all interacting, so for me LexGen is intended as a world-building tool. However, I'd like to make it available for others to use as well, in everything from world-building for their own ficton to just generating names for D&D characters or locales or whatever. So I plan to make a web-accessible version of this at some point. 
