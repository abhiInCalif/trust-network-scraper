__author__ = 'abkhanna'

from bs4 import BeautifulSoup
from urllib2 import urlopen
import pysolr
import time
import threading
import urlparse
import sys, traceback
import requests
import lxml.html
from parser import Parser
from quality import CosineSimilarity
from mlfilters import NearestNeighborFilter
from textblob import Word
import nltk
nltk.data.path.append('./nltk_data/')

BASE_URL = "http://www.bing.com/search?q=ovarian+cancer+survivor+stories"
QUERY_BASE = "ovarian+cancer+survivor+stories"
GOLD_STD = "My story: When I was diagnosed with ovarian cancer in July 2007, all I could think of was my family. " \
           "They are my life, my reason to live. I love them all so much. My children lost their father at a young " \
           "age and I couldnt bear the thought that theyd lose me too. And my grandchildren, " \
           "how could I leave them? And Jon, the love of my life, my husband of only nine years. " \
           "We have a whole lifetime of anniversaries left to celebrate. But by the grace of God, my wonderful " \
           "family and friends, awesome doctors and a fabulous hospital, I am here to tell my story. From diagnosis " \
           "through treatment. For about a year, I had been having lower back pain. It was uncomfortable, but I assumed " \
           "it was nothing more than arthritis. I knew something was not right though when intercourse became painful. " \
           "I went to see my gynecologist, who did an ultrasound on me. The test revealed a large cyst or tumor on one " \
           "of my ovaries. I had surgery to remove the tumor and my ovaries at a local hospital. An oncologist confirmed" \
           " it was ovarian cancer. He spoke with Jon and me about additional treatment and mentioned the typical " \
           "survival rates for the disease. But I wasnt happy with his approach or the set up at the cancer facility." \
           "After a few weeks went by, I became more depressed. I also had developed an oral/throat infection from the " \
           "antibiotics I took as I recovered from the surgery. I needed a doctor who would pay attention to everything " \
           "that was going on with me. Thankfully, when I found Cancer Treatment Centers of America (CTCA), I got a " \
           "doctor who took care of all of me and was experienced in treating my disease. On my first visit to CTCA at " \
           "Midwestern Regional Medical in northern Illinois, I met with Dr. Williams, my gynecologic oncologist. " \
           "She told us before she would treat me for the cancer we needed to figure out what was going on with my " \
           "throat and why I felt as though I wanted to vomit all the time. Dr. Williams used a scope to examine my " \
           "mouth and throat, and thereby discovered I had an infection known as thrush. She treated me for the thrush " \
           "and then proposed an ovarian cancer treatment plan, which included chemotherapy. For about a year, the cancer " \
           "went into remission after I received the chemotherapy treatment. I then underwent surgery to remove new tumors " \
           "that had developed in my abdomen. During the surgery, I also received hyperthermic intraperitoneal chemotherapy " \
           "(HIPEC), a heated chemotherapy that was delivered directly to my abdomen. Dr. Brown, who is the head of the " \
           "HIPEC program at CTCA, performed the procedures.The surgery took approximately six hours and was invasive, " \
           "but my body seemed to tolerate the chemotherapy and I healed well.As part of a clinical trial I participated " \
           "in, tumors that were removed in my surgery were sent to a laboratory to be developed into a vaccine. " \
           "It took some time for the vaccine to be prepared. Once it was ready, I received three injections containing " \
           "the vaccine over a seven-week period. For the next few years, I received additional chemotherapy treatment. " \
           "In 2011, I had my third surgery. I also received radiation therapy. I did experience back issues and upset " \
           "bowels as side effects from the radiation. Overall, though, Ive been able to cope. Whenever I needed to go " \
           "to CTCA for treatment or appointments, I would call the travel/scheduling team to set up arrangements. " \
           "Theyd coordinate my flights to and from Flint, Michigan (the big city nearest my home in Lapeer) and " \
           "Chicago. A driver would pick me up from OHare airport in Chicago and take me to CTCA or its nearby Guest " \
           "Quarters, where Id stay whenever I was in town. My favorite driver, Jim, gave the best bear hugs and allowed" \
           " me to sit in the front seat and chat with him on the way to the hospital. Jim always cares how people are " \
           "feeling. He also takes it upon himself to get to know the family and friends who come along with patients." \
           "Everybody cares about me at CTCA from Jim, to the people behind the scenes in the cafeteria, to the doctors" \
           "and nurses in the surgical suites. They have all touched my life. I am especially grateful for Dr. Williams" \
           "and Dr. Brown for never giving up on me. Both doctors go out of their way to make me feel comfortable." \
           "And, they talk to me like Im their only patient. In 2012, I became a five-year survivor of ovarian cancer." \
           "My name now appears on a gold leaf on the Tree of Life in the hospitals lobby. Whenever Im there, I" \
           "stop and touch my leaf and feel so blessed to have been able to come to CTCA. I get goose bumps thinking" \
           "of how I got my second chance at life, a chance I will never take lightly or for granted. Filled with hope" \
           "My family, friends and CTCA gave me the strength to lift my arms to the sky and say, Im alive and I have" \
           "hope for the future. What a beautiful gift, my life. I can get out of bed in the morning and go to work." \
           "I can sleep in on the weekends. I can smell the flowers and the grass being mowed. I can be with family" \
           "and friends, and I can laugh with my grandchildren. I thank God every day for the gift of life he has" \
           "given me. I hope and pray it is his wish that my life continues for a very long time. When it does" \
           "come to an end, I want people to know I did fight the fight, and I did win. I am in a win-win situation" \
           "and I will continue my fight. I want to reach out and help every person I can. That includes talking to" \
           "family members and being there for them. I want to teach others not only to keep hoping, but to have" \
           "strength and will power to want to go on and live."

