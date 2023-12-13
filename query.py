
from transformers import AutoTokenizer, AutoModel
import numpy as np
import pinecone

class TextEmbeddingQuery:
    '''
    This class converts user input to embeeding and sends it to Pinecone to get the
    result using Hugging Face open source model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
    '''
    def __init__(self, pinecone_api_key, pinecone_env, index_name, model_name):
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        self.index = pinecone.Index(index_name)

        # Load the text embedding model (BERT fine-tuned for QA)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def generate_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings[0]
    


    def query(self, user_input):
        user_embedding = self.generate_embedding(user_input)
        if isinstance(user_embedding, np.ndarray):
            user_embedding = user_embedding.tolist()

        query_result = self.index.query(
            vector=user_embedding,
            top_k=3,
            include_metadata=True
        )

        # Debug: Print raw query results
        print("Raw Query Results:", query_result)

        # Filter results based on content
        filtered_results = []
        for match in query_result['matches']:
            snippet = match['metadata'].get('text', '')
            if "What is" in snippet or "How" in snippet:  # Adjusted criteria
                filtered_results.append(match)

        result_text = "Query Results:\n"  # Initialize result_text here
        if not filtered_results:  # Fallback to top matches if no filtered results
            for i, match in enumerate(query_result['matches'][:3]):  # Show top 3 matches
                snippet = match['metadata'].get('text', '')
                result_text += f"Match {i+1}: ID = {match['id']}, Score = {match['score']:.6f}, Snippet: {snippet}\n"
        else:
            for i, match in enumerate(filtered_results):
                snippet = match['metadata'].get('text', '')
                result_text += f"Match {i+1}: ID = {match['id']}, Score = {match['score']:.6f}, Snippet: {snippet}\n"

        return result_text



# For local testing
if __name__ == "__main__":
    pinecone_api_key = "58f14d8c-0dad-469f-9528-81fca0a063ad"
    pinecone_env = "gcp-starter"
    pincone_index = "kit"
    model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"

    teq = TextEmbeddingQuery(pinecone_api_key, pinecone_env, pincone_index, model_name)

    # Test with a sample input
    sample_input = "How Secure Are Our Data?"
    result = teq.query(sample_input)
    print(result)