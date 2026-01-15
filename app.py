import streamlit as st
from chatbot_core import build_index, get_answer
from chatbot_core import extract_text_from_pdf, decode_text_file


    

st.set_page_config(page_title="RAG Chatbot", layout="centered")

st.title("📘 RAG Notes Chatbot")
st.write("Ask questions from your uploaded notes")

# Initialize chat history
if "chat_history" not in st.session_state or not isinstance(st.session_state.chat_history, list):
    st.session_state.chat_history = []


# Upload notes
uploaded_files = st.file_uploader(
    "Upload your notes (.txt or .pdf)",
    type=["txt", "pdf"],
    accept_multiple_files=True,
    key="notes_uploader"
)


# Initialize filename tracker
if "last_uploaded_filenames" not in st.session_state:
    st.session_state.last_uploaded_filenames = None

# Detect change in uploaded files
current_filenames = []
if uploaded_files:
    current_filenames = sorted([file.name for file in uploaded_files])

# Reset chat if new files are uploaded
if st.session_state.last_uploaded_filenames != current_filenames:
    st.session_state.chat_history = []
    st.session_state.last_uploaded_filenames = current_filenames



if uploaded_files:

    text_by_file = {}
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".txt"):
            text = decode_text_file(uploaded_file)

        elif uploaded_file.name.endswith(".pdf"):
            text = extract_text_from_pdf(uploaded_file)
        else:
            continue
        text_by_file[uploaded_file.name] = text

    try:
        notes,sources ,index = build_index(text_by_file)
        st.success(f"{len(uploaded_files)} document(s) loaded successfully!")
        # 🧹 Clear chat button
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            st.rerun()
        # 📂 Show active uploaded files
        st.markdown("### 📂 Active Documents")
        st.markdown("📌 **Source:**")
        for file in uploaded_files:
            st.markdown(f"- {file.name}")
        st.markdown("📌 **Status:**")


        for file in uploaded_files:
            st.markdown(f"✔ {file.name}")

        st.session_state.file_loaded = True
    except Exception as e:
        st.error(f"Failed to process documents: {e}")
        st.stop()


    mode = st.radio(
        "Select Answer Mode",
        ("Own Generated", "Wikipedia Preference Generated")
    )
    #  Answer length slider
    answer_length = st.select_slider(
        "Select answer length",
        options=["Short", "Medium", "Long"]
    )

    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.markdown(f"**🧑 You:** {chat['content']}")
        else:
            st.markdown(f"**🤖 AI:** {chat['content']}")

    query = st.text_input("Ask a question")

    if st.button("Send") and query:
        # Save user message
        st.session_state.chat_history.append(
            {"role": "user", "content": query}
        )

        # Get AI answer
        answer, source = get_answer(
            query,
            notes,
            sources,
            index,
            mode,
            answer_length,
            st.session_state.chat_history
)


        # Save AI message
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        st.rerun()
