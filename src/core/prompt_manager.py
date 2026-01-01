"""Prompt manager with simple template lookup"""

class PromptManager:
    def __init__(self):
        self.templates = {
            "rag_qa": "Answer the question using the following context:\n{context}\n\nQuestion: {question}\n"
        }

    def get_template(self, name: str):
        return self.templates.get(name)


prompt_manager = PromptManager()
