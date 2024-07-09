from geopy.geocoders import Photon
import pymongo
from unidecode import unidecode
from config import uri
import uuid 

# Connessione al database MongoDB
client = pymongo.MongoClient(uri)
db = client['MongoTicket']
events = db['events']
tickets = db['tickets']

def generate_ticket(concert_name, num):
    event = events.find_one({"concert_name": concert_name})
    if event:
        if event['places_available'] <= 0:
            return False
        else:
            while num >0:
                events.update_one({"concert_name": concert_name},
                                  {"$inc": {"places_available": -1}})
                ticket = {"concert_name": concert_name,
                          "seat_number": event['places_available']-num}
                receipt = tickets.insert_one(ticket)
                num -= 1
                print(f"Ticket ID: {receipt.inserted_id}")
            return True
