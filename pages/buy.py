import streamlit as st
import functions as f

buy = st.session_state.buy
f.generate_ticket(buy[0], buy[1], buy[2])

