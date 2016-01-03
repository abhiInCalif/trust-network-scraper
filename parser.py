__author__ = 'abkhanna'
import lxml.html
from textblob import TextBlob
from nltk.tag import pos_tag
from PIL import Image
import nltk
nltk.data.path.append('./nltk_data/')

class Parser:
    def __init__(self):
        pass

    def blacklist(self, link):
        blacklist = ["logo", "types", "facebook", "google", "yahoo", "pinterest", "twitter",
                     "spinner", "gif", "register", "icon", "rss", "iad", "preview", "thumb",
                     "mailto"]
        for bl in blacklist:
            if bl.lower() in link.lower():
                return True
        else:
            return False

    def html_string(self, s):
        return lxml.html.fromstring(s).text_content()

    def parse(self, body):
        # for now keep it simple,
        # grab all the content in the parent of the h1 tag
        # If it seems to be "large" than keep it
        # else grab the h2 tags, find their parents and see how "large" they are.
        # else grab the h3 tags, find their parents and see how "large" they are.
        contentBody = [self.html_string(str(content.find_parent("div"))) for content in body.findAll("h1")]
        contentBody = filter(lambda s: s != 'None', contentBody)
        contentLength = [len(i) for i in contentBody]

        # check if the contentBody from here has enough "substance"
        # simple check for now, see if the size of the data is long enough.
        if sum(contentLength) > 300:
            print "Used H1 to get the body: {0}".format(contentBody)
            return contentBody

        # this is the else case where the data length is not long enough.
        otherBody = [self.html_string(str(content.find_parent("div"))) for content in body.findAll("h3")]
        otherBody = filter(lambda s: s != 'None', contentBody)
        otherLength = [len(i) for i in otherBody]

        if sum(otherLength) > 300:
            print "Used H3 to get the body: {0}".format(otherBody)
            return otherBody

        return contentBody # not enough info, defaults to contentBody

    def dimension_sort_fun(self, image):
        import pdb; pdb.set_trace()
        if image.get("src", "") is not "":
            # we have a valid src
            im = Image.open(image["src"])
            (w, h) = im.size
            return w * h
        else:
            return 1

    def parseImage(self, body):
        # goal of this function is to find out where the image is to show with the
        # text on the app
        images = body.findAll("img")
        filteredImages = []
        for image in images:
            alt_words = TextBlob(image.get("alt", "")).words
            if len(alt_words) == 0:
                continue
            capital_alt_words = map((lambda x: x.capitalize()), alt_words)
            tagged_sent = pos_tag(capital_alt_words)
            propernouns = [word for word, pos in tagged_sent if pos == 'NNP']
            if len(propernouns) == 0:
                continue
            else:
                if not self.blacklist(image.get("src", "")):
                    filteredImages.append(image)

        # sort the filteredImages by the dimensions of the image.
        filteredImages = sorted(filteredImages, key=self.dimension_sort_fun)

        return filteredImages
