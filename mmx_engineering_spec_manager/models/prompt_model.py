class PromptModel:
    def __init__(self, data):
        self.name = data.get("Name")
        self.value = data.get("Value")
        self.nested_prompt = None

        if "Prompt" in data:
            self.nested_prompt = PromptModel(data["Prompt"])