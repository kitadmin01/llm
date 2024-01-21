import numpy as np
import sagemaker

class EmbeddingCreator:
    def __init__(self, encoder_model_predictor):
        self.encoder = encoder_model_predictor
        # Ensure the encoder's serializer is JSONSerializer
        self.encoder.serializer = sagemaker.serializers.JSONSerializer()

    def embed_docs(self, docs):
        all_embeddings = []

        # Directly send the list of documents as the payload
        try:
            response = self.encoder.predict(docs)
            embeddings = response  # Adjust based on your model's response format
            if embeddings:
                all_embeddings.extend(embeddings)
        except Exception as e:
            print(f"Error in making prediction. Error: {e}")
            raise Exception("No embeddings were generated due to errors.")

        return np.array(all_embeddings)
