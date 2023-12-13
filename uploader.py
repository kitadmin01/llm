
from transformers import AutoTokenizer, AutoModel
import pinecone


class EmbeddingUploader:
    '''
    This class uploads embeeding to PineCone using Hugging Face open source 
    model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
    '''
    def __init__(self, pinecone_api_key, pinecone_env, index_name, model_name):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        existing_indexes = pinecone.list_indexes()
        if index_name in existing_indexes:
            pinecone.delete_index(index_name)
        pinecone.create_index(index_name, dimension=1024)  
        self.index = pinecone.Index(index_name)

        # Load the specified text embedding model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)


    def read_file_segments(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read all lines from the file
            lines = file.readlines()

        segments = []
        segment = ""
        for line in lines:
            # Check if the line is not just a newline character
            if line.strip():
                # Add the line to the current segment
                segment += line.strip() + " "
            else:
                # If the line is empty and there is a current segment, add it to the segments list
                if segment:
                    segments.append(segment.strip())
                    segment = ""  # Reset the segment

        # Add the last segment if it's not empty
        if segment:
            segments.append(segment.strip())

        return segments


    def generate_embedding(self, text):
        # Adjust the max_length to capture more context if needed
        max_length = 1024  # or another value that works better for your data
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings[0]


    def upload_embeddings(self, file_paths):
        vectors_to_upsert = {}
        for file_type, file_path in file_paths.items():
            segments = self.read_file_segments(file_path)
            for i, segment in enumerate(segments):
                embedding = self.generate_embedding(segment)
                vectors_to_upsert[f"{file_type}_{i}"] = {
                    "values": embedding.tolist(),
                    "metadata": {"text": segment, "type": file_type}
                }

        self.batch_upsert(vectors_to_upsert)

    def batch_upsert(self, data):
        batch_size = 100  # Recommended upsert limit
        for i in range(0, len(data), batch_size):
            batch_data = [(k, v['values'], v['metadata']) for k, v in list(data.items())[i:i + batch_size]]
            self.index.upsert(vectors=batch_data)





if __name__ == "__main__":
    pinecone_api_key = "58f14d8c-0dad-469f-9528-81fca0a063ad"
    pinecone_env = "gcp-starter"
    pincone_index = "kit"
    model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"

    uploader = EmbeddingUploader(pinecone_api_key, pinecone_env, pincone_index, model_name)
    path = "./aikit/content/"
    file_paths = {
        "faq": path + "faq.txt",
        "tool_use": path + "tool_use.txt",
        "tool_concept": path + "tool_concept.txt"
    }

    uploader.upload_embeddings(file_paths)