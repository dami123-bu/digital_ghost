# Digital Ghost — Project Overview

## What We're Building

A web application that lets a researcher ask plain-English questions about pharmaceutical drugs and get back relevant scientific literature plus an AI-written summary. It serves as the **target system** for our security research — we build it, then attack it (context poisoning, prompt injection) and measure defenses.

## RAG and Agents

RAG (Retrieval-Augmented Generation) gives the LLM a private search engine at query time, retrieving semantically relevant document chunks from a vector database — see [RAG.md](RAG.md) for a full explanation. 

There are two LangChain agents (Ingest Agent and Query Agent). See [RAG.md](RAG.md) for details on the agent pattern and what each agent does.

## MCP
To be added

## Prompt injection and Context poisoning

### Our Scenario
We simulate a pharmaceutical research assistant. The knowledge base(RAG) is seeded with scientific abstracts from **PubMed** (the US National Library of Medicine's public database of biomedical literature — ~35 million articles). 

A web UI will be provided. 
- Upload PDF documents which will go into the RAG
- A researcher can type a question like *"What are the side effects of Drug X at high doses?"* and get back the 20 most relevant papers plus an AI summary.

Users can also upload their own PDFs, which get added to the same knowledge base. This upload pathway is a primary attack surface — a malicious PDF can inject instructions that manipulate the LLM's behavior for all future queries.


---
