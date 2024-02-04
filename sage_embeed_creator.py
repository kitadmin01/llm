from transformers import AutoTokenizer
from typing import List
import json
import numpy as np

import json

# EmbeddingCreator is a class designed to generate embeddings for a list of documents.
# It utilizes a specified encoder model for generating embeddings and the Hugging Face AutoTokenizer
# for tokenizing the documents. The class provides a method to convert a list of textual documents
# into a list of numerical embeddings that represent the semantic content of each document.
# This is useful for tasks like document similarity, clustering, or as input features for machine learning models.
class EmbeddingCreator:
    def __init__(self, encoder_model_predictor, model_name):
        # Initializes the EmbeddingCreator with a specific encoder model and tokenizer.
        self.encoder = encoder_model_predictor
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def embed_docs(self, docs: List[str]) -> List[List[float]]:
        # Generates embeddings for a list of documents.
        all_embeddings = []

        for doc in docs:
            # Tokenize the document using the pre-initialized tokenizer.
            inputs = self.tokenizer(doc, return_tensors="pt")

            # Convert tokenized input to lists for processing.
            inputs_to_list = {key: value.tolist() for key, value in inputs.items()}

            # Prepare the payload, ensuring it's not double-serialized.
            payload = {"inputs": inputs_to_list}

            try:
                # Use the encoder model to predict embeddings and average them to get a single embedding per document.
                response = self.encoder.predict(payload)
                embeddings = np.mean(np.array(response), axis=1)
                all_embeddings.append(embeddings.tolist())
            except Exception as e:
                # Handle any errors that occur during the embedding process.
                print(f"Error in embedding document: {e}")

        if not all_embeddings:
            # Raise an exception if no embeddings were generated, indicating a failure in the process.
            raise Exception("No embeddings were generated due to errors.")

        return all_embeddings
