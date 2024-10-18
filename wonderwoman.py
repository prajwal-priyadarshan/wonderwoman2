import streamlit as st
import base64
import os
from groq import Groq
from pinecone import Pinecone

# Initialize Groq and Pinecone clients
client = Groq(api_key="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")
pc = Pinecone(api_key="87533450-0ea3-4657-9c34-bcb35f7833b4")
index = pc.Index("quickstart")

# Set API key in the session state
st.session_state.api_key = "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"

# Apply custom CSS for pinkish theme
def apply_custom_css():
    st.markdown("""
        <style>
            body {
                background-color: #ffe6f2; /* Soft pink background */
                color: #4d004d; /* Dark purple text */
                font-family: 'Arial', sans-serif;
            }
            .stTextInput>div>input {
                border: 2px solid #ff66b2; /* Input border color */
                border-radius: 8px; /* Rounded input */
                padding: 10px; /* Padding in input */
                font-size: 16px; /* Input font size */
                color: #4d004d; /* Dark purple input text */
            }
            .stButton>button {
                background-color: #ff66b2; /* Button color */
                color: white; /* Button text color */
                border: none; /* No border */
                border-radius: 8px; /* Rounded button */
                padding: 10px 20px; /* Button padding */
                font-size: 16px; /* Button font size */
                cursor: pointer; /* Pointer on hover */
            }
            .stButton>button:hover {
                background-color: #cc0066; /* Darker pink on hover */
            }
            .stChatInput textarea {
                background-color: #ffe6f2;
                color: #4d004d;
            }
        </style>
    """, unsafe_allow_html=True)

# Apply the custom CSS theme
apply_custom_css()

# Only show the API key input if the key is not already set
if not st.session_state.api_key:
    # Ask the user's API key if it doesn't exist
    api_key = st.text_input("Enter API Key", type="password")
    
    # Store the API key in the session state once provided
    if api_key:
        st.session_state.api_key = api_key
        st.rerun()  # Refresh the app once the key is entered to remove the input field
else:
    # If the API key exists, show the chat app
    st.title("🌸 Chat to Get to Know About Inspiring Women 🌸")

    # Initialize the chat message list in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.groq_chat_messages = [{"role": "system", "content": "You are a helpful assistant. The user will ask a query, and you will respond to it. If any additional context for the query is found, you will be provided with it."}]
        st.session_state.chat_messages = []
        
    # Display previous chat messages
    for messages in st.session_state.chat_messages:
        if messages["role"] in ["user", "assistant"]:
            with st.chat_message(messages["role"]):
                st.markdown(messages["content"])
    
    # Define a function to simulate chat interaction (you would replace this with an actual API call)
    def get_chat():
        embedding = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[st.session_state.chat_messages[-1]["content"]],
            parameters={
                "input_type": "query"
            }
        )
        results = index.query(
            namespace="ns1",
            vector=embedding[0].values,
            top_k=3,
            include_values=False,
            include_metadata=True
        )
        context = ""
        for result in results.matches:
            if result['score'] > 0.8:
                context += result['metadata']['text']
            
        st.session_state.groq_chat_messages[-1]["content"] = f"User Query: {st.session_state.chat_messages[-1]['content']} \n Retrieved Content (optional): {context}"
        chat_completion = client.chat.completions.create(
            messages=st.session_state.groq_chat_messages,
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content

    # Handle user input
    if prompt := st.chat_input("Ask a question about inspiring women, or thank the assistant!"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        st.session_state.groq_chat_messages.append({"role": "user", "content": prompt})
        
        # Get the assistant's response
        with st.spinner("Getting response..."):
            response = get_chat()
        
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add user message and assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.session_state.groq_chat_messages.append({"role": "assistant", "content": response})
