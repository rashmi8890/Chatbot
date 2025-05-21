from openai import OpenAI
import streamlit as st
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"]
)

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


st.set_page_config(page_title="Education Chatbot", page_icon="💬")
st.title("🎓 Education Chatbot")
st.markdown("Ask anything related to education!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Show chat history in sidebar
with st.sidebar:
    st.header("🕒 Chat History")
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            role = "👤 You" if msg["role"] == "user" else "🤖 Chatbot"
            st.markdown(f"**{role}:** {msg['content']}")
    else:
        st.write("No conversation yet.")


st.markdown("### 💬 Conversation")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Chatbot:** {message['content']}")

# Input and send button in a form
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])  # Adjust ratio as needed
    with col1:
        user_input = st.text_input("Type your message:", key="user_input_field", label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(":material/send:")

# Process input on button click
if submit_button and user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history)
    st.session_state.chat_history = updated_history
