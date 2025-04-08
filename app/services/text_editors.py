from transformers import pipeline, AutoTokenizer

from abc import abstractmethod


class TextEditor:

    @abstractmethod
    def edit(self, text: str) -> str:
        pass


class HFTextEditor(TextEditor):

    def __init__(self):
        self.model_name = "prithivida/grammar_error_correcter_v1"
        self.model = pipeline("text2text-generation", model=self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def edit(self, text: str) -> tuple[str, int]:
        result = self.model(text)[0]["generated_text"]

        input_tokens = self.tokenizer.encode(text, return_tensors="pt")
        output_tokens = self.tokenizer.encode(result, return_tensors="pt")
        num_tokens = input_tokens.shape[1] + output_tokens.shape[1]

        return result, num_tokens
