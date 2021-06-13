from xml.etree import ElementTree as ET
from konlpy.tag import Mecab
import re
import tqdm

wiki_fname = 'kowiki-latest-pages-articles.xml'
mecab = Mecab()

def clean_text(text):    
    # Common
    text = re.sub("(?s)<ref>.+?</ref>", "", text) # remove reference links
    text = re.sub("(?s)<[^>]+>", "", text) # remove html tags
    text = re.sub("&[a-z]+;", "", text) # remove html entities
    text = re.sub("(?s){{.+?}}", "", text) # remove markup tags
    text = re.sub("(?s){.+?}", "", text) # remove markup tags
    text = re.sub("(?s)\[\[([^]]+\|)", "", text) # remove link target strings
    text = re.sub("(?s)\[\[([^]]+\:.+?]])", "", text) # remove media links
    
    text = re.sub("[']{5}", "", text) # remove italic+bold symbols
    text = re.sub("[']{3}", "", text) # remove bold symbols
    text = re.sub("[']{2}", "", text) # remove italic symbols
    
    text = re.sub(u"[^\s\r\n가-힣.?!]", " ", text) # Replace unacceptable characters with a space.
    text = re.sub('([.?!]){2,}', '\\1', text) # remove repeated punctuation
    text = re.sub('\s[.?!]\s', '', text) # remove isolated punctuation
    
    # Common
    text = re.sub("\s{2,}", " ", text) # Squeeze spaces.
    return text


def sentence_segment(text):
    '''
    Args:
      text: A string. A unsegmented paragraph.
    
    Returns:
      A list of sentences.
    '''
    return re.split('([.?!])?[\n]+|[.?!] ', text)


def word_segment(sent):
    return [word for word, _ in mecab.pos(sent)]


def build_corpus():
    ns = '{http://www.mediawiki.org/xml/export-0.10/}' # namespace
    with open(f'./data/{wiki_fname.split("-")[0]}_corpus.txt', 'w', encoding='utf-8') as fout:
        for i, (_, elem) in tqdm(enumerate(ET.iterparse(f'./data/{wiki_fname}'))):
            try:
                tag = elem.tag.replace(ns, '')
                if tag == 'text':
                    running_text = clean_text(elem.text)
                    sents = sentence_segment(running_text)
                    for sent in sents:
                        if sent:
                            words = word_segment(sent)
                            if len(words) > 10:
                                fout.write(' '.join(words) + '\n')
            except:
                continue
            elem.clear()


if __name__=='__main__':
    build_corpus()
    print('Done')