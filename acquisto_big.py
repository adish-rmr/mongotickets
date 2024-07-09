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

# Funzione per generare un biglietto
def generate_ticket(concert_name):
    event = events.find_one({"concert_name": concert_name})  # Trova il concerto nel DB
    if not event:
        return "Concerto non trovato"
    else:
        if event['places_available'] <= 0:
            return "Biglietti esauriti"
        else:
            ticket_id = str(uuid.uuid4()) # uuid serve per generare un ID univoco per ogni biglietto
            ticket = {"ticket_id": ticket_id, "concert_name": concert_name, "seat_number": event['places_available']}
            
            tickets.insert_one(ticket)  # Inserisci il biglietto nel database
            events.update_one({"concert_name": concert_name}, {"$inc": {"places_available": -1}})  # Aggiorna i posti disponibili nel concerto
            return ticket
