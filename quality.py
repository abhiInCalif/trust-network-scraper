__author__ = 'abkhanna'
import re, math
from collections import Counter
from textblob import TextBlob
import nltk
nltk.data.path.append('./nltk_data/')

WORD = re.compile(r'\w+')

class CosineSimilarity:

    def __init__(self):
        pass

    @staticmethod
    def get_cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    @staticmethod
    def text_to_vector(text):
        words = TextBlob(text)
        filter_DT = filter(lambda x: not("DT" in x), words.tags)
        filter_TO = filter(lambda x: not("TO" in x), filter_DT)
        filter_IN = filter(lambda x: not("IN" in x), filter_TO)
        just_terms = map(lambda x: x[0], filter_IN)
        just_terms = map(lambda x: x.replace(".", " "), just_terms)
        just_terms = map(lambda x: x.lower(), just_terms)
        return Counter(just_terms)

    @staticmethod
    def similarity(text1, text2):
        v1 = CosineSimilarity.text_to_vector(text1)
        v2 = CosineSimilarity.text_to_vector(text2)
        similarity_index = CosineSimilarity.get_cosine(v1, v2)
        print "Cosine Similarity: {0}".format(similarity_index)
        return similarity_index
