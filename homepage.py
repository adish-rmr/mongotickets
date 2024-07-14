import streamlit as st
import functions as f


st.title("MongoTickets")

if "page" not in st.session_state:
    st.session_state.page = "home"

radio = st.radio("Search by", ["Name Event", "Artist", "Date", "Distance"], horizontal=True)

if radio == "Name Event" or radio == "Artist":
    lista = []
    t_input = st.text_input("Enter artist or event name", key="search", placeholder="e.g. Taylor Swift")
    if radio == "Name Event":
        results = f.search_by_name(t_input)
    else:
        results = f.search_by_artist(t_input)
    for doc in results:
        nome = doc["concert_name"]
        artista = ", ".join(doc["artists"])
        palco = doc["stage"]["name"]
        data = doc["date"].strftime("%m/%d/%Y, %H:%M")
        posti = doc["places_available"]
        prezzo = doc["price"]

        st.write(f"### {nome}")
        st.write(f"with **{artista}**  \n "
                 f"at {palco}, {data}  \n "
                 f"Only {posti} available! \n "
                 f"Price: {prezzo}€ ")

        buy = st.toggle("Buy", key=f"buy_{nome}")
        submitted = False
        if buy:
            with st.form(key=f"buy_{nome}"):
                user = st.text_input("Type your name")
                numero = st.number_input("How many tickets do you wanna buy?", min_value=1, max_value=posti, value="min")
                submitted = st.form_submit_button("Submit")
                if submitted:
                    st.session_state.buy = [nome, numero, user]
                    st.page_link("pages/buy.py", label="**PRINT TICKETS**", icon="🔙")




