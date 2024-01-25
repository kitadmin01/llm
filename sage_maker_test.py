import os
import pinecone
from sagemaker.huggingface import HuggingFacePredictor
from sage_model_deploy import ModelDeploymentAndEndpointManager 
from sage_embeed_creator import EmbeddingCreator
from sage_query_processor import QueryProcessor
from dotenv import load_dotenv 
load_dotenv()
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from sagemaker.huggingface.model import HuggingFacePredictor

# Assuming the necessary AWS and Pinecone environment variables are set:
os.environ['AWS_ROLE_ARN'], os.environ['PINECONE_API_KEY'], os.environ['PINECONE_ENV']

# Initialize Pinecone
pinecone.init(api_key=os.environ.get("PINECONE_API_KEY"), environment=os.environ.get("PINECONE_ENV"))

# Model and endpoint names
gpt2_model_name = "gpt2-medium-model"
gpt2_endpoint_name = "gpt2-medium-demo"
bert_model_name = "bert-base-uncased"  
bert_endpoint_name = "bert-base-demo"

# Create and use the ModelDeploymentAndEndpointManager class
deployment_manager = ModelDeploymentAndEndpointManager(
    gpt2_model_name, gpt2_endpoint_name, bert_model_name, bert_endpoint_name, os.environ['AWS_ROLE_ARN']
)

# Define the configurations for the GPT-2 and BERT models
hub_config_gpt2 = {
    'HF_MODEL_ID': 'gpt2-medium',  # Model ID from Hugging Face Hub
    'HF_TASK': 'text-generation'   # Task specification
}

hub_config_bert = {
    'HF_MODEL_ID': 'bert-base-uncased',  # Model ID from Hugging Face Hub
    'HF_TASK': 'feature-extraction'      # Task specification
}

# Get the Hugging Face container image URIs for the respective models
llm_image_gpt2 = get_huggingface_llm_image_uri("huggingface", version="0.8.2")
llm_image_bert = get_huggingface_llm_image_uri("huggingface", version="0.8.2")

# Deploy GPT-2 model and create an endpoint
# deployment_manager.deploy_model(hub_config_gpt2, llm_image_gpt2, gpt2_endpoint_name, gpt2_model_name)

# Deploy BERT model and create an endpoint
# deployment_manager.deploy_model(hub_config_bert, llm_image_bert, bert_endpoint_name, bert_model_name)

# Initialize EmbeddingCreator with the predictor for the BERT model
# Initialize EmbeddingCreator with the predictor for the BERT model
bert_predictor = HuggingFacePredictor(endpoint_name=bert_endpoint_name)
embedding_creator = EmbeddingCreator(bert_predictor, bert_model_name)

# Initialize QueryProcessor with the predictor for the GPT-2 model
gpt2_predictor = HuggingFacePredictor(endpoint_name=gpt2_endpoint_name)
index_name = 'kit'  # Replace with your Pinecone index name
index = pinecone.Index(index_name)

prompt_template = """
Answer the following QUESTION based on the CONTEXT_TEXT provided. If you do not know the answer and the CONTEXT_TEXT say "I don't know".

CONTEXT_TEXT:
{context_text}

QUESTION:
{question_text}

ANSWER:
"""

query_processor = QueryProcessor(gpt2_predictor, index, prompt_template, embedding_creator)

# Use the query_processor to process a query
question = "How does Amazon SageMaker Canvas pricing work?"
response = query_processor.rag_query(question)
print(response)