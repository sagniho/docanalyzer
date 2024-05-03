import streamlit as st
import openai

# Initialize the OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ASSISTANT_ID = st.secrets["McKund"]

def main():
    st.title('Interactive Document Analyzer')

    # Create columns for the logo and the title
    col1, col2 = st.columns([1, 4])

    # In the first column, display the logo
    with col1:
        st.image('lock.png', width=150)  # Adjust the width as needed

    # In the second column, display the title and subtitle
    with col2:
        st.markdown("<h2 style='margin-top: 0;padding-left: 10px;'>Secure Doc Analyzer</h2>", unsafe_allow_html=True)
        st.markdown("<em><p style='margin-top: 0; padding-left: 10px;'>Intelligent insights into your documents.</p></em>", unsafe_allow_html=True)

    # Information box with AI assistant capabilities
    st.info("Powered by GPT-4, this assistant helps you analyze documents. Upload your files, and ask questions directly about the content.", icon="ℹ️")

    # File upload and processing
    uploaded_file = st.file_uploader("Upload document(s). Must be a pdf, docx, or txt file.", type=['pdf', 'txt', 'docx'])
    document_content = ""
    if uploaded_file is not None:
        document_content = uploaded_file.getvalue().decode('utf-8')  # Simplified assumption

    # Initialize the thread in session state if not present
    if 'thread' not in st.session_state:
        st.session_state['thread'] = client.Thread.create().id

    # Initialize messages in session state if not present
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []

    # Display previous chat messages
    for msg in st.session_state['messages']:
        role, content = msg['role'], msg['content']
        if role == 'user':
            with st.chat_message("You", avatar="🧑‍💻"):
                st.write(content)
        else:
            with st.chat_message("AI Assistant", avatar="🤖"):
                st.write(content)

    # Chat input for new message
    user_input = st.text_input("Ask your question about the document here...", key="chat_input")

    # When a message is sent through the chat input
    if st.button("Send"):
        # Append the user message to the session state
        st.session_state['messages'].append({'role': 'user', 'content': user_input})

        # Get the response from the assistant
        with st.spinner('Analyzing your document...'):
            response = send_message_get_response(ASSISTANT_ID, user_input, document_content)
            # Append the response to the session state
            st.session_state['messages'].append({'role': 'assistant', 'content': response})
            # Display the assistant's response
            with st.chat_message("AI Assistant", avatar="🤖"):
                st.write(response)

def send_message_get_response(assistant_id, user_message, document_content):
    thread_id = st.session_state['thread']

    # Add user message to the thread with document content as context
    message = client.ThreadMessage.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        messages=[
            {"role": "system", "content": f"Document content: {document_content[:500]}..."},  # Provide initial part of document as context
            {"role": "user", "content": user_message}
        ]
    )

    # Poll for the response
    while True:
        time.sleep(1)  # Delay to prevent over-polling
        response = client.ThreadMessage.list(thread_id=thread_id)
        if response.data[-1].role == "assistant":
            return response.data[-1].content

if __name__ == "__main__":
    main()
