import pandas as pd
import os
import itertools
from datetime import datetime

class LexGen:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

        self.lang_dict = self.read_lang_dict()
        # this is a df with cols = [lang_code, lang_name]
        # later, this will become reading the languages table
        self.corpora = self.scan_corpora()
        # this is df with cols = [corpus_name, corpus_filepath]
        # later, this will become reading the corpora table
        self.trans_mats = self.scan_trans_mats()
        # this is a dataframe with cols = [corpus_name, prefix_len, trans_matrix_filepath]
        # later, this will become reading the transition_matrices table

    def read_lang_dict(self):
        # check to see if file exists
        # check to see if columns exist (and not extra columns)
        # check to see if data exists (rows > 0)
        # check to see if datatypes are valid (alphabetic strings, non-numeric)
        abs_fname = os.path.join(self.script_dir, 'data', 'ref', 'lang_ref.dat')
        return pd.read_csv(abs_fname)

    def scan_corpora(self):
        # read all files in data/corpora subfolder of current directory
        corpora_path = os.path.join(self.script_dir, 'data', 'corpora')
        # the .rsplit('.', 1)[0] drops the file extension
        corpora_files = [f.rsplit('.', 1)[0] for f in os.listdir(corpora_path) if os.path.isfile(os.path.join(corpora_path, f))]
        corpora_indiv_paths = [os.path.join(corpora_path, p + '.dat') for p in corpora_files]
        return pd.DataFrame(list(zip(corpora_files, corpora_indiv_paths)), columns=['corpus_name', 'corpus_filepath'])

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

        return trans_mat_df

    def load_corpus(self, corpus_name, corpus_file):
        # read in the corpus line by line
        # first string is word, second string (if exists) is frequency
        # get unique list of words with frequency
        # write output to file: /data/corpora/{corpus_name}.dat
        pass

    def refresh_trans_mats(self):
        # iterate over self.trans_mats
        # call create_trans_mat for every row where last_updated = None
        # update last_updated as you go
        pass

    def create_trans_mat(self, corpus_name, corpus_file, trans_mat_file, prefix_len):
        # trans_mat is a nested dictionary with structure as follows:
        # Outer Dictionary key: the prefix
        # Outer Dictionary value: the Inner Dictionary
        # Inner Dictinoary key: the suffix
        # Inner Dictionary key: the frequency of transitioning to that suffix given the prefix (Outer Dictionary key)

        # tot_freq is a dictionary with structure as follows:
        # Outer Dictionary key: the prefix
        # Inner Dictionary key: cumulative frequency for all transitions

        # read in all of the prefixes, suffixes, and frequencies
        # for each line in a corpus
            # read the word and pad with a whitespace before and after
            # for each prefix in the word (prefix is a substring of length = prefix_len, don't include the last one)
                # trans_mat[prefix][suffix] += frequency
                # tot_freq[prefix] += frequency

        # convert all of the frequencies to relative frequency
        # IS THIS STEP NECESSARY?
        # for each key in Outer Dictionary
            # prefix_freq = 0
            # for each key in Inner Dictionary
                # trans_mat[prefix][suffix] = trans_mat[prefix][prefix] / tot_freq[prefix]

        # write the output as a table:
        # prefix | suffix | rel_trans_freq
        # trans_mat_path = os.path.join(self.script_dir, 'data', 'trans_mats', trans_mat_file + '.dat')
        pass

    def run(self):
        print('you ran lexgen')

if __name__ == '__main__':
    lexgen = LexGen()
