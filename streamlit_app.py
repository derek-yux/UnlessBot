from pathlib import Path

import streamlit as st
from openai import OpenAI
import json
import os


DB_FILE = 'db.json'
THIS_DIR = Path(__file__).parent if "__file__" in locals() else Path.cwd()
CSS_FILE = THIS_DIR / "main.css"


def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css_file(CSS_FILE)

def main():
    client = OpenAI(api_key=st.session_state.openai_api_key)

    # List of models
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    # Create a select box for the models
    st.session_state["openai_model"] = st.sidebar.selectbox("Select OpenAI model", models, index=0)
    st.session_state["tone"] = st.sidebar.selectbox("Customize my tone!", ('Normal', 'Philosophical', 'OUTRAGEOUSLY FUNNY!', 'Depressed :('))
    st.session_state["lang"] = st.sidebar.selectbox("Language", ('English', 'Chinese (Mandarin)', 'Korean', 'French'))
    st.header("Unless Bot!")
    st.markdown(f'<a href="https://buy.stripe.com/14k4jp0Yi6my2qsdQQ" class="button"> Unlock Unlimited Unlesses!</a>',
                unsafe_allow_html=True,
               )
    st.subheader(":green[...unless?]")
    # Load chat history from db.json
    with open(DB_FILE, 'r') as file:
        db = json.load(file)
    st.session_state.messages = db.get('chat_history', [])

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Tell me a fact! (ex. I will eat tacos every day)"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            tone=st.session_state["tone"]
            lang=st.session_state["lang"]
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"] + ". If this is falsifiable, make a(n) " + str(tone) + " response within 15 words in " + str(lang) + "and start your answer with the word '...unless'. Else, respond normally."}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Store chat history to db.json
        db['chat_history'] = st.session_state.messages
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)

    # Add a "Clear Chat" button to the sidebar
    if st.sidebar.button('Clear Chat'):
        # Clear chat history in db.json
        db['chat_history'] = []
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)
        # Clear chat messages in session state
        st.session_state.messages = []
        st.rerun()


if __name__ == '__main__':

    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        main()
    
    else:

        # if the DB_FILE not exists, create it
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w') as file:
                db = {
                    'openai_api_keys': [],
                    'chat_history': []
                }
                json.dump(db, file)
        # load the database
        else:
            with open(DB_FILE, 'r') as file:
                db = json.load(file)

        # display the selectbox from db['openai_api_keys']
        selected_key = st.selectbox(
            label = "Existing OpenAI API Keys", 
            options = db['openai_api_keys']
        )

        # a text input box for entering a new key
        new_key = st.text_input(
            label="New OpenAI API Key", 
            type="password"
        )

        login = st.button("Login")

        # if new_key is given, add it to db['openai_api_keys']
        # if new_key is not given, use the selected_key
        if login:
            if new_key:
                db['openai_api_keys'].append(new_key)
                with open(DB_FILE, 'w') as file:
                    json.dump(db, file)
                st.success("Key saved successfully.")
                st.session_state['openai_api_key'] = new_key
                st.rerun()
            else:
                if selected_key:
                    st.success(f"Logged in with key '{selected_key}'")
                    st.session_state['openai_api_key'] = selected_key
                    st.rerun()
                else:
                    st.error("API Key is required to login")
