import pymongo
import os
from datetime import datetime
from config import uri
import time 

# Prova a connetterti al server MongoDB
try:
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000)
    db = client['MongoTicket']
    events = db['events']
    tickets = db['tickets']
    # Tentativo di selezionare il server per verificare la connessione
    client.server_info()
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Errore di connessione a MongoDB: {err}")
    exit(1)

def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:
        os.system('clear')

def format_event(event):
    return (f"Nome: {event['concert_name']}\n"
            f"Artisti: {', '.join(event['artists'])}\n"
            f"Data: {event['date'].strftime('%d/%m/%Y %H:%M')}\n"
            f"Luogo: {event['stage']['name']}\n"
            f"Posti disponibili: {event['places_available']}\n"
            f"Prezzo: {event['price']}€\n")

def search_by_name():
    while True:
        keyword = input("Inserisci il nome del concerto (anche parziale, o 'b' per tornare indietro): ")
        if keyword.lower() == 'b':
            return
        query = {"concert_name": {"$regex": keyword, "$options": "i"}}
        results = list(events.find(query))
        if len(results) == 0:
            print("Nessun risultato trovato.")
        elif len(results) == 1:
            print(format_event(results[0]))
        else:
            for i, result in enumerate(results):
                print(f"{i+1}. {result['concert_name']}")
            try:
                selection = input("Seleziona il concerto (numero, o 'b' per tornare indietro): ")
                if selection.lower() == 'b':
                    return
                selected_event = results[int(selection) - 1]
                print(format_event(selected_event))
            except (ValueError, IndexError):
                print("Selezione non valida.")
        input("\nPremi INVIO per continuare...")
        return

def search_by_artist():
    while True:
        keyword = input("Inserisci il nome dell'artista (anche parziale, o 'b' per tornare indietro): ")
        if keyword.lower() == 'b':
            return
        query = {"artists": {"$regex": keyword, "$options": "i"}}
        results = list(events.find(query))
        if len(results) == 0:
            print("Nessun risultato trovato.")
        elif len(results) == 1:
            print(format_event(results[0]))
        else:
            for i, result in enumerate(results):
                print(f"{i+1}. {result['concert_name']} - {', '.join(result['artists'])}")
            try:
                selection = input("Seleziona il concerto (numero, o 'b' per tornare indietro): ")
                if selection.lower() == 'b':
                    return
                selected_event = results[int(selection) - 1]
                print(format_event(selected_event))
            except (ValueError, IndexError):
                print("Selezione non valida.")
        input("\nPremi INVIO per continuare...")
        return

def generate_ticket():
    while True:
        keyword = input("Inserisci il nome del concerto (anche parziale, o 'b' per tornare indietro): ")
        if keyword.lower() == 'b':
            return
        query = {"concert_name": {"$regex": keyword, "$options": "i"}}
        results = list(events.find(query))
        if len(results) == 0:
            print("Nessun risultato trovato.")
            continue
        elif len(results) == 1:
            selected_event = results[0]
        else:
            for i, result in enumerate(results):
                print(f"{i+1}. {result['concert_name']}")
            try:
                selection = input("Seleziona il concerto (numero, o 'b' per tornare indietro): ")
                if selection.lower() == 'b':
                    return
                selected_event = results[int(selection) - 1]
            except (ValueError, IndexError):
                print("Selezione non valida.")
                continue
        
        print(format_event(selected_event))
        
        num = input("Inserisci il numero di biglietti (o 'b' per tornare indietro): ")
        if num.lower() == 'b':
            return
        try:
            num = int(num)
        except ValueError:
            print("Inserisci un numero valido.")
            continue
        name_buyer = input("Inserisci il nome dell'acquirente (o 'b' per tornare indietro): ")
        if name_buyer.lower() == 'b':
            return

        if selected_event['places_available'] < num:
            print("Numero di biglietti richiesti non disponibile.")
            return

        for i in range(num):
            events.update_one({"_id": selected_event["_id"]}, {"$inc": {"places_available": -1}})
            ticket = {"id_event": selected_event["_id"],
                      "concert_name": selected_event["concert_name"],
                      "buyer_name": name_buyer,
                      "seat_number": selected_event['places_available'] - i}
            receipt = tickets.insert_one(ticket)
            print(f"Biglietto emesso: ID {receipt.inserted_id}, Posto {ticket['seat_number']}")

        print("Biglietti generati con successo.")
        return

def search_geo():
    while True:
        lat = input("Inserisci la latitudine (o 'b' per tornare indietro): ")
        if lat.lower() == 'b':
            return
        lon = input("Inserisci la longitudine (o 'b' per tornare indietro): ")
        if lon.lower() == 'b':
            return
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            print("Inserisci coordinate valide.")
            continue
        events_nearby = events.aggregate([
            {'$match': {
                'location.geo': {
                    '$geoWithin': {
                        '$centerSphere': [[lon, lat], 7000 / 6378100]}
                }}}])
        found_results = False
        for event in events_nearby:
            print(format_event(event))
            found_results = True
        if not found_results:
            print("Nessun evento trovato nelle vicinanze.")
        input("\nPremi INVIO per continuare...")
        return

def search_by_date():
    while True:
        date_from = input("Inserisci la data di inizio (formato: AAAA-MM-GG, o 'b' per tornare indietro): ")
        if date_from.lower() == 'b':
            return
        date_to = input("Inserisci la data di fine (formato: AAAA-MM-GG, o 'b' per tornare indietro): ")
        if date_to.lower() == 'b':
            return
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            print("Inserisci una data valida nel formato AAAA-MM-GG.")
            continue
        query = {
            "date": {
                "$gte": date_from,
                "$lt": date_to
            }
        }
        results = events.find(query)
        found_results = False
        for result in results:
            print(format_event(result))
            found_results = True
        if not found_results:
            print("Nessun evento trovato nell'intervallo di date specificato.")
        input("\nPremi INVIO per continuare...")
        return

def avvia_sessione():
    while True:
        clear_screen()
        print("Opzioni disponibili:")
        print("1. Cerca per nome del concerto")
        print("2. Cerca per artista")
        print("3. Genera biglietti")
        print("4. Cerca per coordinate geografiche")
        print("5. Cerca per data")
        print("6. Esci")
        scelta = input("Inserisci il numero dell'opzione desiderata: ")

        if scelta == '1':
            search_by_name()

        elif scelta == '2':
            search_by_artist()

        elif scelta == '3':
            generate_ticket()

        elif scelta == '4':
            search_geo()

        elif scelta == '5':
            search_by_date()

        elif scelta == '6':
            print("Grazie per aver usato l'applicazione.")
            break

        else:
            print("Opzione non valida. Riprova.")
            time.sleep(2)
if __name__ == "__main__":
    avvia_sessione()
