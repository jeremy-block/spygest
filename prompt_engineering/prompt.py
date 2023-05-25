def collect_messages():
    """
    messages=[
                {"role": "system", "content": ""},
                {"role": "assistant", "content": ""},
                {"role": "user", "content": ""},
                {"role": "assistant", "content": ""},
                {"role": "user", "content": ""},
                ...
            ]
    """

def get_system_message():
    """
    return a system message
    - task: Your task is to [generate a summary of]/[extract relevant information from] the interaction logs of a user who was trying to [investigate an event in the intelligence domain] written in sentences [of the format: ]. 
        - [The goal is to communicate findings and progress in a collaborative investigation scenario]
        - number of sentences/words
        - with a focus on ...
    - style: conversational
    - tone: assertive vs. non-assertive (suggestive)
    - length: short (concise) vs. long (verbose)
    - persona: manager vs. peer
    - steps
        - 
    """

def get_user_message():
    """
    return a user message
    - delimiter
    """