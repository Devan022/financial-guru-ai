# Dashboard rendering and visualization section
import streamlit as st

st.title("Survey")
st.title("Survey")


name = st.text_input("Your name")
rating = st.slider("Rate this app", 1, 5)

if st.button("Submit"):
    st.success(f"Thanks {name}, you rated us {rating}/5")

name = st.text_input("Your name")
rating = st.slider("Rate this app", 1, 5)

if st.button("Submit"):
    st.success(f"Thanks {name}, you rated us {rating}/5")
