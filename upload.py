import streamlit as st
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["ASST"]

# Create columns for the logo and the title
col1, col2 = st.columns([1, 4])

# In the first column, display the logo
with col1:
    st.image('lock.png', width=100)  # Adjust the width as needed

# In the second column, display the title and subtitle
with col2:
    st.markdown("<h2 style='margin-top: 0;padding-left: 10px;'>Secure Doc Analyzer</h2>", unsafe_allow_html=True)
    st.markdown("<em><p style='margin-top: 0; padding-left: 10px;'>Intelligent insights into your documents.</p></em>", unsafe_allow_html=True)

# Information box with AI assistant capabilities and knowledge base
info_text = """
Powered by GPT-4, this assistant helps you analyze documents.
Upload your files, and ask questions directly about the content.
"""


st.info(info_text, icon="ℹ️")


uploaded_file = st.file_uploader("Upload document(s). Must be a pdf, docx, or txt file.", type=['pdf', 'txt', 'docx'])

def send_message_get_response(assistant_id, user_message, file_id=None):
    if 'thread' not in st.session_state:
        st.session_state['thread'] = client.beta.threads.create().id

    thread_id = st.session_state['thread']

    message = {
        "role": "user",
        "content": user_message
    }

    if file_id:
        message["attachments"] = [{"file_id": file_id, "tools": [{"type": "file_search"}]}]

    client.beta.threads.messages.create(thread_id=thread_id, **message)

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread_id, run_id=run.id))
    message_content = messages[0].content[0].text
    annotations = message_content.annotations
    citations = []

    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    return message_content.value, "\n".join(citations)

def main():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            with st.chat_message("user", avatar="🧑‍💻"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg["content"])
                if msg["citations"]:
                    st.write(msg["citations"])

    user_input = st.chat_input(placeholder="Please ask me your question…")

    if user_input:
        st.session_state['messages'].append({'role': 'user', 'content': user_input})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.write(user_input)

        with st.spinner('Working on this for you now...'):
            if uploaded_file:
                message_file = client.files.create(file=uploaded_file, purpose="assistants")
                response, citations = send_message_get_response(ASSISTANT_ID, user_input, message_file.id)
            else:
                response, citations = send_message_get_response(ASSISTANT_ID, user_input)

            st.session_state['messages'].append({'role': 'assistant', 'content': response, 'citations': citations})
            with st.chat_message("assistant", avatar="🤖"):
                st.write(response)
                if citations:
                    st.write(citations)

if __name__ == "__main__":
    main()
