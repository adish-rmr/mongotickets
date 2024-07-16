import pymongo
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
def search_by_name(keyword):
    return list(events.find({"concert_name": {"$regex": keyword, "$options": "i"}}))


def search_by_artist(keyword):
    return list(events.find({"artists": {"$regex": keyword, "$options": "i"}}))


def search_by_date(start_date,end_date):
    query = {
        "date": {
            "$gte": start_date,
            "$lt": end_date
        }
    }
    return list(events.find(query))


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


def generate_ticket(event, num, name_buyer):
    if event:
        if event['places_available'] < num:
            print("Non ci sono abbastanza posti disponibili.")
        else:
            for i in range(num):
                events.update_one({"_id": event['_id']}, {"$inc": {"places_available": -1}})
                ticket = {
                    "id_event": event["_id"],
                    "concert_name": event["concert_name"],
                    "buyer_name": name_buyer,
                    "seat_number": event['places_available'] - i,
                    "price": event['price']
                }
                receipt = tickets.insert_one(ticket)
                print(f"Ticket ID: {receipt.inserted_id}")
            print(f"{num} biglietti generati con successo per {event['concert_name']}")
    else:
        return None



def display_events(results):
    for i, event in enumerate(results):
        print(f"{i + 1}. {event['concert_name']} \n"
              f"Artisti: {event['artists']} \n"
              f"Data: {event['date']} \n"
              f"Posti disponibili: {event['places_available']} \n"
              f"Prezzo: €{event['price']} \n")


def ticket_cost(event, num):
    price_per_ticket = event['price']
    total_cost = num * price_per_ticket
    return total_cost


# CLI
def avvia_sessione():
    while True:
        print("Opzioni disponibili:")
        print("1. Cerca per nome del concerto")
        print("2. Cerca per artista")
        print("3. Cerca per località")
        print("4. Cerca per data")
        print("5. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        results = None

        if scelta == '1':
            keyword = input("Inserisci il nome del concerto: ")
            if keyword.lower() == 'q' or len(keyword) == 0 or len(keyword) > 30:
                pass
            else:
                results = search_by_name(keyword)

        elif scelta == '2':
            keyword = input("Inserisci il nome dell'artista: ")
            if keyword.lower() == 'q' or len(keyword) == 0 or len(keyword) > 30:
                pass
            else:
                results = search_by_artist(keyword)

        elif scelta == '3':
            location_name = input("Inserisci il nome della località: ")
            if location_name.lower() == 'q' or len(location_name) == 0 or len(location_name) > 30 or len(location_name) < 3:
                pass
            else:
                results = search_by_location(location_name)

        elif scelta == '4':
            try:
                start_date = input("Inserisci la data di inizio (YYYY-MM-DD) (o 'q' per tornare indietro): ")
                end_date = input("Inserisci la data di fine (YYYY-MM-DD) (o 'q' per tornare indietro): ")
                if 2023 < int(start_date[:4]) < 2031 and 0 < int(start_date[5:7]) < 13 and 0 < int(start_date[8:10]) < 32:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                    if 2023 < int(end_date[:4]) < 2031 and 0 < int(end_date[5:7]) < 13 and 0 < int(end_date[8:10]) < 32:
                        end_date = datetime.strptime(end_date, "%Y-%m-%d")
                        if end_date > start_date:
                            results = search_by_date(start_date, end_date)
                        else:
                            print("Errore: La data di fine non può essere precedente alla data di inizio.")
                            pass
                    else:
                        pass
                else:
                    pass
            except ValueError:
                print("Formato data non valido. Usa il formato YYYY-MM-DD.")
                pass

        elif scelta == '5':
            print("Grazie per aver usato l'applicazione.")
            break
        else:
            print("Opzione non valida. Riprova.")
            time.sleep(1)
            continue

        if results:
            display_events(results)
            selection = int(input("Seleziona l'evento desiderato inserendo il numero corrispondente: "))
            if 1 <= selection <= len(results):
                selection -= 1
                selected_event = results[selection]
                if selected_event:
                    num = int(input(f"Quanti biglietti desideri acquistare per l'evento? "))
                    if num > 0 and isinstance(num, int):
                        total_cost = ticket_cost(selected_event, num)
                        print(f"Il costo totale è di €{total_cost:.2f}")
                        confirm = input("Vuoi procedere con l'acquisto? (s/n): ").lower()
                        if confirm == 's' or confirm == 'S':
                            name_buyer = input("Inserisci il nome dell'acquirente: ")
                            if name_buyer.lower() != 'q' and len(name_buyer) > 0:
                                generate_ticket(selected_event, num, name_buyer)
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
        elif results is not None:
            print("Nessun evento trovato.")


if __name__ == "__main__":
    avvia_sessione()
