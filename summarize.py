import openai
import tiktoken
import json
import math
import collections
from datasets import load_metric

openai.api_key = "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"
_FILE_PATH = "./data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json"
_MAX_TOKEN = 3072
_PID = "P1"

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
        {"role": "user", "content": (_PID + " " + ", ".join(res))}
    ]
    return num_tokens_from_messages(messages)

def get_final_summary(summaries):
    # summaries = ['The user is searching through multiple documents to find a connection between a disease that began in Nigeria in 2011 and arms dealing in Nigeria and Kenya. They are looking for information about gun dealers in those countries and trying to find a link between illegal arms trade and the disease.', 'The user is searching through various documents related to weapons, sickness, and conversations between people with different names, trying to find connections and order the information by dates. They highlight important dates and make notes on the documents. They shift between top-down and bottom-up approaches to find relevant information.', 'The person is searching through various documents, trying to find information about a disease. They come across a document that mentions Dubai and start to suspect that there may be a connection between the disease and illegal arms trafficking. The person searches for certain names and phone numbers and makes connections between different documents. They also focus on finding information about textbooks which they suspect are being used as a cover for arms deals. The person highlights and connects different parts of the documents to piece together the information they need.', 'The person is trying to find information about a disease outbreak that occurred in a meeting held in Borj Al Arab, Dubai in April 2009, which resulted in some of the attendees being hospitalized. They are analyzing various documents related to arms dealing, highlighting important names and locations, and trying to connect the dots to identify how the disease was transmitted.', 'The user is reading various documents related to an arms deal and is searching for evidence to link a Nigerian guy who was in Dubai to a disease outbreak. They connect documents and notes together to form a clear picture of the situation and also investigate other countries that attended the meeting.']
    summaries = " ".join(summaries)
    statistics = get_statistics()
    # messages=[
    #     {"role": "system", "content": "You are a spy. Your task is to summarize an investigation."},
    #     {"role": "assistant", "content": statistics},
    #     {"role": "user", "content": summaries}
    # ]
    messages=[
        {"role": "system", "content": "You are ChatGPT. Your task is to summarize an investigation."}, # slightly different prompt
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


def get_sentences(logs, start_ix, token_limit, doc_ref):
    # starting_text = ""
    # if start_ix == 0:
    #     starting_text = "P1 "
    # else:
    #     starting_text = "Next, P1 "
    doc_logs = get_logs("./dataset1_doc_summary.json")
    res = []
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": (_PID + " " + ", ".join(res))}
    ]
    log_ix = start_ix
    while num_tokens_from_messages(messages) < token_limit:
        log = logs[log_ix]
        res.append(log["summary"])
        content = _PID + " " + ", ".join(res)
        if log["interactionType"] == "Reading" and log["id"] in doc_ref:
            content += ". The content of the document is: " + doc_logs[int(log["id"][11:])]["summary"]
            # print(log_ix)
            # print(log["summary"])
            # print("The content of the document is: " + doc_logs[int(log["id"][11:])]["summary"])
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
            {"role": "user", "content": content}
        ]
        log_ix += 1
    return _PID + " " + ", ".join(res), log_ix-1

def get_statistics():
    supers = get_logs("./original_web_interface/ApplicationManifest.json")["superlatives"][0][0]
    return (f'They focused on {supers["topicCount"]} main topics in this analysis session,' + 
            f'exploring {round(100 * supers["dataCoverage"])} of the dataset.' + 
            f'The topics that received the most attention were {supers["topics"]}.' +  
            f'They started searching for {supers["breakpointSearches"][0]}, before transitioning to {supers["breakpointSearches"][1]} and finally looking for {supers["breakpointSearches"][2]}.' + 
            f'They conducted {supers["searchCount"]} searches throughout their session.')

def evaluate(type, user, summary):
    """
    Argument
    - type
      - "rouge"
      - "sacrebleu"
    - user
      - p1, p2, p3
    """
    manual_logs = get_logs("./dataset1_doc_manual.json")
    for s in manual_logs["manualSummaries"]:
        if s["user"] == user:
            manual = s["summary"]
    metric = load_metric(type)
    predictions = [summary]
    references = [manual]
    print(references)
    if type == "rouge":
        # rouge = load_metric(type)
        # predictions = ["The cat scratched the dog"]
        # references = []
        print(metric.compute(predictions=predictions, references=references))
    elif type == "sacrebleu":
        # SacreBLEU operates on raw text, not tokens
        # sacrebleu = load_metric("sacrebleu")
        # predictions = ["I have thirty six years"]
        # references = [["I am thirty six years old", "I am thirty six"]]
        print(metric.compute(predictions=predictions, references=references))
    pass

def get_topics(doc_ref):
    """
    Argument
    - doc_ref: the documents to focus on
    """
    entity_logs = get_logs("./dataset1_doc_topics.json")
    entities = []
    for id in doc_duration:
        # doc_id = sorted_doc_duration[i][0]
        for log in entity_logs:
            if log[0]["id"] == id:
                # print(log[0].keys())
                for k, v in log[0].items():
                    if k != 'id' and k != 'DATE' and k != 'TIME':
                        entities += v
    entity_content = "the user focused on these named entities: " + ",".join(entities)
    pass

