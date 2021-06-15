from locale import Error
from logging import raiseExceptions
from gensim.models import KeyedVectors
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import urllib
import json


kv_fname = 'kowiki-neg-300.kv'
tg_disease_kw = ['독감', '증상'] # target disease keywords
max_word_num = 10 # maximum number of words to search

start_date = '2017-01-02' # monday of 17-1 week 
end_date = '2021-06-06'# monday of 21-22 week

naver_trends_url = 'https://openapi.naver.com/v1/datalab/search' # use naver trends api, 1000 request per day
client_id = 'B4Vmp4Wt5ECl_fNWgIXR' # input your client id
client_secret = 'WnmtyQRoNa' # input your secret key


def request_trends(word):
    '''
    Args:
        word (str): target word
    
    Returns:
        {'period': 'YYYY-MM-DD', 'ratio': XX.XX}
    '''

    body = (f'{{"startDate":"{start_date}","endDate":"{end_date}","timeUnit":"week",' 
                + '"keywordGroups":[{"groupName":"' + word + '","keywords":["' + word + '"]}]}')

    request = urllib.request.Request(naver_trends_url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type","application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))
    rescode = response.getcode()

    if rescode==200:
        resbody = response.read()
        resbody = json.loads(resbody.decode('utf8'))
        return resbody['results'][0]['data']
    else:
        raise Exception(f'request is failed for "{word}", response code: {rescode}')


def fill_zero(trends):
    '''
    Fill empty 'period' with zeros

    Args:
        trends (list): [{'period': '2017-01-02', 'ratio': XX.XX},
                        {'period': '2017-01-16', 'ratio': XX.XX}, ...]

    Returns:
        fz_trends (list): [{'period': '2017-01-02', 'ratio': XX.XX},
                           {'period': '2017-01-09', 'ratio': 0.0},
                           {'period': '2017-01-16', 'ratio': XX.XX}, ...]
    '''
    fz_trends = []
    i = 0
    for date in pd.date_range(start_date, end_date, freq='W-MON').strftime('%Y-%m-%d'):
        if len(trends)==0: # no trends data
            fz_trends.append({'period': date, 'ratio': 0.0})
        else:
            if trends[i]['period']==date:
                fz_trends.append({'period': date, 'ratio': trends[i]['ratio']})
                if i+1 < len(trends): # not last index of trends
                    i += 1
            else: # if there is no target period, fill period with zeros
                fz_trends.append({'period': date, 'ratio': 0.0})
    return fz_trends


def get_trends_csv():
    w2v_kv = KeyedVectors.load(f'./models/{kv_fname}')

    if len(tg_disease_kw)==0:
        raise Error('there are no target disease keywords')
    for tg_word in tg_disease_kw:
        if tg_word not in w2v_kv.key_to_index:
            raise Error(f'{tg_word} is not in vocab of word2vec model')

    related_words = [w for w, _ in w2v_kv.most_similar_cosmul(positive=tg_disease_kw,
                                                              topn=max_word_num)]

    word_trends = {}

    for word in tqdm(related_words):
        try:
            trends = request_trends(word)
            word_trends[word] = fill_zero(trends)
        except Exception as e:
            print(str(e))
            continue
    
    word_trends_df = pd.DataFrame({word: [data['ratio'] for data in trends] 
                                    for word, trends in word_trends.items()})
    word_trends_df.insert(0, 'period', pd.date_range(start_date, end_date, freq='W-MON').strftime('%Y-%m-%d'))
    word_trends_df.to_csv(f'./data/{"+".join(tg_disease_kw)}_word_trends.csv', index=False)


if __name__=='__main__':
    get_trends_csv()

    