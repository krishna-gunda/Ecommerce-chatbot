"""
build_vectorstore.py
----------------------
This script does the RAG "knowledge base" setup in 3 steps:

  1. LOAD   - read the policy .txt files from data/policies/
  2. CHUNK  - split each document into smaller overlapping pieces
  3. EMBED  - convert each chunk into a vector (a list of numbers) using
              OpenAI's embedding model, and store it in ChromaDB

Run this ONCE (or whenever you change the policy documents) with:
    python build_vectorstore.py

After running, you'll have a "chroma_db" folder - that's your local vector
database. The agent will search this folder later to answer policy questions.
"""

import os
from dotenv import load_dotenv

# Load your OPENAI_API_KEY from the .env file
load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def main():
    # ---- STEP 1: LOAD the documents ----
    # DirectoryLoader reads every .txt file inside data/policies/
    # Each file becomes one "Document" object with .page_content and .metadata
    print("Step 1: Loading policy documents...")
    loader = DirectoryLoader(
        "data/policies",
        glob="*.txt",
        loader_cls=TextLoader
    )
    documents = loader.load()
    print(f"  Loaded {len(documents)} documents.")
    for doc in documents:
        source_name = doc.metadata.get("source", "unknown")
        print(f"   - {source_name} ({len(doc.page_content)} characters)")

    # ---- STEP 2: CHUNK the documents ----
    # LLMs and retrievers work better with small focused chunks instead of
    # giant documents. RecursiveCharacterTextSplitter tries to split on
    # paragraph breaks first, then sentences, so chunks stay meaningful.
    #
    # chunk_size=500      -> each chunk is roughly 500 characters
    # chunk_overlap=50     -> chunks overlap by 50 characters so we don't
    #                         accidentally cut a sentence in half between chunks
    print("\nStep 2: Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"  Created {len(chunks)} chunks from {len(documents)} documents.")

    # ---- STEP 3: EMBED the chunks and store them ----
    # OpenAIEmbeddings turns each chunk of text into a vector (list of numbers)
    # that captures its meaning. Similar meanings = similar vectors.
    # Chroma.from_documents does two things at once:
    #   a) calls the embedding model on every chunk
    #   b) saves the resulting vectors + original text into a local folder
    print("\nStep 3: Creating embeddings and saving to ChromaDB...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db",   # this folder becomes your vector DB
        collection_name="ecommerce_policies"
    )

    print(f"  Done. Vector database saved to ./chroma_db")
    print(f"  Total chunks embedded: {len(chunks)}")

    # Quick sanity check: run a test search right away
    print("\nQuick test search: 'What is the return window for electronics?'")
    results = vectorstore.similarity_search(
        "What is the return window for electronics?", k=2
    )
    for i, result in enumerate(results, start=1):
        print(f"\n  Result {i}:")
        print(f"  {result.page_content[:200]}...")


if __name__ == "__main__":
    main()
