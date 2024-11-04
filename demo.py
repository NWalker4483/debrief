# Interactive usage example:
from obsidian_debrief.analyze import process_user_request


if __name__ == "__main__":
    request = """
    Add a high priority task for the API documentation review with these details:
    - Due next Friday
    - Tag with #documentation and #review
    - Add to the Technical/API/Tasks.md file
    - Put it under the 'Documentation Tasks' section
    """

    process_user_request(VAULT_PATH, request)
