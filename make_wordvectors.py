from gensim.models import Word2Vec

min_count = 5
window_size = 5
num_neg = 15
vector_size = 300

def make_wordvectors():
    print('Making sentences as list...')
    sents = []
    corpus_fname = 'kowiki_corpus.txt'

    with open(f'./data/{corpus_fname}', 'r', encoding='utf8') as fin:
        line = fin.readline()
        while line:
            words = line.split()
            sents.apend(words)
            line = fin.readline()

    print('Making word vectors')
    model = Word2Vec(sents, vector_size=vector_size, min_count=min_count, 
                    negative=num_neg, window=window_size)
    model.save('./models/kowiki-neg-300.bin') # model save
    model.wv.save('./models/kowiki-neg-300.kv') # keyvector save


if __name__=='__main__':
    make_wordvectors()
    print('Done')

