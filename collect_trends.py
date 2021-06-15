from locale import Error
from gensim.models import KeyedVectors
from pytrends.request import TrendReq
from tqdm import tqdm
import pandas as pd
import time


kv_fname = 'kowiki-neg-300.kv'
tg_disease_kw = ['독감', '증상'] # target disease keywords
max_word_num = 10 # maximum number of words to search

start_date = '2017-01-01' # sunday of 17-1 week 
end_date = '2021-06-05'#  saturday of 21-22 week

pyt = TrendReq(hl='ko-KR') # language code for korea


def request_trends(keywords):
    '''
    Args:
        keywords (list): [w1, w2, ...] keywords for query
    
    Returns:
        pandas.DataFrame: {w1: [...], w2: [...], ...}
    '''

    pyt.build_payload(keywords, timeframe=f'{start_date} {end_date}', geo='KR') # request
    trends = pyt.interest_over_time() # search rate for keywords
    trends.pop('isPartial') # ignore "isPartial" column
    return trends


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_trends_csv():
    print('load keyvector of model...')
    w2v_kv = KeyedVectors.load(f'./models/{kv_fname}')

    if len(tg_disease_kw)==0:
        raise Error('there are no target disease keywords')
    for tg_word in tg_disease_kw:
        if tg_word not in w2v_kv.key_to_index:
            raise Error(f'{tg_word} is not in vocab of word2vec model')

    related_words = ['독감'] + [w for w, _ in w2v_kv.most_similar_cosmul(positive=tg_disease_kw,
                                                                         topn=max_word_num)]

    trends = None
    for keywords in tqdm(chunks(related_words, 5)):
        try:
            trends = pd.concat([trends, request_trends(keywords)], axis=1) # concat horizontally
            trends.to_csv(f'./data/{"+".join(tg_disease_kw)}_google_trends.csv') # Can be blocked by google limit rate, so save every time 
            time.sleep(5) # interval to prevent google limit rate 
        except Exception as e:
            print(f'{keywords} request is failed', str(e))
            break

    
if __name__=='__main__':
    get_trends_csv()
    print('Done')

    