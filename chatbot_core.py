import os
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer
import faiss
from pypdf import PdfReader
from streamlit import context
from torch import mode
import chardet

# Load environment variables
load_dotenv()


# Read API key safely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Embedding model (local, free)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def build_index(text_by_file, chunk_size=500):
    chunks = []
    sources = []
    for filename,text in text_by_file.items():
        words = text.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
            sources.append(filename)

    if len(chunks) == 0:
        raise ValueError("Document text could not be chunked properly.")

    vectors = embed_model.encode(chunks)

    if len(vectors.shape) < 2:
        raise ValueError("Embedding generation failed.")

    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    return chunks, index, sources




def get_answer(query, notes, index, mode, chat_history, answer_length, sources):
    query_vec = embed_model.encode([query])
    _, I = index.search(query_vec, k=1)
    best_idx = I[0][0]
    context = notes[best_idx]
    source_file = sources[best_idx]

    conversation = ""
    for chat in chat_history[-6:]:
        if isinstance(chat, dict):
            role = "User" if chat.get("role") == "user" else "Assistant"
            content = chat.get("content", "")
            conversation += f"{role}: {content}\n"


    # Length instruction
    if answer_length == "Short":
        length_instruction = "Answer in 2 to 3 short lines."
    elif answer_length == "Medium":
        length_instruction = "Answer in one clear paragraph."
    else:
        length_instruction = "Give a detailed explanation with bullet points."
    # Detect weak context
    context_is_weak = len(context.split()) < 20

    # 🔁 MODE 1: Own Generated (STRICT RAG)
    if mode == "Own Generated":
        prompt = f"""
You are an AI tutor.

Answer the question using ONLY the reference notes below.
Do NOT add extra information.
Do NOT use outside knowledge.

Reference notes:
{context}

Question:
{query}

Give a clear, simple answer.
"""
    # 🔁 MODE 2: Wikipedia Preference Generated
    else:
        if mode == "Own Generated":
            prompt = f"""
You are an AI tutor.
Use ONLY the reference notes. Do not add outside information.

Reference notes:
{context}

Question:
{query}

{length_instruction}
"""
        else:
            if context_is_weak:
                prompt = f"""
You are an expert AI tutor.

The reference notes are insufficient.
Answer the question using your general knowledge.

Question:
{query}

{length_instruction}
"""
            else:
                prompt = f"""
You are an expert AI tutor.
Prefer the reference notes, but you may use general knowledge.

Reference notes:
{context}

Question:
{query}

{length_instruction}
"""

        

    response = client.models.generate_content(
        model="models/gemini-flash-lite-latest",
        contents=prompt
    )

    return response.text, source_file

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"

    return text


def decode_text_file(uploaded_file):
    raw_bytes = uploaded_file.read()

    result = chardet.detect(raw_bytes)
    encoding = result["encoding"]

    if encoding is None:
        raise ValueError("Unable to detect file encoding.")

    return raw_bytes.decode(encoding, errors="ignore")
