import pandas as pd
import os
import itertools
from datetime import datetime


class LexGen:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.lang_dict = None
        self.corpora = None
        self.trans_mats = None

        self.read_lang_dict()
        # populates self.lang_dict pandas df with cols = [lang_code, lang_name]
        # later, this will become reading the languages table from a database

        self.scan_corpora()
        # populates self.corpora pandas df with cols = [corpus_name, corpus_filepath]
        # later, this will become reading the corpora table from a database

        self.scan_trans_mats()
        # populates trans_mats pandas df with cols = [corpus_name, prefix_len, trans_matrix_filepath]
        # later, this will become reading the transition_matrices table from a database

    def read_lang_dict(self):
        # check to see if file exists
        # check to see if columns exist (and not extra columns)
        # check to see if data exists (rows > 0)
        # check to see if datatypes are valid (alphabetic strings, non-numeric)
        abs_fname = os.path.join(self.script_dir, 'data', 'ref', 'lang_ref.dat')
        self.lang_dict = pd.read_csv(abs_fname)

    def scan_corpora(self):
        # read all files in data/corpora subfolder of current directory
        corpora_path = os.path.join(self.script_dir, 'data', 'corpora')
        # the .rsplit('.', 1)[0] drops the file extension
        corpora_files = [f.rsplit('.', 1)[0] for f in os.listdir(corpora_path) if os.path.isfile(os.path.join(corpora_path, f))]
        corpora_indiv_paths = [os.path.join(corpora_path, p + '.dat') for p in corpora_files]
        self.corpora = pd.DataFrame(list(zip(corpora_files, corpora_indiv_paths)), columns=['corpus_name', 'corpus_filepath'])

    def scan_trans_mats(self):
        # create a dataframe with spaces for all of the corpora
        # then scan to see if they exist and populate last_updated accordingly
        # dataframe columns: corpus_name, prefix_len, trans_mat_name_, file_path, last_updated

        # create corpus_name list (list of corpus names, but 4x per corpus)
        # the inner list comprehension here creates a list of lists, where each inner list is 4x the corpus name
        # see: https://stackoverflow.com/questions/2785954/creating-a-list-in-python-with-multiple-copies-of-a-given-object-in-a-single-lin
        # the outer list flattens it
        # see: https://stackoverflow.com/questions/2961983/convert-multi-dimensional-list-to-a-1d-list-in-python
        corpus_name_col = [x for sublist in [list(itertools.repeat(c, 4)) for c in self.corpora['corpus_name'].values.tolist()] for x in sublist]

        # create prefix_col list (list of prefix lengths (1, 2, 3, 4) repeated once for each corpus
        prefix_len_col = list(range(1,5))*self.corpora.shape[0]

        # create trans_mat_name list {corpus_name}_tm{prefix_length}
        trans_mat_name_col = ['{0}_tm{1}'.format(x[0], x[1]) for x in zip(corpus_name_col, prefix_len_col)]

        # create the full path for each trans_mat
        trans_mat_path = os.path.join(self.script_dir, 'data', 'trans_mats')
        trans_mat_path_col = [os.path.join(trans_mat_path, tm + '.dat') for tm in trans_mat_name_col]

        # create a list of Nones for the initial values of the last_updated column
        last_udpated_col = [None] * (self.corpora.shape[0] * 4)

        # turn these lists into columns in a dataframe
        trans_mat_df = pd.DataFrame(list(zip(corpus_name_col, prefix_len_col, trans_mat_name_col, trans_mat_path_col, last_udpated_col))
                                    , columns=['corpus_name', 'prefix_len', 'trans_mat_name', 'file_path', 'last_updated'])

        # run through the entire list and attempt to read each file
        # if it exists, update with last_updated datetime
        for index, row in trans_mat_df.iterrows():
            try:
                trans_mat_df.at[index, 'last_updated'] = datetime.fromtimestamp(os.stat(row['file_path']).st_mtime)
            except OSError as e:
                pass

        self.trans_mats = trans_mat_df

    def load_corpus(self, corpus_name, corpus_file):
        # read in the corpus line by line
        # first string is word, second string (if exists) is frequency
        # get unique list of words with frequency
        # write output to file: /data/corpora/{corpus_name}.dat
        pass

    def refresh_trans_mats(self):
        # iterate over self.trans_mats
        # call create_trans_mats for every row where last_updated = None
        # call scan_trans_mats at the end
        pass

    def create_trans_mats(self, corpus_name):
        # use the corpora dataframe to lookup the associated filepath for the corpus_name provided
        corpus_file_path = self.corpora.loc[self.corpora['corpus_name'] == corpus_name, 'corpus_filepath'].iloc[0]
        # create a list of 4 dictionaries, one for each transition matrix
        tms = [{} for i in range(4)]
        # the transition matrix dictionaries will be nested dictionaries with structure as follows:
        # Outer Dictionary key: the prefix (1 - 4 characters)
        # Outer Dictionary value: the Inner Dictionary
        # Inner Dictionary key: the suffix (1 character)
        # Inner Dictionary value: the frequency of transitioning to that suffix given the prefix (Outer Dictionary key)

        # create a list of 4 dictionaries, one for each cumulative frequency
        from_substr_freqs = [{} for i in range(4)]
        # tot_freq is a dictionary with structure as follows:
        # key: the prefix
        # value: cumulative frequency for all transitions

        # read in all of the prefixes, suffixes, and frequencies
        with open(corpus_file_path, 'r') as c_file:
            for line in c_file:
                tokens = line.split(sep=' ')
                word = tokens[0].strip()
                frequency = int(tokens[1])
                word = ' ' + word + ' '
                for i in range(1, len(word)):
                    to_char = word[i]
                    # for each character in the word, we're going to iterate through our substring lengths = (1, 2, 3, 4)
                    # (of course, the indicies are actually t = (0, 1, 2, 3) )
                    for t in range(4):
                        from_substr = word[i-t-1:i] if i > t else None

                        # now we're going to store the substrings and associated frequency in our transition matrix dictionaries
                        # remember the structure of the these transition matrix dictionaries.
                        # tms is a list of dictionaries, one dictionary for each substring length
                        # for each dictionary, the outer key is from_substr and the value is another dictinoary with inner key / value
                        # the inner key is the to_char
                        # the inner value is the frequency of transition from outer key (from_substr) to inner key (to_char)

                        # check to see if this from_substr has been found before
                        if from_substr in tms[t].keys():
                            # if the from_substr has been found before, check to see if the to_char has been associated with it
                            if to_char in tms[t][from_substr].keys():
                                # if we already have the from_substr / to_char pair before, update the frequence
                                tms[t][from_substr][to_char] = tms[t][from_substr][to_char] + frequency
                            else:
                                # if we already have the from_substr but not the to_char, add to_char: frequency to the dictionary
                                tms[t][from_substr][to_char] = frequency
                        elif from_substr is not None:
                            # if we don't have
                            # for the value, I need a dictionary with to_char as the key and frequency as the value
                            tms[t][from_substr] = {to_char: frequency}
                        else:
                            # since from_substr is None, we ignore it
                            pass

                        # in this code block, we're going to update a total frequency for the outer keys (from_substr's)
                        # this is so that we can convert all our conversion frequencyes from outer key (from_substr) to inner key (to_char)
                        #    to relative frequencies
                        if from_substr in from_substr_freqs[t].keys():
                            # print('found one')
                            from_substr_freqs[t][from_substr] = from_substr_freqs[t][from_substr] + frequency
                        elif from_substr is not None:
                            from_substr_freqs[t][from_substr] = frequency
                        else:
                            pass

        # in this code block we have iterated through the entire list of words
        # tms[0], ... , tm[3] contain our complete transition matrices
        # subst_freqs[0], ... , subst_freqs[3] contain the total occurrences of all substrings
        #    Note: the sum of subst_freqs[t] may be greater than the sum of word occurrences.
        #          This is because a from_subst can show up more than once in a single word
        # now we're going to normalize these frequencies.
        # The intent is that for any given from_subst, the total frequency of the to_chars will sum to 1
        # This just makes it a lot easier to sample from, since we can use a simple U[0,1] distribution.
        for t in range(4):
            for key in from_substr_freqs[t].keys():
                total_freq = from_substr_freqs[t][key]
                for sub_key in tms[t][key].keys():
                    tms[t][key][sub_key] = tms[t][key][sub_key] / total_freq

        # in this code block we are converting all of our transition matrices from nested dictionaries
        #     into pandas dataframes
        # create a list that will store the dataframes (one per substring length)
        tm_dfs = []
        for t in range(4):
            substr_col = []
            to_char_col = []
            frequency_col = []
            for outer_key in tms[t].keys():
                for inner_key, value in tms[t][outer_key].items():
                    substr_col.append(outer_key)
                    to_char_col.append(inner_key)
                    frequency_col.append(value)
            data = list(zip(substr_col, to_char_col, frequency_col))
            df = pd.DataFrame(data, columns=['from_str', 'to_char', 'rel_frequency'])
            tm_dfs.append(df)

        # write the output as a table
        trans_mat_filenames = [corpus_name + '_tm' + str(t) + '.dat' for t in range(1, 5)]
        for t in range(4):
            trans_mat_path = os.path.join(self.script_dir, 'data', 'trans_mats', trans_mat_filenames[t])
            tm_dfs[t].to_csv(trans_mat_path)


    def run(self):
        print('you ran lexgen')

if __name__ == '__main__':
    lexgen = LexGen()
