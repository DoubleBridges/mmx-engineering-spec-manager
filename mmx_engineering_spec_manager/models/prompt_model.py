class PromptModel:
    def __init__(self, data):
        self.name = data.get("Name")
        self.value = data.get("Value")