# noinspection PyMethodMayBeStatic
class Scraper:
    def __init__(self):
        self.links = []
        pass

    def query_expansion(self, query):
        # this function takes in the query and expands it using wordnet
        print "start query_expansion"
        split_query = query.split("+")
        list_of_synset_sets = []
        for term in split_query:
            synsets = Word(term).synsets
            print "synsets reached"
            syn_names = map(lambda x: x.lemma_names(), synsets)
            flat_syn_names = reduce(lambda acc, x: acc + x, syn_names)
            flat_syn_names = reduce(lambda acc, x: acc if x in acc else acc + [x], flat_syn_names, [])
            list_of_synset_sets.append(flat_syn_names)

        # should be a list of names at this point.
        # now you can build_combinations out of it.
        all_combinations = self.build_combinations(list_of_synset_sets[0], list_of_synset_sets[1:])
        print "end query_expansion"
        print "combinations: {0}".format(all_combinations)
        return all_combinations

    def build_combinations(self, hd, tail):
        if len(tail) == 1:
            # base case
            export_list = []
            for a in hd:
                export_list.extend(map(lambda x: a + "+" + x, tail[0]))
            return export_list
        else:
            # recurring case
            export_list = []
            for a in hd:
                export_list.extend(map(lambda x: a + "+" + x, self.build_combinations(tail[0], tail[1:])))
            return export_list


    def get_bing_links(self, pg):
        print "Getting bing links for page: {0}".format(pg)
        first = (pg - 1) * 14
        html = urlopen(BASE_URL + "&first=" + str(first)).read()
        soup = BeautifulSoup(html, "lxml")
        linkSection = soup.find("ol")
        category_links = [li.h2.a["href"] for li in linkSection.findAll("li", "b_algo")]

        # query expand, grab the links on the other pages as well
        query_combinations = self.query_expansion(QUERY_BASE)
        query_expanded_links = map(lambda x: "http://www.bing.com/search?q=" + x, query_combinations)

        for link in query_expanded_links:
            time.sleep(10)
            print "Grabbing next link {0}".format(link)
            html = urlopen(link + "&first=" + str(first)).read()
            soup = BeautifulSoup(html, "lxml")
            linkSection = soup.find("ol")
            category_links.extend([li.h2.a["href"] for li in linkSection.findAll("li", "b_algo")])

        print "Bing links {0}".format(category_links)
        return category_links

    def make_links_absolute(self, soup, url):
        for tag in soup.findAll('a', href=True):
            tag['href'] = urlparse.urljoin(url, tag['href'])

        for tag in soup.findAll('img', src=True):
            tag['src'] = urlparse.urljoin(url, tag['src'])

    def extract_links(self, body):
        try:
            link_list = [l["href"] for l in body.findAll("a")]
            filtered_list = filter(lambda lnk: not (Parser()).blacklist(lnk), link_list)
            return filtered_list
        except:
            print "Unexpected error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            return []

    # noinspection PyBroadException
    def get_content_from_pages(self, link):
        # method will be used to scrape and index each of the links we scrape from bing
        # and put into the scraper so that we can rank the files and mark them as relevant.
        try:
            html = urlopen(link).read()
            # TODO - Fix this to be the line above.
            # html = urlopen("https://en.wikipedia.org/wiki/Malignant_neoplastic_disease").read()
            soup = BeautifulSoup(html, "lxml")
            self.make_links_absolute(soup, link)
            body = soup.html.body
            title = lxml.html.fromstring(str(soup.html.title)).text_content()

            # grab the links from the page and add them to links to explore
            contentLinks = self.extract_links(body)
            print "Getting content links from pages {0}".format(str(contentLinks))
            for l in contentLinks:
                if l not in self.links:
                    self.links.append(l)

            print "Getting contents from pages {0}".format(link)
            contentBody = (Parser()).parse(body)
            contentImage = (Parser()).parseImage(body)
        except Exception:
            print "Unexpected error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            contentBody = []
            title = ""
            contentImage = []
        return title, contentBody, contentImage

    @staticmethod
    def store_in_solr(link, emotional_score, quality_score, contentTuple):
        try:
            # print "ContentTuple: {0}".format(contentTuple)
            (title, bodyList, image) = contentTuple
            solr = pysolr.Solr('http://52.91.13.38:8983/solr/survivor_stories/', timeout=10)
            solr.add([
                {
                    "id": link,
                    "emotional_score": emotional_score,
                    "quality_score": quality_score,
                    "body": bodyList,
                    "title": title,
                    "picture": image,
                },
            ])
        except:
            print "Unexpected error:", sys.exc_info()[0]

    def get_emotional_score(self, bodyList):
        return 0.5 # for now just return 0.5 till we figure this algorithm out.

    def get_quality_score(self, bodyList):
        # we will measure quality by looking at relevancy and the quality of the writing
        # relevancy will be judged as a normalized score.
        # return reduce(lambda acc, x: acc + CosineSimilarity.similarity(x, GOLD_STD), bodyList, 0)
        cosine_sim_value = reduce(lambda acc, x: acc + CosineSimilarity.similarity(x, GOLD_STD), bodyList, 0)
        nearest_neighbor_class = (NearestNeighborFilter()).classify(CosineSimilarity.text_to_vector(" ".join(bodyList)))
        nearest_neighbor_class = nearest_neighbor_class[0]  # get the actual value.
        # we are going to return a weighted average of the two filters
        print "Combined score: {0}".format(0.58 * cosine_sim_value + 0.42 * nearest_neighbor_class)
        return 0.58 * cosine_sim_value + 0.42 * nearest_neighbor_class
        # return 0.9 # for now just return this as default.

    def run(self, start_page=1, end_page=20):
        # runs the scraper
        for i in range(start_page, end_page):
            time.sleep(10) # sleep for 10 seconds so as not to overload the server
            links = self.get_bing_links(i)
            self.links.extend(links)
            for j in range(0, len(self.links)):
                print "Length of links array: {0}".format(len(self.links))
                link = self.links[j]
                (title, bodyList, imageList) = self.get_content_from_pages(link)
                if title == "" or bodyList == [] or imageList == []:
                    continue
                emotional_score = self.get_emotional_score(bodyList)
                quality_score = self.get_quality_score(bodyList)
                if quality_score > 0.45:
                    # we are going to ship it into the db for human testing
                    data = {
                        'title': title,
                        'url': link,
                        'emotional_score': emotional_score,
                        'quality_score': quality_score,
                        'body': " ".join(bodyList), # kept because I cant get rid of it without breaking something
                        'image': imageList[0].get("src"),
                    }
                    try:
                        requests.post(url="http://" + "trust-network.herokuapp.com" + "/stories/create", data=data)
                    except:
                        pass
                    # Scraper.store_in_solr(link, emotional_score, quality_score, (title, bodyList, imageList))


class ThreadedScraper(threading.Thread):
    def __init__(self, start_page, end_page):
        threading.Thread.__init__(self)
        self.start_page = start_page
        self.end_page = end_page

    def run(self):
        print "Starting " + self.name
        s = Scraper()
        s.run(self.start_page, self.end_page)
        print "Exiting " + self.name

def run_program(start, end):
    t = ThreadedScraper(start, end)
    t1 = ThreadedScraper(end + 1, 2 * end - start + 1)
    t.start()
    # t1.start()

