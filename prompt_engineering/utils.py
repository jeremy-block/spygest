# write a parser for parsing superlatives from a manifest file given the file path, the manifest file is a json file, and save the results to a User class
import json
import openai
import tiktoken
import difflib
import os
from dotenv import load_dotenv
import evaluate
from datasets import load_metric
# import load
# import tensorflow as tf
# print(tf.__version__)

load_dotenv(dotenv_path=".env/api_key.py")
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def load_json_to_dict(file_path):
    with open(file_path, "r") as f:
        res = json.load(f)
    return res

def save_dict_to_json(dict_to_save, folder_name=None, filename=None) -> None:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # write the snapshot to a file named "filemane.json" in the folder we just created
    with open(os.path.join(folder_name, filename + '.json'), 'w') as f:
        json.dump(dict_to_save, f)

def highlight_differences(text1, text2):
    diff = difflib.ndiff(text1.split(), text2.split())
    differences = [part for part in diff if part.startswith('-') or part.startswith('+')]
    highlighted_text = []
    for difference in differences:
        # if difference.startswith('-'):
        #     highlighted_text.append(f"[-{difference[1:]}-]")  # Enclose removed parts in square brackets
        # elif difference.startswith('+'):
        #     highlighted_text.append(f"[+{difference[1:]}+]")  # Enclose added parts in square brackets
        if difference.startswith('-'):
            highlighted_text.append(f"\033[91m{difference}\033[0m")  # Highlight removed parts in red
        elif difference.startswith('+'):
            highlighted_text.append(f"\033[92m{difference}\033[0m")  # Highlight added parts in green
    return ' '.join(highlighted_text)

def run_evaluate(predictions, references, metrics):
    results = None
    if metrics == "rouge":
        rouge = evaluate.load('rouge')
        results = rouge.compute(predictions=predictions, references=references)
    elif metrics == "bleu":
        bleu = evaluate.load('bleu')
        results = bleu.compute(predictions=predictions, references=references)
    elif metrics == "bleurt":
        # bleurt = evaluate.load("bleurt")
        bleurt = load_metric('bleurt', 'bleurt-large-512')
        results = bleurt.compute(predictions=predictions, references=references)
    elif metrics == "ter":
        ter = evaluate.load('ter')
        results = ter.compute(predictions=predictions, references=references)
    else:
        raise NotImplementedError(f"The metric {metrics} is not implemented.")
    print(results)
    return results
