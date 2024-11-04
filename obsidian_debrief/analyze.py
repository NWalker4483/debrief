import instructor
import obsidiantools.api as otools
from openai import OpenAI
from pydantic import BaseModel

# Import our previously defined models and prompt
from obsidian_debrief.actions import ActionExecutor, LLMAction
from obsidian_debrief.prompts.system import SYSTEM_PROMPT


class ActionList(BaseModel):
    list_: LLMAction


def test_vault_action(vault_path: str, user_request: str) -> list[LLMAction]:
    # Initialize vault connection
    vault = otools.Vault(vault_path).connect().gather()

    # Create context about current vault state
    vault_context = f"""
    Current vault state:
    - Total files: {len(vault.md_file_index)}
    - Project files: {sum(1 for f in vault.md_file_index if '#project' in ' '.join(vault.get_tags(f)))}
    - Available project files: {[f for f in vault.md_file_index.keys() if '#project' in ' '.join(vault.get_tags(f))]}
    """

    # Setup instructor client
    client = instructor.patch(
        OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        ),
        mode=instructor.Mode.JSON,
    )

    # Get LLM response
    response = client.chat.completions.create(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Vault Context:\n{vault_context}\n\nUser Request: {user_request}",
            },
        ],
        response_model=ActionList,
        max_tokens=2000,
        temperature=0.7,
    )

    return response

if __name__ == "__main__":
    VAULT_PATH = "/home/walkenz1/Sync/HomeVault"

    # Initialize action executor
    executor = ActionExecutor(VAULT_PATH)

    # Test cases
    test_requests = [
        "Add a high priority task to review the API documentation, due next week, add it to the Development/Tasks.md file",
        "Mark the task 'Initial research' as complete in Research/Planning.md",
        "Update the main project file Projects/API-Integration.md with a summary of our progress this week",
        "Add a new section called 'Dependencies' to the Technical-Specs.md file",
    ]

    # Run tests
    for request in test_requests:
        print(f"\nTesting request: {request}")
        print("-" * 80)

        # Get actions from LLM
        actions = test_vault_action(VAULT_PATH, request)

        print("\nGenerated Actions:")
        for action in actions:
            print(f"\nAction Type: {action.action_type}")
            print(f"Action Data: {action.action_data}")
            print(f"Reasoning: {action.reasoning}")

            # Validate action
            try:
                print("\nExecuting action...")
                success = executor.execute_action(action)
                print(f"Action {'succeeded' if success else 'failed'}")
            except Exception as e:
                print(f"Error executing action: {e}")

            print("-" * 40)


# Example usage with specific request
def process_user_request(vault_path: str, request: str) -> None:
    """Process a single user request"""
    actions = test_vault_action(vault_path, request)
    executor = ActionExecutor(vault_path)

    print(f"\nProcessing request: {request}")
    for action in actions:
        print(f"\nProposed action: {action.action_type}")
        print(f"Reasoning: {action.reasoning}")

        # Ask for confirmation
        if input("\nExecute this action? (y/n): ").lower() == "y":
            try:
                success = executor.execute_action(action)
                print(f"Action {'succeeded' if success else 'failed'}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Action skipped")


