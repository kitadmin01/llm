# Vector Embedding for Website

## Overview
This repository contains a collection of programs designed to create vector embeddings for content from the website [www.analytickit.com](https://www.analytickit.com). It utilizes both Hugging Face open-source models and OpenAI models to generate embeddings. These embeddings are then uploaded to PineCone, enabling a feature on the Analytickit website where users can ask questions and receive answers about the Analytickit SAAS platform.

## Data Flow Diagram
![Alt text](./images/image.png)

## Contents
- `requirements.txt`: Lists all the Python dependencies required for the project.
- `uploader_openai.py`: Script to create embeddings using OpenAI models and upload them to PineCone.
- `query_openai.py`: Script to query the uploaded data using OpenAI models.
- `openai_up.py`: An alternative or supplementary script for uploading data using OpenAI models.
- `query.py`: General script for querying the uploaded embedding data.
- `uploader.py`: General script for uploading data to PineCone.
- `LICENSE`: The license file for the project.
- `.gitignore`: Specifies intentionally untracked files to ignore.

## Goal
The primary goal of this project is to enhance the user experience on the Analytickit website. By integrating these vector embeddings into the site, users can interactively ask questions and receive relevant answers about the Analytickit SAAS platform, leveraging the power of advanced AI models.

## How to Use
1. Install the required dependencies: `pip install -r requirements.txt`
2. Use `uploader_openai.py` or `uploader.py` to create and upload embeddings to PineCone.
3. Query the data using `query_openai.py` or `query.py` as needed.

## License
This project is licensed under the [LICENSE](LICENSE) included in the repository.

# RAG in AWS SageMaker
![Alt text](./images/RAG-SageMaker.png)

# AWS Architecture Overview for Language Learning Model

This diagram illustrates our AWS-backed system designed to process user queries using advanced natural language processing models. The architecture facilitates a conversational AI or question-answering application that provides intelligent and context-aware responses. Below is an overview of the key components of our system:

## Doc2Vector Mapper

The `Doc2Vector Mapper` is a crucial component that transforms textual data into a numerical vector format. Doing so converts the high-dimensional text data into a lower-dimensional space that retains semantic meaning but is more manageable for computational processes. The vectors generated by this mapper are essential for the subsequent machine learning tasks, as they allow for efficient similarity comparisons and pattern recognition within the text.

## Query2Vector Mapper

Following the `Doc2Vector Mapper`, the `Query2Vector Mapper` takes the user's input text and converts it into a query vector. This representation enables the system to accurately understand and compare the user's query against the indexed knowledge base. The conversion to a vector space is a fundamental step to facilitate matching the query with relevant information and context in subsequent processing stages.

## Content Generation

The Content Generation stage is where the processed input comes to fruition. It involves:

- **Retrieving Conversation History**: This step involves recalling the previous exchanges with the user, stored in `Amazon DynamoDB,` to maintain context and coherence in the conversation.
- **Prompt Template Generation**: Here, the system constructs a prompt that includes the user's query, retrieved text from `OpenSearch`, and the conversation history. This prompt is then fed to a `SageMaker-deployed Language Learning Model (LLM).
- **SageMaker LLM Response**: Our LLM, developed on `Amazon SageMaker`, utilizes the prompt to generate an appropriate response. The model leverages the `BERT` algorithm to understand the nuances of the query and produce a relevant and accurate answer.

The response generated by the LLM is then conveyed back to the user, completing the query-response cycle. This architecture enables our system to handle complex queries and provide contextually relevant and insightful responses, enhancing the user's experience.

## Architectural Steps
## Program 1: Data Processing and Embedding Storage

### PostgreSQL Database
- **Description**: Contains FAQ data.
- **Data Flow**: Arrows from the database indicate data flow to the next component.

### Data Retrieval and Preprocessing
- **Function**: Retrieves data from PostgreSQL.
- **Processes**:
  - Preprocesses text (cleaning, normalization).
- **Connections**:
  - Connects to the PostgreSQL database.
  - Connects to the Embedding Model.

### Embedding Model
- **Function**: Converts preprocessed text into embeddings.
- **Data Flow**:
  - Receives input from Data Retrieval and Preprocessing.
  - Sends embeddings to Pinecone.

### Pinecone (Vector Database)
- **Function**: Stores embeddings with metadata.
- **Data Flow**:
  - Receives embeddings from the Embedding Model.

## Program 2: User Interaction and Response Generation

### User Interface
- **Function**:
  - Receives user queries.
  - Sends queries to the Embedding Model.

### Embedding Model (same as in Program 1)
- **Function**:
  - Converts user queries into embeddings.
  - Sends query embeddings to Pinecone.

### Pinecone (Vector Database) (same as in Program 1)
- **Function**:
  - Receives query embeddings.
  - Performs similarity search.
  - Returns matching FAQ IDs and metadata.
- **Connections**:
  - Connects to PostgreSQL Database for FAQ retrieval.

### PostgreSQL Database (same as in Program 1)
- **Function**:
  - Receives FAQ IDs and metadata from Pinecone.
  - Retrieves corresponding FAQ texts.
  - Sends FAQ texts to the Language Model.

### Language Model (e.g., GPT-3)
- **Function**:
  - Receives combined context (user query + FAQ texts).
  - Generates a response based on the context.
  - Sends the response back to the User Interface.

### User Interface
- **Function**: Displays the generated response to the user.



# MLOps in AWS
![Alt text](./images/aws_mlops.png)