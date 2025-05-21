from openai import OpenAI
import streamlit as st
client = OpenAI(
  api_key="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"
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

for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Chatbot:** {message['content']}")

user_input = st.text_input("You:", key="user_input")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response, updated_history = chat_with_gpt(user_input, st.session_state.chat_history)
    st.session_state.chat_history = updated_history


