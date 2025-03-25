# LangChain Python SDK Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Components](#core-components)
4. [Model I/O](#model-io)
5. [Data Connection](#data-connection)
6. [Chains](#chains)
7. [Memory](#memory)
8. [Agents](#agents)
9. [Vector Search & Embeddings](#vector-search--embeddings)
10. [Integration Examples](#integration-examples)

## Introduction

LangChain is a framework designed to simplify the creation of applications using Large Language Models (LLMs). It provides a standard interface for chains, integrating with various LLMs, and managing the composition of multiple chains through agents.

### Key Features
- Data-aware: Connect LLMs with external data sources
- Agentic: Allow LLMs to interact with their environment
- Memory: Implement state in LLM applications
- Chains: Combine multiple components together

## Installation

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core LangChain
pip install langchain

# Common additional dependencies
pip install python-dotenv  # for environment variables
pip install openai        # for OpenAI models
pip install chromadb      # for vector store
pip install tiktoken      # for token counting
```

## Core Components

### 1. LLMs and Chat Models
```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Initialize LLM
llm = OpenAI(temperature=0.7)

# Initialize Chat Model
chat_model = ChatOpenAI(temperature=0.7)
```

### 2. Prompts
```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["product"],
    template="What is a good name for a company that makes {product}?"
)
```

### 3. Output Parsers
```python
from langchain.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()
format_instructions = parser.get_format_instructions()
```

## Data Connection

### Document Loaders
```python
from langchain.document_loaders import TextLoader, PyPDFLoader

# Load text files
loader = TextLoader("path/to/file.txt")
documents = loader.load()

# Load PDF files
pdf_loader = PyPDFLoader("path/to/file.pdf")
pdf_documents = pdf_loader.load()
```

### Text Splitters
```python
from langchain.text_splitter import CharacterTextSplitter

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200
)
```

## Vector Search & Embeddings

### 1. Embeddings
```python
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
```

### 2. Vector Stores

#### Chroma
```python
from langchain.vectorstores import Chroma

db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="path/to/store"
)
```

#### FAISS
```python
from langchain.vectorstores import FAISS

vectorstore = FAISS.from_documents(
    documents=documents,
    embedding=embeddings
)
```

### 3. Similarity Search
```python
# Basic similarity search
docs = db.similarity_search("query text", k=4)

# Similarity search with score
docs = db.similarity_search_with_score("query text", k=4)
```

## Chains

### 1. Basic Chain Types
```python
from langchain.chains import LLMChain, SimpleSequentialChain

# Simple LLM Chain
chain = LLMChain(llm=llm, prompt=prompt)

# Sequential Chain
chain1 = LLMChain(llm=llm, prompt=prompt1)
chain2 = LLMChain(llm=llm, prompt=prompt2)
sequential_chain = SimpleSequentialChain(chains=[chain1, chain2])
```

### 2. Question Answering Chains
```python
from langchain.chains.question_answering import load_qa_chain

chain = load_qa_chain(llm, chain_type="stuff")
response = chain.run(input_documents=docs, question="your question")
```

## Memory

### 1. Conversation Buffer Memory
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)
```

### 2. Vector Store Memory
```python
from langchain.memory import VectorStoreRetrieverMemory

retriever = vectorstore.as_retriever()
memory = VectorStoreRetrieverMemory(retriever=retriever)
```

## Agents

### 1. Basic Agent
```python
from langchain.agents import load_tools, initialize_agent
from langchain.agents import AgentType

tools = load_tools(["wikipedia", "llm-math"], llm=llm)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

### 2. Custom Tools
```python
from langchain.tools import Tool

custom_tool = Tool(
    name="Custom-Tool",
    func=lambda x: "Custom tool response",
    description="Custom tool description"
)
```

## Integration Examples

### 1. RAG (Retrieval Augmented Generation)
```python
from langchain.chains import RetrievalQA

retriever = vectorstore.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

### 2. Chat with Documents
```python
from langchain.chains import ConversationalRetrievalChain

chain = ConversationalRetrievalChain.from_llm(
    llm=chat_model,
    retriever=retriever,
    memory=memory
)
```

## Best Practices

1. **Error Handling**
   - Always implement proper error handling for API calls
   - Handle rate limiting and token limits appropriately
   - Implement retries for transient failures

2. **Security**
   - Never hardcode API keys
   - Use environment variables for sensitive information
   - Implement proper authentication and authorization

3. **Performance**
   - Use async operations when possible
   - Implement caching where appropriate
   - Optimize chunk sizes for document splitting

4. **Monitoring**
   - Implement logging for debugging
   - Track token usage
   - Monitor API response times

## Advanced Features

### 1. Custom Callbacks
```python
from langchain.callbacks import BaseCallbackHandler

class CustomCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"Starting LLM with prompts: {prompts}")
```

### 2. Streaming Responses
```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = OpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0
)
```

## Troubleshooting

Common issues and their solutions:

1. **Rate Limiting**
   - Implement exponential backoff
   - Use appropriate API tiers
   - Monitor usage limits

2. **Memory Issues**
   - Optimize chunk sizes
   - Implement pagination
   - Use efficient vector stores

3. **Token Limits**
   - Monitor token usage
   - Implement truncation strategies
   - Use efficient prompts

## Additional Resources

- [Official Documentation](https://python.langchain.com/)
- [GitHub Repository](https://github.com/hwchase17/langchain)
- [LangChain Hub](https://github.com/hwchase17/langchain-hub)
- [Community Discord](https://discord.gg/6adMQxSpJS)

## Version Information

This documentation is current as of 2024 and covers LangChain version 0.1.0 and above. Please check the official documentation for the latest updates and changes. 