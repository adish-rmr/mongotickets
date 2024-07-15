# MongoTicket

MongoTicket è un'applicazione Python per la gestione e la prenotazione di biglietti per eventi musicali, utilizzando MongoDB come database.

## Caratteristiche

- Ricerca eventi per nome del concerto
- Ricerca eventi per artista
- Ricerca eventi per coordinate geografiche
- Ricerca eventi per intervallo di date
- Generazione e acquisto di biglietti per gli eventi selezionati
- Interfaccia utente a riga di comando semplice e intuitiva

## Requisiti

- Python 3.x
- pymongo
- MongoDB

## Installazione

1. Clona il repository
2. Installa le dipendenze:
   -pip install pymongo
3. Configura la connessione MongoDB:
   Crea un file `config.py` nella directory principale del progetto e aggiungi la tua URI di connessione MongoDB:
```python
uri = "mongodb://your_connection_string_here"
```

## Utilizzo

Esegui lo script principale:
1. CLI
2. Segui le istruzioni a schermo

## Funzionalità

- Ricerca per nome del concerto: Cerca eventi utilizzando il nome del concerto
- Ricerca per artista: Trova eventi in base al nome dell'artista
- Ricerca geografica: Cerca eventi nelle vicinanze di coordinate specifiche
- Ricerca per data: Trova eventi in un intervallo di date specifico
- Generazione biglietti: Crea biglietti per gli eventi selezionati

### Database
Il progetto utilizza due collezioni MongoDB:

- events: Contiene informazioni sugli eventi musicali
- tickets: Memorizza i biglietti generati
