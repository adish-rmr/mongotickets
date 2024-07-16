from geopy.geocoders import Photon
import pymongo
from unidecode import unidecode
from config import uri


# Connessione al database MongoDB
client = pymongo.MongoClient(uri)
db = client['MongoTicket']
events = db['events']
tickets = db['tickets']

# Crea indice geospaziale
events.create_index([("stage.location", pymongo.GEOSPHERE)])

# Funzione per ottenere le coordinate di una posizione
def get_coordinates(location_name):
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"Impossibile trovare le coordinate per {location_name}")  # Debug
        return None

# Funzione per cercare eventi vicini basati sulle coordinate
def search_by_location(location_name):
    coordinates = get_coordinates(location_name)
    if coordinates:
        lat, long = coordinates
        query = {
            "stage.location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lat, long]
                    },
                    "$maxDistance": 100000  # 100 km
                }
            }
        }
        results = events.find(query)
        results_list = list(results)
        print(f"Trovati {len(results_list)} eventi vicini a {location_name}")  # Debug
        return results_list
    else:
        return []
    
location_name = "Milano"
events_nearby = search_by_location(location_name)

for event in events_nearby:
    print(f"Evento: {event.get('concert_name', 'N/A')}")



 

