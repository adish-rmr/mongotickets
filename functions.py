import pymongo
from unidecode import unidecode
from config import uri
import streamlit as st
import datetime
import pandas as pd
import json
import acquisto_big as a


client = pymongo.MongoClient(uri)
db = client['MongoTicket']
events = db['events']
tickets = db['tickets']


def search_by_name(keyword):
    query = {"concert_name": {"$regex": keyword, "$options": "i"}}
    results = events.find(query)
    return list(results)


def search_by_artist(keyword):
    query = {"artists": {"$regex": keyword, "$options": "i"}}
    results = events.find(query)
    return list(results)


def generate_ticket(concert_name, num, name_buyer):
    event = events.find_one({"concert_name": concert_name})
    if event:
        if event['places_available'] <= 0:
            return False
        else:
            while num > 0:
                events.update_one({"concert_name": concert_name},
                                  {"$inc": {"places_available": -1}})
                ticket = {"id_event": event["_id"],
                          "concert_name": event["concert_name"],
                          "buyer_name": name_buyer,
                          "seat_number": event['places_available']-num}
                receipt = tickets.insert_one(ticket)
                num -= 1
                st.write(f"Ticket ID: {receipt.inserted_id}")
            return True


def search_geo(coordinates):
    events_nearby = concerti.aggregate([
        {'$match': {
            'location.geo': {
                '$geoWithin': {
                    '$centerSphere': [coordinates[::-1], 7000 / 6378100]}
            }}}])
    return events_nearby


for event in events_nearby:
    print(f"Evento: {event.get('concert_name', 'N/A')}")
