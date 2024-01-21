from typing import List

class QueryProcessor:
    def __init__(self, llm_predictor, index, prompt_template, embedding_creator):
        self.llm = llm_predictor
        self.index = index
        self.prompt_template = prompt_template
        self.embedding_creator = embedding_creator

    def rag_query(self, question_text: str) -> str:
        query_vec = self.embedding_creator.embed_docs([question_text])[0]
        res = self.index.query(query_vec, top_k=5, include_metadata=True)
        contexts = [match.metadata['text'] for match in res.matches]
        context_str = self.construct_context(contexts)
        text_input = self.prompt_template.replace("{context_text}", context_str).replace("{question_text}", question_text)
        out = self.llm.predict({"inputs": text_input})
        return out[0]["generated_text"]

    def construct_context(self, contexts: List[str], max_section_len=1000) -> str:
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
