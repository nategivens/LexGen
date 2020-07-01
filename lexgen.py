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
        tot_freqs = [{} for i in range(4)]
        # tot_freq is a dictionary with structure as follows:
        # key: the prefix
        # value: cumulative frequency for all transitions

        # read in all of the prefixes, suffixes, and frequencies
        with open(corpus_file_path, 'r') as c_file:
            for line in c_file:
                tokens = line.split(sep=' ')
                word = tokens[0].strip()
                print('word is: {0}'.format(word))
                frequency = int(tokens[1])
                print('frequency is: {0}'.format(str(frequency)))
                word = ' ' + word + ' '
                for i in range(1, len(word)):
                    to_char = word[i]
                    print('to_char is: {0}'.format(to_char))
                    for t in range(4):
                        from_substr = word[i-t-1:i] if i > t else None
                        if t == 0:
                            print('for i = {0}, t = {1} from_substr is: {2}'.format(str(i), str(t), from_substr))
                        if from_substr in tms[t].values() and from_substr is not None:
                            if to_char in tms[t][from_substr].values():
                                tms[t][from_substr][to_char] = tms[t][from_substr][to_char] + frequency
                            else:
                                tms[t][from_substr][to_char] = frequency
                        else:
                            tms[t][from_substr] = {}
                            tms[t][from_substr][to_char] = frequency
                        if from_substr in tot_freqs[t].values():
                            tot_freqs[t][from_substr] = tot_freqs[t][from_substr] + frequency
                        else:
                            tot_freqs[t][from_substr] = frequency

        print(tms[0].values())

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
