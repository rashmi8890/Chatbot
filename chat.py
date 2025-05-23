from openai import OpenAI
import streamlit as st
from users_db import create_user_table, add_user, get_user

client = OpenAI(api_key=st.secrets["openai"]["api_key"])
create_user_table()

st.set_page_config(page_title="Education Chatbot", page_icon="💬")
st.title("🎓 Education Chatbot")

st.markdown("""
    <style>
        .top-right-auth {
            position: fixed;
            top: 10px;
            right: 20px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.15);
            z-index: 9999;
            width: 300px;
        }
    </style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None

if not st.session_state.authenticated:
    st.markdown('<div class="top-right-auth">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            st.session_state.auth_mode = "Sign In"
    with col2:
        if st.button("Sign Up"):
            st.session_state.auth_mode = "Sign Up"

    if st.session_state.auth_mode == "Sign In":
        st.subheader("Sign In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn"):
            user = get_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.name = user[1]
                st.rerun()
            else:
                st.error("Invalid credentials!")

    elif st.session_state.auth_mode == "Sign Up":
        st.subheader("Sign Up")
        username = st.text_input("Choose a Username", key="signup_username")
        name = st.text_input("Full Name", key="signup_name")
        password = st.text_input("Create a Password", type="password", key="signup_password")
        if st.button("Register", key="register_btn"):
            add_user(username, name, password)
            st.success("User Registered! Please Sign In.")
            st.session_state.auth_mode = "Sign In"

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(f"Welcome, **{st.session_state.name}** 👋")
st.markdown("Ask anything related to education!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "question_summaries" not in st.session_state:
    st.session_state.question_summaries = []

def chat_with_gpt(prompt, chat_history):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=chat_history + [{"role": "user", "content": prompt}]
    )
    reply = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply, chat_history

with st.sidebar:
    st.header("🕒 Questions Asked")
    if st.session_state.question_summaries:
        for i, q in enumerate(st.session_state.question_summaries):
            st.markdown(f"{i+1}. {q}")
    else:
        st.write("No conversation yet.")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.auth_mode = None
        st.experimental_rerun()

st.markdown("### 💬 Conversation")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("Type your message:", key="user_input_field", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(":material/send:")

if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history)
    st.session_state.chat_history = updated_history

    heading = user_input.strip().split('\n')[0][:80]
    st.session_state.question_summaries.append(heading)

for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Chatbot:** {message['content']}")
