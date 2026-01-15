# from sentence_transformers import SentenceTransformer
# import faiss
# from transformers import pipeline

# # Load embedding model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Read notes
# notes = open("notes.txt").read().split("\n")

# # Convert to vectors
# vectors = model.encode(notes)

# # Store in FAISS
# index = faiss.IndexFlatL2(vectors.shape[1])
# index.add(vectors)

# query = "Explain supervised learning"
# query_vector = model.encode([query])

# # Search similar notes
# D, I = index.search(query_vector, k=1)

# relevant_notes = [notes[i] for i in I[0]]
# print(relevant_notes)


# # ask LLM to answer based on relevant notes
# from transformers import pipeline

# generator = pipeline(
#     "text2text-generation",
#     model="google/flan-t5-small",
#     device=-1  # CPU
# )

# context = " ".join(relevant_notes)

# context = relevant_notes[0]

# prompt = f"""
# Task: Explain a machine learning concept.

# Concept name:
# Supervised learning

# Given fact:
# Supervised learning uses labeled data.

# Write a simple explanation in 3 bullet points.
# """



# output = generator(
#     prompt,
#     max_new_tokens=120,
#     do_sample=False
# )

# print(output[0]["generated_text"])


