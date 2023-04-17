import openai
import tiktoken
import json
import math
import collections
from datasets import load_metric
import evaluate

"""
Named Entities:
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

openai.api_key = "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"
_FILE_PATH = ["./data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json", "./data/Dataset_1/User Interactions/Arms_P2_InteractionsLogs.json", "./data/Dataset_1/User Interactions/Arms_P3_InteractionsLogs.json"]
_MAX_TOKEN = 3072 #2048
_PID = "P1" #P2 #P3
_PIDS = ["P1", "P2", "P3"]
_EVAL_TYPES = ["rouge", "bleu"]
_PROMPT = "topic" #ner #topic
_DOC_TYPE = "duration" #frequency #both
_ITERS = 3

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

def get_tokens(logs, pid):
    res = []
    for log in logs:
        res.append(log["summary"])
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": (pid + " " + ", ".join(res))}
    ]
    return num_tokens_from_messages(messages)

def get_final_summary(summaries, pid, prompt):
    print(f"{[get_final_summary.__qualname__]} Get final summary for {pid}")
    summaries = " ".join(summaries)
    print(summaries)
    
    ## Persona
    # behavior_example = "A spy's behavior involves establishing a cover identity, building relationships with sources, and collecting and transmitting information to their handlers while maintaining secrecy to avoid detection. Espionage is illegal and unethical, and the consequences for being caught can be severe."
    # messages=[
    #     {"role": "system", "content": "You are a spy. Your task is to summarize an investigation."},
    #     {"role": "assistant", "content": behavior_example},
    #     {"role": "user", "content": summaries}
    # ]

    # ## statistics
    # statistics = get_statistics(pid)
    # print(statistics)
    # messages=[
    #     {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
    #     {"role": "assistant", "content": statistics},
    #     {"role": "user", "content": summaries}
    # ]

    ## NER or topics
    print(prompt)
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible based on the fact that " + prompt},
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
    return response.choices[0].message.content


def get_sentences(logs, start_ix, token_limit, pid, doc_ref):
    # starting_text = ""
    # if start_ix == 0:
    #     starting_text = "P1 "
    # else:
    #     starting_text = "Next, P1 "
    print(f"[{get_sentences.__qualname__}] Get sentences for {pid}")
    doc_logs = get_logs("./dataset1_doc_summary.json")
    res = []
    messages=[
        {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
        {"role": "user", "content": (pid + " " + ", ".join(res))}
    ]
    log_ix = start_ix
    while num_tokens_from_messages(messages) < token_limit:
        log = logs[log_ix]
        res.append(log["summary"])
        content = pid + " " + ", ".join(res)
        if doc_ref:
            if log["interactionType"] == "Reading" and log["id"] in doc_ref:
                content += ". The content of the document is: " + doc_logs[int(log["id"][11:])]["summary"]
            # print(log_ix)
            # print(log["summary"])
            print("The content of the document is: " + doc_logs[int(log["id"][11:])]["summary"])
        messages=[
            {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible."},
            {"role": "user", "content": content}
        ]
        log_ix += 1
    return pid + " " + ", ".join(res), log_ix-1

def get_statistics(pid):
    print(f"[{get_statistics.__qualname__}] Getting statistics for {pid}")
    ix = 0
    if pid == "P2":
        ix = 1
    elif pid == "P3":
        ix = 2
    supers = get_logs("./original_web_interface/ApplicationManifest.json")["superlatives"][0][ix]
    return (f'They focused on {supers["topicCount"]} main topics in this analysis session,' + 
            f'exploring {round(100 * supers["dataCoverage"])}% of the dataset.' + 
            f'The topics that received the most attention were {supers["topics"]}.' +  
            f'They started searching for {supers["breakpointSearches"][0]}, before transitioning to {supers["breakpointSearches"][1]} and finally looking for {supers["breakpointSearches"][2]}.' + 
            f'They conducted {supers["searchCount"]} searches throughout their session.')

def run_evaluate(type, user, summary):
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
        if s["user"] == user.lower():
            manual = s["summary"]
    # metric = load_metric(type)
    metric = evaluate.load(type)
    predictions = [summary]
    references = [manual]
    print(references)
    res = 0
    if type == "rouge":
        # rouge = load_metric(type)
        # predictions = ["The cat scratched the dog"]
        # references = []
        rouge_score = metric.compute(predictions=predictions, references=references)
        print(rouge_score)
        rouge_1 = rouge_score["rouge1"]
        print(rouge_1)
        res = rouge_1
    elif type == "bleu":
        bleu_score = metric.compute(predictions=predictions, references=[references])
        print(bleu_score)
        bleu_1_precision = bleu_score['precisions'][0]
        print(bleu_1_precision)
        res = bleu_1_precision
    elif type == "sacrebleu":
        # SacreBLEU operates on raw text, not tokens
        # sacrebleu = load_metric("sacrebleu")
        # predictions = ["I have thirty six years"]
        # references = [["I am thirty six years old", "I am thirty six"]]
        print(metric.compute(predictions=predictions, references=[references]))
    return res

def get_topics(doc_ref):
    """
    Argument
    - doc_ref: the documents to focus on
    """
    topic_logs = get_logs("./dataset1_doc_topics.json")
    topics = []
    for id in doc_ref:
        # doc_id = sorted_doc_duration[i][0]
        for log in topic_logs:
            if log["id"] == id:
                # print(log[0].keys())
                topics.append(log["topic"])
                # print(log["topic"])
    topics_content = "the user focused on these topics:\n" + "\n".join(topics)
    return topics_content

def get_docs(pid):
    ix = 0
    if pid == "P2":
        ix = 1
    elif pid == "P3":
        ix = 2
    print(f"[get_docs] Get logs for {pid} from {_FILE_PATH[ix]}")
    interaction_logs = get_logs(_FILE_PATH[ix])

    """
    - get the top 3 entities that are most focused on
    - top 3 docs the user spend the most time on (accumulated)
    """
    doc_duration = collections.defaultdict(int)
    doc_count = collections.defaultdict(int)
    for log in interaction_logs:
        if log["interactionType"] == "Reading":
            doc_duration[log["id"]] += log["duration"]
            doc_count[log["id"]] += 1
    sorted_doc_duration = sorted(doc_duration.items(), key=lambda item: item[1], reverse=True)
    sorted_doc_count = sorted(doc_count.items(), key=lambda item: item[1], reverse=True)
    doc_duration_id = []
    doc_count_id = []
    for i in range(3):
        doc_duration_id.append(sorted_doc_duration[i][0])
        doc_count_id.append(sorted_doc_count[i][0])
    return doc_duration_id, doc_count_id

    """
    top 3 docs the user visited the most often
    """

def get_doc_with_summary(filename):
    logs = get_logs(filename)
    print(logs[0]["summary"])

def summarize(pid):
    """
    Argument
    - 
    Return
    - (rouge-1, bleu-1)
    """
    print(f"Summarize and evaluate for {pid}")
    ## get docs
    doc_duration, doc_count = get_docs(pid)
    print(doc_duration)
    print(doc_count)

    ## get topics
    # topic_content = get_topics(doc_duration)
    # print(f"The message that includes topics: {topic_content}")

    ## get entities
    entity_logs = get_logs("./data/Dataset_1/Documents/Entities_Dataset1_BERT.json")
    entities = []
    for id in doc_duration:
        # doc_id = sorted_doc_duration[i][0]
        for log in entity_logs:
            if log[0]["id"] == id:
                for k, v in log[0].items():
                    if k != 'id' and k != 'DATE' and k != 'TIME':
                        entities += v
    entity_content = "the user focused on these named entities: " + ",".join(entities)
    print(f"The message that includes named entities: {entity_content}")
    log_ix = 0
    if pid == "P2":
        log_ix = 1
    elif pid == "P3":
        log_ix = 2
    print(f"[get_docs] Get logs for {pid} from {_FILE_PATH[log_ix]}")
    logs = get_logs(_FILE_PATH[log_ix])
    tokens_needed = get_tokens(logs, pid)
    segment_num = math.ceil(tokens_needed / _MAX_TOKEN)
    tokens_per_segment = tokens_needed // segment_num
    # print(f"number of segments: {segment_num}")
    # print(f"number of tokens per input segment {tokens_per_segment}")
    summaries = []
    start_ix = 0
    prompt = entity_content # topic_content, entity_content, None
    # if _PROMPT == "ner":
    #     prompt = entity_content
    # elif _PROMPT == "topic":
    #     prompt = topic_content
    print(f"prompting ChatGPT with '{prompt}' as the system message")
    
    for seg_ix in range(segment_num):
        print(f"summarizing segment #{seg_ix+1}")
        print(f"starting from log#{start_ix}")
        sentences, ix = get_sentences(logs, start_ix, tokens_per_segment, pid, None) # doc_duration, None
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
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible based on the fact that " + prompt},
                {"role": "assistant", "content": " ".join(summaries)},
                {"role": "user", "content": sentences}
            ]
        else:
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI. Summarize as concisely as possible based on the fact that " + prompt},
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
        
        # generated = response.usage.completion_tokens
        # print(f"generated {generated} tokens")
        # tokens_total_gen += generated
    
        summaries.append(response.choices[0].message.content)
    # print(f"should generated a total of {tokens_total_goal} tokens")
    # print(f"generated a total of {tokens_total_gen} tokens")
    print(summaries)
    final_sum = get_final_summary(summaries, pid, prompt)
    res = collections.defaultdict(float)
    for eval_type in _EVAL_TYPES:
        print(f"Evaluation using {eval_type}")
        res[eval_type] = (run_evaluate(eval_type, pid, final_sum))
        # run_evaluate(eval_type, pid, final_sum)
    return res

if __name__ == "__main__":
    rouge_1 = 0
    bleu_1 = 0
    for _ in range(_ITERS):
        for pid in _PIDS:
            print(f"Summarize and evaluate for {pid}")
            results = summarize(pid)
            print(f"results: {results}")
            rouge_1 += results["rouge"]
            bleu_1 += results["bleu"]
    print(f"ROUGE-1: {rouge_1/(len(_PIDS)*_ITERS)}")
    print(f"BLEU-1: {bleu_1/(len(_PIDS)*_ITERS)}")
