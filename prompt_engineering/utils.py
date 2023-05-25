# write a parser for parsing superlatives from a manifest file given the file path, the manifest file is a json file, and save the results to a User class
from user import User
import json
import openai
import tiktoken

openai.api_key = "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"

def parse_manifest_file(manifest_file_path):
    with open(manifest_file_path, 'r') as f:
        manifest = json.load(f)
    
    print(manifest["superlatives"][0][0].keys())
    # print(type(manifest["superlatives"][0][0]))
    users = []
    # for user in manifest:
    #     user_obj = User(user['name'], user['superlatives'])
    #     print(user_obj)
    #     user_obj.save_to_db()

    return users

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
#     print(str(response.choices[0].message))
    return response.choices[0].message["content"]

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
    See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

if __name__ == '__main__':
    parse_manifest_file("../original_web_interface/ApplicationManifest.json")