import pymongo
from unidecode import unidecode
from config import uri
from datetime import datetime
import time
from geopy.geocoders import Photon

# Connessione al database MongoDB
client = pymongo.MongoClient(uri)
db = client['MongoTicket']
events = db['events']
tickets = db['tickets']

# Crea indice geospaziale
events.create_index([("stage.location", pymongo.GEOSPHERE)])

def search_by_name():
    keyword = input("Inserisci il nome del concerto: ")
    results = events.find({"concert_name": {"$regex": keyword, "$options": "i"}})
    return list(results)

def search_by_artist():
    keyword = input("Inserisci il nome dell'artista: ")
    results = events.find({"artists": {"$regex": keyword, "$options": "i"}})
    return list(results)

# Funzione per ottenere le coordinate di una posizione
def get_coordinates(location_name):
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"Impossibile trovare le coordinate per {location_name}")
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

def search_by_date():
    try:
        start_date = input("Inserisci la data di inizio (YYYY-MM-DD): ")
        end_date = input("Inserisci la data di fine (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        print("Formato data non valido. Usa il formato YYYY-MM-DD.")
        return []

    query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date
        }
    }
    results = events.find(query)
    return list(results)

def generate_ticket(event_id, concert_name, num, name_buyer):
    event = events.find_one({"_id": event_id})
    if event:
        if event['places_available'] < num:
            print("Non ci sono abbastanza posti disponibili.")
        else:
            for i in range(num):
                events.update_one({"_id": event_id}, {"$inc": {"places_available": -1}})
                ticket = {
                    "id_event": event["_id"],
                    "concert_name": event["concert_name"],
                    "buyer_name": name_buyer,
                    "seat_number": event['places_available'] - i
                }
                receipt = tickets.insert_one(ticket)
                print(f"Ticket ID: {receipt.inserted_id}")
            print(f"{num} biglietti generati con successo per {concert_name}")

def clear_screen():
    print("\033[H\033[J", end="")

def avvia_sessione():
    while True:
        clear_screen()
        print("Opzioni disponibili:")
        print("1. Cerca per nome del concerto")
        print("2. Cerca per artista")
        print("3. Cerca per località")
        print("4. Cerca per data")
        print("5. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        if scelta == '1':
            results = search_by_name()
        elif scelta == '2':
            results = search_by_artist()
        elif scelta == '3':
            location_name = input("Inserisci il nome della località: ")
            results = search_by_location(location_name)
        elif scelta == '4':
            results = search_by_date()
        elif scelta == '5':
            print("Grazie per aver usato l'applicazione.")
            break
        else:
            print("Opzione non valida. Riprova.")
            time.sleep(2)
            continue

        if results:
            for i, event in enumerate(results):
                print(f"{i + 1}. {event.get('concert_name', 'N/A')} - Artisti: {event.get('artists', 'N/A')} - Data: {event.get('date', 'N/A')} - Posti disponibili: {event.get('places_available', 'N/A')}")

            try:
                selection = int(input("Seleziona l'evento desiderato inserendo il numero corrispondente: ")) - 1
                if 0 <= selection < len(results):
                    selected_event = results[selection]
                    concert_name = selected_event.get('concert_name', 'N/A')
                    num = int(input(f"Quanti biglietti desideri acquistare per {concert_name}? "))
                    name_buyer = input("Inserisci il nome dell'acquirente: ")
                    generate_ticket(selected_event["_id"], concert_name, num, name_buyer)
                else:
                    print("Selezione non valida.")
            except ValueError:
                print("Errore: inserisci un numero valido.")
        else:
            print("Nessun evento trovato.")

        input("Premi Invio per continuare...")

if __name__ == "__main__":
    avvia_sessione()
