from mmx_engineering_spec_manager.models.prompt_model import PromptModel


class SpecificationGroupModel:
    def __init__(self, data):
        self.name = data.get("Name")

        # Explicitly handle the 'Global' prompts
        global_prompts_data = data.get("Global", {}).get("Prompts", [])
        self.global_prompts = [PromptModel(prompt_data) for prompt_data in global_prompts_data]

        # Explicitly handle the 'Wizard' prompts
        wizard_prompts_data = data.get("Wizard", {}).get("Prompts", [])
        self.wizard_prompts = [PromptModel(prompt_data) for prompt_data in wizard_prompts_data]