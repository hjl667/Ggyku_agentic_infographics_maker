from enum import Enum


class PromptBuilder:
    def __init__(self):
        self.prompt = ""

    def get_final_result(self):
        return self.prompt

    def append(self, text: str):
        self.prompt += text