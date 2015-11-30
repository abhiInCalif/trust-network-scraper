__author__ = 'abkhanna'

from pymongo import MongoClient

def database():
    client = MongoClient("mongodb://heroku_pw3tw66l:f6u3bvhehp4es6u4emoo23snol@ds035137.mongolab.com:35137/heroku_pw3tw66l")
    db = client.heroku_pw3tw66l
    return db

class Record:
    @staticmethod
    def create(vector, classification):
        # given the vector and the classification, store the doc
        doc = {
            "vector": vector,
            "class": classification
        }
        database().Record.insert_one(doc)

    @staticmethod
    def fetch(limit=-1):
        if limit < 0:
            # return all of them!
            return database().Record.find()
        else:
            retArray = []
            i = 0
            records = database().Record.find()
            for record in records:
                if i < limit:
                    retArray.append(record)
                    i += 1

