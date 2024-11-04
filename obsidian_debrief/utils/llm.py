def validate_llm_response(response_text: str) -> List[LLMAction]:

    # Parse JSON response
    import json
    actions_data = json.loads(response_text)

    # Handle single action or list of actions
    if isinstance(actions_data, dict):
        actions_data = [actions_data]

    # Validate each action
    validated_actions = []
    for action_data in actions_data:
        action = LLMAction(**action_data)
        validated_actions.append(action)

    return validated_actions

def structured_generation():
    pass