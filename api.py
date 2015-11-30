__author__ = 'abkhanna'
import web
from scraper import Scraper
import Store
from quality import CosineSimilarity

urls = (
    '/accept/story', 'AcceptHumanMarkAndUpdateConstants',
)

class AcceptHumanMarkAndUpdateConstants:
    def __init__(self):
        pass

    def POST(self):
        # accepts the human marked form
        # takes the YES/NO signal and if YES sends to Solr
        # either way uses the YES/NO to train another epoch of the
        # machine learning algorithm. The constants will be stored in
        # the database.
        web.header('Content-type', 'application/json')
        request_input = web.input(answer='', url='', title='', image='', emotional_score=-1, quality_score=-1, body='')
        url = request_input.url
        title = request_input.title
        image = request_input.image
        emotional_score = request_input.emotional_score
        quality_score = request_input.quality_score
        body = request_input.body
        answer = request_input.answer
        if answer == '' or url == '' or title == '' or image == '' or emotional_score == -1 or quality_score == -1 or body == '':
            return web.badrequest()

        if "yes" == answer:
            Store.Record.create(CosineSimilarity.text_to_vector(body), 1)
            Scraper.store_in_solr(url, emotional_score, quality_score, (title, body, image))
        else:
            Store.Record.create(CosineSimilarity.text_to_vector(body), 0)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
