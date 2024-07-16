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

# Funzioni di ricerca
def search_by_name():
    keyword = input("Inserisci il nome del concerto (o 'q' per tornare indietro): ")
    if keyword.lower() == 'q':
        return None
    return list(events.find({"concert_name": {"$regex": keyword, "$options": "i"}}))

def search_by_artist():
    keyword = input("Inserisci il nome dell'artista (o 'q' per tornare indietro): ")
    if keyword.lower() == 'q':
        return None
    return list(events.find({"artists": {"$regex": keyword, "$options": "i"}}))

def search_by_date():
    try:
        start_date = input("Inserisci la data di inizio (YYYY-MM-DD) (o 'q' per tornare indietro): ")
        if start_date.lower() == 'q':
            return None
        end_date = input("Inserisci la data di fine (YYYY-MM-DD) (o 'q' per tornare indietro): ")
        if end_date.lower() == 'q':
            return None
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end_date < start_date:
            print("Errore: La data di fine non può essere precedente alla data di inizio.")
            return []
    except ValueError:
        print("Formato data non valido. Usa il formato YYYY-MM-DD.")
        return []

    query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date
        }
    }
    return list(events.find(query))

# Funzioni di geolocalizzazione
def get_coordinates(location_name):
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"Impossibile trovare le coordinate per {location_name}")
        return None

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
        results = list(events.find(query))
        print(f"Trovati {len(results)} eventi vicini a {location_name}")
        return results
    else:
        return None

# Funzioni di gestione biglietti
def calculate_total_cost(num_tickets, price_per_ticket):
    return num_tickets * price_per_ticket

def generate_ticket(event_id, concert_name, num, name_buyer, price_per_ticket):
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
                    "seat_number": event['places_available'] - i,
                    "price": price_per_ticket
                }
                receipt = tickets.insert_one(ticket)
                print(f"Ticket ID: {receipt.inserted_id}")
            print(f"{num} biglietti generati con successo per {concert_name}")

# Funzioni di utilità
def clear_screen():
    print("\033[H\033[J", end="")

def display_events(results):
    for i, event in enumerate(results):
        print(f"{i + 1}. {event.get('concert_name', 'N/A')} - Artisti: {event.get('artists', 'N/A')} - Data: {event.get('date', 'N/A')} - Posti disponibili: {event.get('places_available', 'N/A')} - Prezzo: €{event.get('price', 'N/A')}")

def process_event_selection(results):
    try:
        selection = input("Seleziona l'evento desiderato inserendo il numero corrispondente (o 'q' per tornare indietro): ")
        if selection.lower() == 'q':
            return None
        selection = int(selection) - 1
        if 0 <= selection < len(results):
            return results[selection]
        else:
            print("Selezione non valida.")
            return None
    except ValueError:
        print("Errore: inserisci un numero valido.")
        return None

def process_ticket_purchase(event):
    concert_name = event.get('concert_name', 'N/A')
    num = int(input(f"Quanti biglietti desideri acquistare per {concert_name}? "))
    price_per_ticket = event.get('price', 0)
    total_cost = calculate_total_cost(num, price_per_ticket)
    print(f"Il costo totale è di €{total_cost:.2f}")
    confirm = input("Vuoi procedere con l'acquisto? (s/n): ").lower()
    if confirm != 's':
        print("Acquisto annullato.")
        return
    name_buyer = input("Inserisci il nome dell'acquirente: ")
    generate_ticket(event["_id"], concert_name, num, name_buyer, price_per_ticket)

# Funzione principale
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

        results = None
        if scelta == '1':
            results = search_by_name()
        elif scelta == '2':
            results = search_by_artist()
        elif scelta == '3':
            location_name = input("Inserisci il nome della località (o 'q' per tornare indietro): ")
            if location_name.lower() != 'q':
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
            display_events(results)
            selected_event = process_event_selection(results)
            if selected_event:
                process_ticket_purchase(selected_event)
        elif results is not None:
            print("Nessun evento trovato.")

        input("Premi Invio per continuare...")

if __name__ == "__main__":
    avvia_sessione()
