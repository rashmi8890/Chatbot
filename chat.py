from openai import OpenAI
import streamlit as st
from users_db import create_user_table, add_user, get_user
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"]
)

create_user_table()

# Page setup
st.set_page_config(page_title="Education Chatbot", page_icon="💬")
st.title("🎓 Education Chatbot")

st.markdown("""
    <style>
        .top-right-auth {
            position: fixed;
            top: 10px;
            right: 20px;
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            z-index: 9999;
            width: 300px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Authentication UI ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # HTML container for auth
    st.markdown('<div class="top-right-auth">', unsafe_allow_html=True)

    auth_mode = st.selectbox("Choose Option", ["Sign In", "Sign Up"], key="auth_mode")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if auth_mode == "Sign Up":
        name = st.text_input("Full Name", key="fullname")
        if st.button("Register", key="register_btn"):
            add_user(username, name, password)
            st.success("User Registered! Please Sign In.")
    else:
        if st.button("Login", key="login_btn"):
            user = get_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state["username"] = username
                st.session_state["name"] = user[1]
                st.rerun() 
            else:
                st.error("Invalid credentials!")

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Chatbot Begins after Login ---
st.markdown(f"Welcome, **{st.session_state.name}** 👋")
st.markdown("Ask anything related to education!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def chat_with_gpt(prompt, chat_history):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=chat_history + [
        {"role": "user", "content": prompt}
        ]
    )

    reply = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": reply})
    return reply, chat_history

with st.sidebar:
    st.header("🕒 Chat History")
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            role = "👤 You" if msg["role"] == "user" else "🤖 Chatbot"
            st.markdown(f"**{role}:** {msg['content']}")
    else:
        st.write("No conversation yet.")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()


st.markdown("### 💬 Conversation")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Chatbot:** {message['content']}")


with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])  # Adjust ratio as needed
    with col1:
        user_input = st.text_input("Type your message:", key="user_input_field", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(":material/send:")


if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history)
    st.session_state.chat_history = updated_history
