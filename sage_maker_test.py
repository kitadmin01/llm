import os
import pinecone
from sage_maker import SageMakerHelper  

# Initialize Pinecone
pinecone.init(api_key=os.environ.get("PINECONE_API_KEY"), environment=os.environ.get("PINECONE_ENV"))

# Model and endpoint names
flan_t5_model_name = "flan-t5-model"
flan_t5_endpoint_name = "flan-t5-demo"
minilm_model_name = "minilm-model"
minilm_endpoint_name = "minilm-demo"

# Create and use the SageMakerHelper class
helper = SageMakerHelper("./content/Amazon_SageMaker_FAQs.csv", 
                         flan_t5_model_name, flan_t5_endpoint_name, 
                         minilm_model_name, minilm_endpoint_name)

# Create and upload data to the Pinecone index
index_name = 'kit'
helper.process_and_upload_data(index_name)

# Create a Pinecone index object
index = pinecone.Index(index_name)

# Define the prompt template
prompt_template = """
Answer the following QUESTION based on the CONTEXT_TEXT provided. If you do not know the answer and the CONTEXT_TEXT say "I don't know".

CONTEXT_TEXT:
{context_text}

QUESTION:
{question_text}

ANSWER:
"""

# Use the rag_query method
question = "How does Amazon SageMaker Canvas pricing work?"
response = helper.rag_query(question, index, prompt_template)
print(response)