def get_entities(filename):
    """
    CARDINAL: Numerals that do not fall under another type.
    DATE: Absolute or relative dates or periods.
    EVENT: Named hurricanes, battles, wars, sports events, etc.
    FAC: Buildings, airports, highways, bridges, etc.
    GPE: Countries, cities, states.
    LANGUAGE: Any named language.
    LAW: Named documents made into laws.
    LOC: Non-GPE locations, mountain ranges, bodies of water.
    MONEY: Monetary values, including unit.
    NORP: Nationalities or religious or political groups.
    ORDINAL: "first", "second", etc.
    ORG: Companies, agencies, institutions, etc.
    PERCENT: Percentage, including "%".
    PERSON: People, including fictional.
    PRODUCT: Objects, vehicles, foods, etc. (Not services.)
    QUANTITY: Measurements, as of weight or distance.
    TIME: Times smaller than a day.
    WORK_OF_ART: Titles of books, songs, etc.
    """
    entity_logs = get_logs(filename)
    id = "armsdealing1"
    # print(logs[0][0])
    interaction_logs = get_logs(_FILE_PATH)
    longest_duration = 0
    longest_reading_ix = -1
    for ix, log in enumerate(interaction_logs):
        if log["interactionType"] == "Reading":
            pass
            # if log["duration"] > longest_duration:
            #     longest_duration = log["duration"]
            #     longest_reading_ix = ix
    # print(f"the doc the user spend the most time on: {interaction_logs[longest_reading_ix]['id']}")

    """
    - get the top 3 entities that are most focused on
    - top 3 docs the user spend the most time on (accumulated)
    """
    doc_duration = collections.defaultdict(int)
    doc_count = collections.defaultdict(int)
    for ix, log in enumerate(interaction_logs):
        if log["interactionType"] == "Reading":
            doc_duration[log["id"]] += log["duration"]
            doc_count[log["id"]] += 1
    # sorted_doc_duration = dict(sorted(doc_duration.items(), key=lambda item: item[1], reverse=True))
    sorted_doc_duration = sorted(doc_duration.items(), key=lambda item: item[1], reverse=True)
    sorted_doc_count = sorted(doc_count.items(), key=lambda item: item[1], reverse=True)
    # print(sorted_doc_duration)
    interaction_entities = collections.defaultdict(list)
    doc_duration_id = []
    doc_count_id = []
    for i in range(3):
        doc_id = sorted_doc_duration[i][0]
        doc_duration_id.append(sorted_doc_duration[i][0])
        doc_count_id.append(sorted_doc_count[i][0])
        for log in entity_logs:
            if log[0]["id"] == doc_id:
                # print(log[0].keys())
                for k, v in log[0].items():
                    if k != 'id' and k != 'DATE':
                        interaction_entities[k] += v
    # print(sorted_doc_duration)
    # print(sorted_doc_count)
    # print(interaction_entities)
    return doc_duration_id, doc_count_id

    """
    top 3 docs the user visited the most often
    """

def get_doc_with_summary(filename):
    logs = get_logs(filename)
    print(logs[0]["summary"])
    pass


if __name__ == "__main__":
    evaluate("rouge", "p1", "")
    evaluate("rouge", "p2", "")
    evaluate("rouge", "p3", "")

    doc_duration, doc_count = get_entities("./data/Dataset_1/Documents/Entities_Dataset1_BERT.json")
    print(doc_duration)
    print(doc_count)
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
    # get entities
    entity_logs = get_logs("./data/Dataset_1/Documents/Entities_Dataset1_BERT.json")
    entities = []
    for id in doc_duration:
        # doc_id = sorted_doc_duration[i][0]
        for log in entity_logs:
            if log[0]["id"] == id:
                # print(log[0].keys())
                for k, v in log[0].items():
                    if k != 'id' and k != 'DATE' and k != 'TIME':
                        entities += v
    entity_content = "the user focused on these named entities: " + ",".join(entities)
    print(f"The message that includes named entities: {entity_content}")
    for seg_ix in range(segment_num):
        print(f"summarizing segment #{seg_ix+1}")
        print(f"starting from log#{start_ix}")
        sentences, ix = get_sentences(logs, start_ix, tokens_per_segment, doc_duration)
        # print(sentences)
        print(f"summarized up to log #{ix}")
        start_ix = ix + 1
        # if summaries:
        #     messages=[
        #         {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        #         {"role": "assistant", "content": " ".join(summaries)},
        #         {"role": "user", "content": sentences}
        #     ]
        # else:
        #     messages=[
        #         {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        #         {"role": "user", "content": sentences}
        #     ]
        if summaries:
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible based on the fact that " + entity_content},
                {"role": "assistant", "content": " ".join(summaries)},
                {"role": "user", "content": sentences}
            ]
        else:
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible based on the fact that " + entity_content},
                {"role": "user", "content": sentences}
            ]

        """
        'gpt-3.5-turbo'
        maximum limit: 4096 tokens
        """

        input_tokens = num_tokens_from_messages(messages)
        print(f"the number of input tokens for this segment is {input_tokens}")
        # max_tokens = int((input_tokens * _MAX_TOKEN * 0.99) // tokens_needed)
        # print(f"so the number of output tokens for this segment should be set to {max_tokens}")
        # tokens_total_goal += max_tokens

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
