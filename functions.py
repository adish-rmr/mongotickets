import pymongo
from unidecode import unidecode
from config import uri

client = pymongo.MongoClient(uri)
db = client['MongoTicket']
events = db['events']
tickets = db['tickets']


def normalize(user_input):
    no_accent = unidecode(user_input)
    keyword = no_accent.lower().replace(" ", "")
    return keyword


def search_by_artist(artist_name):
    keyword = normalize(artist_name)
    query = {"norm_names": {"$regex": keyword}}
    results = events.find(query)
    return list(results)


def search_by_name(event_name):
    keyword = normalize(event_name)
    query = {"norm_names": {"$regex": keyword}}
    results = events.find(query)
    return list(results)



print(search_by_name("fest"))


client.close()

