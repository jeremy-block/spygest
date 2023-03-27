import openai
import tiktoken
import json
import math

openai.api_key = "API_KEY"
_FILE_PATH = "./data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json"
_MAX_TOKEN = 2048

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

def get_logs(file_path):
    with open(file_path, "r") as read_file:
        data = json.load(read_file)
    return data

def get_tokens(logs):
    res = []
    for log in logs:
        res.append(log["summary"])
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": ("P1 " + ", ".join(res))}
    ]
    return num_tokens_from_messages(messages)

def get_final_summary(summaries):
    # summaries = ['The user is searching through multiple documents to find a connection between a disease that began in Nigeria in 2011 and arms dealing in Nigeria and Kenya. They are looking for information about gun dealers in those countries and trying to find a link between illegal arms trade and the disease.', 'The user is searching through various documents related to weapons, sickness, and conversations between people with different names, trying to find connections and order the information by dates. They highlight important dates and make notes on the documents. They shift between top-down and bottom-up approaches to find relevant information.', 'The person is searching through various documents, trying to find information about a disease. They come across a document that mentions Dubai and start to suspect that there may be a connection between the disease and illegal arms trafficking. The person searches for certain names and phone numbers and makes connections between different documents. They also focus on finding information about textbooks which they suspect are being used as a cover for arms deals. The person highlights and connects different parts of the documents to piece together the information they need.', 'The person is trying to find information about a disease outbreak that occurred in a meeting held in Borj Al Arab, Dubai in April 2009, which resulted in some of the attendees being hospitalized. They are analyzing various documents related to arms dealing, highlighting important names and locations, and trying to connect the dots to identify how the disease was transmitted.', 'The user is reading various documents related to an arms deal and is searching for evidence to link a Nigerian guy who was in Dubai to a disease outbreak. They connect documents and notes together to form a clear picture of the situation and also investigate other countries that attended the meeting.']
    summaries = " ".join(summaries)
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": summaries}
    ]
    print(num_tokens_from_messages(messages))
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
        
    generated = response.usage.completion_tokens
    print(f"generated {generated} tokens")
    print(response.choices[0].message.content)


def get_sentences(logs, start_ix, token_limit):
    # starting_text = ""
    # if start_ix == 0:
    #     starting_text = "P1 "
    # else:
    #     starting_text = "Next, P1 "
    res = []
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": ("P1 " + ", ".join(res))}
    ]
    log_ix = start_ix
    while num_tokens_from_messages(messages) < token_limit:
        log = logs[log_ix]
        res.append(log["summary"])
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
            {"role": "user", "content": ("P1 " + ", ".join(res))}
        ]
        log_ix += 1
    return "P1 " + ", ".join(res), log_ix-1

if __name__ == "__main__":
    logs = get_logs(_FILE_PATH)
    tokens_needed = get_tokens(logs)
    segment_num = math.ceil(tokens_needed / _MAX_TOKEN)
    tokens_per_segment = tokens_needed // segment_num
    print(f"number of segments: {segment_num}")
    print(f"number of tokens per input segment {tokens_per_segment}")
    summaries = []
    start_ix = 0
    tokens_total_goal = 0
    tokens_total_gen = 0
    for seg_ix in range(segment_num):
        print(f"summarizing segment #{seg_ix+1}")
        print(f"starting from log#{start_ix}")
        sentences, ix = get_sentences(logs, start_ix, tokens_per_segment)
        # print(sentences)
        print(f"summarized up to log #{ix}")
        start_ix = ix + 1
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
            {"role": "user", "content": sentences}
        ]

        """
        'gpt-3.5-turbo'
        maximum limit: 4096 tokens
        """

        input_tokens = num_tokens_from_messages(messages)
        print(f"the number of input tokens for this segment is {input_tokens}")
        max_tokens = int((input_tokens * _MAX_TOKEN * 0.99) // tokens_needed)
        print(f"so the number of output tokens for this segment should be set to {max_tokens}")
        tokens_total_goal += max_tokens

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=4096-input_tokens-1
        )
        
        generated = response.usage.completion_tokens
        print(f"generated {generated} tokens")
        tokens_total_gen += generated
    
        summaries.append(response.choices[0].message.content)
    print(f"should generated a total of {tokens_total_goal} tokens")
    print(f"generated a total of {tokens_total_gen} tokens")
    print(summaries)
    get_final_summary(summaries)
    