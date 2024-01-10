import os
import numpy as np
import pandas as pd
from typing import List
import boto3
from io import StringIO
import pinecone
import time
from tqdm.auto import tqdm
from sagemaker.huggingface import HuggingFaceModel, get_huggingface_llm_image_uri
from sagemaker.huggingface.model import HuggingFacePredictor
# Load environment variables
from dotenv import load_dotenv 
load_dotenv()
from botocore.exceptions import ClientError
from sagemaker.model import Model
from sagemaker.huggingface import HuggingFaceModel
import sagemaker
from sagemaker.session import Session



class SageMakerHelper:
    def __init__(self, csv_file_path, flan_t5_model_name, flan_t5_endpoint_name, minilm_model_name, minilm_endpoint_name):
        # Read AWS Role ARN from environment variable
        self.aws_role_arn = os.environ.get("AWS_ROLE_ARN")
        if not self.aws_role_arn:
            raise ValueError("AWS_ROLE_ARN environment variable not set")

        self.csv_file_path = csv_file_path
        self.flan_t5_model_name = flan_t5_model_name
        self.flan_t5_endpoint_name = flan_t5_endpoint_name
        self.minilm_model_name = minilm_model_name
        self.minilm_endpoint_name = minilm_endpoint_name

        # Initialize models and other configurations
        self.initialize_models()
        self.df_knowledge = self.read_csv_data()

    def read_csv_data(self):
        """Read data from a CSV file into a pandas DataFrame."""
        return pd.read_csv(self.csv_file_path, header=None, names=["Question", "Answer"])

    def initialize_models(self):
        """Initialize HuggingFace models and deploy them on SageMaker."""
        # Configuration for the FLAN-T5 model
        hub_config_flan_t5 = {
            'HF_MODEL_ID': 'google/flan-t5-xl',
            'HF_TASK': 'text-generation'
        }
        llm_image_flan_t5 = get_huggingface_llm_image_uri("huggingface", version="0.8.2")

        # Check if FLAN-T5 model exists and decide the deployment method
        if self.model_exists(self.flan_t5_model_name):
            if not self.check_endpoint_exists(self.flan_t5_endpoint_name):
                self.create_endpoint_with_existing_model(self.flan_t5_endpoint_name, self.flan_t5_model_name)
            self.llm = self.get_model_predictor(self.flan_t5_endpoint_name)
        else:
            self.llm = self.deploy_model(hub_config_flan_t5, llm_image_flan_t5, self.flan_t5_endpoint_name, self.flan_t5_model_name)

        if self.llm is None:
            raise Exception("Failed to initialize the FLAN-T5 model.")

        # Configuration for the MiniLM model
        hub_config_minilm = {
            'HF_MODEL_ID': 'sentence-transformers/all-MiniLM-L6-v2',
            'HF_TASK': 'feature-extraction'
        }
        llm_image_minilm = get_huggingface_llm_image_uri("huggingface", version="0.8.2")

        # Check if MiniLM model exists and decide the deployment method
        if self.model_exists(self.minilm_model_name):
            if not self.check_endpoint_exists(self.minilm_endpoint_name):
                self.create_endpoint_with_existing_model(self.minilm_endpoint_name, self.minilm_model_name)
            self.encoder = self.get_model_predictor(self.minilm_endpoint_name)
        else:
            self.encoder = self.deploy_model(hub_config_minilm, llm_image_minilm, self.minilm_endpoint_name, self.minilm_model_name)

        if self.encoder is None:
            raise Exception("Failed to initialize the MiniLM encoder model.")


    def get_model_predictor(self, endpoint_name):
        """Get the model predictor for an existing endpoint."""
        try:
            # Create a HuggingFacePredictor object for the existing endpoint
            return HuggingFacePredictor(endpoint_name=endpoint_name)
        except Exception as e:
            print(f"Error getting model predictor: {e}")
            return None

    def model_exists(self, model_name):
        """Check if a model exists in SageMaker."""
        sagemaker_client = boto3.client('sagemaker')
        try:
            sagemaker_client.describe_model(ModelName=model_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return False
            else:
                raise

    def create_endpoint_with_existing_model(self, endpoint_name, model_name):
        """Create an endpoint in SageMaker using an existing model."""
        sagemaker_client = boto3.client('sagemaker')

        # Check if the endpoint configuration already exists
        endpoint_config_name = endpoint_name + "-config"
        try:
            sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            print(f"Endpoint configuration '{endpoint_config_name}' already exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # Create the endpoint configuration
                print(f"Creating endpoint configuration '{endpoint_config_name}' with model '{model_name}'.")
                sagemaker_client.create_endpoint_config(
                    EndpointConfigName=endpoint_config_name,
                    ProductionVariants=[
                        {
                            'VariantName': 'AllTraffic',
                            'ModelName': model_name,
                            'InitialInstanceCount': 1,
                            'InstanceType': 'ml.g5.4xlarge',
                            'InitialVariantWeight': 1
                        }
                    ]
                )
            else:
                raise

        # Check if the endpoint already exists
        try:
            sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            print(f"Endpoint '{endpoint_name}' already exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # Create the endpoint
                print(f"Creating endpoint '{endpoint_name}'.")
                sagemaker_client.create_endpoint(
                    EndpointName=endpoint_name,
                    EndpointConfigName=endpoint_config_name
                )
                print(f"Endpoint '{endpoint_name}' creation initiated.")
            else:
                raise


    def get_actual_model_name(self, expected_model_name):
        """Retrieve the actual model name from SageMaker."""
        sagemaker_client = boto3.client('sagemaker')
        try:
            response = sagemaker_client.describe_model(ModelName=expected_model_name)
            return response['ModelName']
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return None
            else:
                raise

    def create_or_update_endpoint_config(self, endpoint_config_name, model_name):
        """Create or update the endpoint configuration."""
        sagemaker_client = boto3.client('sagemaker')
        try:
            sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            print(f"Endpoint configuration '{endpoint_config_name}' already exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                print(f"Creating endpoint configuration '{endpoint_config_name}'.")
                sagemaker_client.create_endpoint_config(
                    EndpointConfigName=endpoint_config_name,
                    ProductionVariants=[
                        {
                            'VariantName': 'AllTraffic',
                            'ModelName': model_name,
                            'InitialInstanceCount': 1,
                            'InstanceType': 'ml.g5.4xlarge',
                            'InitialVariantWeight': 1
                        }
                    ]
                )
            else:
                raise

    def create_endpoint_if_not_exists(self, endpoint_name, model_name):
        """Create the endpoint if it does not exist."""
        sagemaker_client = boto3.client('sagemaker')

        try:
            # Check if the endpoint already exists
            sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            print(f"Endpoint '{endpoint_name}' already exists.")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                # Endpoint does not exist, create it
                print(f"Creating endpoint '{endpoint_name}' with model '{model_name}'.")
                try:
                    # Create endpoint configuration
                    endpoint_config_name = endpoint_name + "-config"
                    sagemaker_client.create_endpoint_config(
                        EndpointConfigName=endpoint_config_name,
                        ProductionVariants=[
                            {
                                'VariantName': 'AllTraffic',
                                'ModelName': model_name,
                                'InitialInstanceCount': 1,
                                'InstanceType': 'ml.g5.4xlarge',
                                'InitialVariantWeight': 1
                            }
                        ]
                    )
                    # Create endpoint
                    sagemaker_client.create_endpoint(
                        EndpointName=endpoint_name,
                        EndpointConfigName=endpoint_config_name
                    )
                    print(f"Endpoint '{endpoint_name}' creation initiated.")
                except ClientError as error:
                    print(f"Error creating endpoint: {error}")
            else:
                raise



    def deploy_model(self, hub_config, llm_image, endpoint_name, model_name):
        """Deploy a HuggingFace model to SageMaker."""
        sagemaker_client = boto3.client('sagemaker')

        # Check if the model already exists
        model_exists = self.check_model_exists(model_name)

        # Create the model if it doesn't exist
        if not model_exists:
            print(f"Creating model '{model_name}'.")
            huggingface_model = HuggingFaceModel(
                env=hub_config,  # Ensure HF_MODEL_ID is included in hub_config
                role=self.aws_role_arn,
                image_uri=llm_image,
                name=model_name,  # Explicitly set the model name
                sagemaker_session=sagemaker.Session()
            )

            # Deploy the model
            huggingface_model.deploy(
                initial_instance_count=1,
                instance_type="ml.g5.4xlarge",
                endpoint_name=endpoint_name
            )

        # Check if the endpoint configuration already exists
        endpoint_config_name = endpoint_name + "-config"
        try:
            sagemaker_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            print(f"Endpoint configuration '{endpoint_config_name}' already exists. Updating it.")
            sagemaker_client.update_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[
                    {
                        'VariantName': 'AllTraffic',
                        'ModelName': model_name,
                        'InitialInstanceCount': 1,
                        'InstanceType': 'ml.g5.4xlarge',
                        'InitialVariantWeight': 1
                    }
                ]
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                print(f"Creating endpoint configuration '{endpoint_config_name}'.")
                sagemaker_client.create_endpoint_config(
                    EndpointConfigName=endpoint_config_name,
                    ProductionVariants=[
                        {
                            'VariantName': 'AllTraffic',
                            'ModelName': model_name,
                            'InitialInstanceCount': 1,
                            'InstanceType': 'ml.g5.4xlarge',
                            'InitialVariantWeight': 1
                        }
                    ]
                )

        # Check if the endpoint already exists
        if not self.check_endpoint_exists(endpoint_name):
            print(f"Creating endpoint '{endpoint_name}'.")
            sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            print(f"Endpoint '{endpoint_name}' creation initiated.")


    def check_model_exists(self, model_name):
        """Check if a model exists in SageMaker."""
        sagemaker_client = boto3.client('sagemaker')
        try:
            sagemaker_client.describe_model(ModelName=model_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return False
            else:
                raise

    def check_endpoint_exists(self, endpoint_name):
        """Check if an endpoint exists in SageMaker."""
        sagemaker_client = boto3.client('sagemaker')
        try:
            sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return False
            else:
                raise



    def embed_docs(self, docs: List[str]) -> np.ndarray:
        """Embed documents using the encoder model."""
        if self.encoder is None:
            raise Exception("Encoder model is not initialized.")

        all_embeddings = []
        for doc in docs:
            # Predict using the encoder model for each document
            response = self.encoder.predict({'inputs': doc})
            # Assuming the response contains the embedding directly
            embeddings = response['vectors']
            all_embeddings.append(embeddings)

        # Convert embeddings to a NumPy array
        return np.array(all_embeddings)

    def construct_context(self, contexts: List[str], max_section_len=1000) -> str:
        """Construct a context string from a list of contexts."""
        chosen_sections = []
        chosen_sections_len = 0

        for text in contexts:
            text = text.strip()
            chosen_sections_len += len(text) + 2
            if chosen_sections_len > max_section_len:
                break
            chosen_sections.append(text)

        concatenated_doc = "\n".join(chosen_sections)
        return concatenated_doc

    def rag_query(self, question_text: str, index, prompt_template) -> str:
        """Perform a Retrieval-Augmented Generation query."""
        query_vec = self.embed_docs([question_text])[0]
        res = index.query(query_vec, top_k=5, include_metadata=True)
        contexts = [match.metadata['text'] for match in res.matches]
        context_str = self.construct_context(contexts)
        text_input = prompt_template.replace("{context_text}", context_str).replace("{question_text}", question_text)
        out = self.llm.predict({"inputs": text_input})
        return out[0]["generated_text"]
    
    def process_and_upload_data(self, index_name, batch_size=10, vector_limit=1000):
        """Process the data and upload it to Pinecone."""
        if index_name in pinecone.list_indexes():
            pinecone.delete_index(index_name)

        # Create Pinecone index
        pinecone.create_index(
            name=index_name,
            dimension=self.embed_docs(["sample text"])[0].shape[0],
            metric='cosine'
        )
        # Wait for index to finish initialization
        while not pinecone.describe_index(index_name).status['ready']:
            time.sleep(1)

        # Process data in batches
        answers = self.df_knowledge[:vector_limit]
        index = pinecone.Index(index_name)

        for i in tqdm(range(0, len(answers), batch_size)):
            i_end = min(i + batch_size, len(answers))
            ids = [str(x) for x in range(i, i_end)]
            metadatas = [{'text': text} for text in answers["Answer"][i:i_end]]
            texts = answers["Answer"][i:i_end].tolist()
            embeddings = self.embed_docs(texts)
            records = zip(ids, embeddings, metadatas)
            index.upsert(vectors=records)

    def create_sagemaker_endpoint(endpoint_name, model_name):
        sagemaker_client = boto3.client('sagemaker')

        # Hardcode the model name based on your manual verification
        hardcoded_model_name = "flan-t5-model"  # Replace with your actual model name

        # Create the endpoint configuration
        try:
            endpoint_config_name = endpoint_name + "-config"
            sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[
                    {
                        'VariantName': 'AllTraffic',
                        'ModelName': hardcoded_model_name,
                        'InitialInstanceCount': 1,
                        'InstanceType': 'ml.g5.4xlarge',
                        'InitialVariantWeight': 1
                    }
                ]
            )
        except ClientError as e:
            print(f"Error creating endpoint configuration: {e}")
            return

        # Create the endpoint
        try:
            sagemaker_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            print(f"Endpoint '{endpoint_name}' creation initiated.")
        except ClientError as e:
            print(f"Error creating endpoint: {e}")



            
