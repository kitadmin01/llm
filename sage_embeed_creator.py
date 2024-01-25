from transformers import AutoTokenizer
from typing import List
import json
import numpy as np

import json

class EmbeddingCreator:
    def __init__(self, encoder_model_predictor, model_name):
        self.encoder = encoder_model_predictor
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def embed_docs(self, docs: List[str]) -> List[List[float]]:
        all_embeddings = []

        for doc in docs:
            # Tokenize the document
            inputs = self.tokenizer(doc, return_tensors="pt")

            # Convert tokenized input to lists
            inputs_to_list = {key: value.tolist() for key, value in inputs.items()}

            # Prepare the payload, ensuring it's not double-serialized
            payload = {"inputs": inputs_to_list}

            try:
                response = self.encoder.predict(payload)
                embeddings = np.mean(np.array(response), axis=1)
                all_embeddings.append(embeddings.tolist())
            except Exception as e:
                print(f"Error in embedding document: {e}")

        if not all_embeddings:
            raise Exception("No embeddings were generated due to errors.")

        return all_embeddings


