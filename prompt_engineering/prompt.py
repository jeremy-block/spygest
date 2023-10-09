from user import User
import utils
import toml
import json
import os
import datetime
import sys

config = toml.load("config.toml")
prompt_config = config["prompt"]
system_config = prompt_config["system"] 
user_config = prompt_config["user"]
adjectives_config = prompt_config["adjectives"]
examples_config = prompt_config["examples"]
audience_config = prompt_config["audience"]

def collect_messages(context=None, system_prompt=None, assistant_prompt=None, user_prompt=None):
    """
    messages=[
                {"role": "system", "content": ""},
                {"role": "assistant", "content": ""},
                {"role": "user", "content": ""},
                {"role": "assistant", "content": "seg1"},
                {"role": "user", "content": ""},
                {"role": "assistant", "content": "seg2"},
                {"role": "user", "content": ""},
                {"role": "assistant", "content": ""},
                {"role": "user", "content": ""},
                ...
            ]
    """
    if assistant_prompt:
        context.append(assistant_prompt)
    if user_prompt:
        context.append(user_prompt)

def get_system_message(user):
    """
    return a system message
    - role
    - task
        - use case
        - domain
        - input format
        - number of segments
        - step bt step
        - reminder: consider previous segments
        - length
        - scenario
    - persona
        - manager: objectivity, relevance, conciseness, clarity
        - peer: engaging, accuracy
        - self: relevance, proper citation, objectivity, engaging, conciseness, coherence, clarity, accuracy
        - none
    """
    prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario."""
    prompt += adjectives_config["none"]
    return {"role": "system", "content": prompt}

def get_user_message(user, segment_num):
    """
    return a segment user message
    - task:
      - Summarize the sentences describing the interactions of segment [#] delimited by triple backticks in at most [number of words/sentences]. 
      - Make sure you take into account summaries of previous segments. 
      - Document: ```{user.interaction_logs[segment_num]}```
    """
    prompt = f"""Summarize the sentences describing the interactions of segment {segment_num} delimited by triple backticks in at most {system_config["long_length"]}. Make sure you take into account summaries of previous segments. Description: ```{user.interaction_logs[segment_num-1]}```"""
    return {"role": "user", "content": prompt}

def get_user_message_final(user, summaries: str):
    """
    return a final user message
    - audience
      - manager
      - peer
      - self
      - none
    - example
      - masked_template
      - manual_example
      - masked_manual_example
      - none
    """
    prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}."""
    # prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}. Summaries: ```{summaries}```"""
    prompt += audience_config["none"] + examples_config["masked_template"] # masked_template, 
    return {"role": "user", "content": prompt}

def process_old_user_msg(msg, segment_num):
    # take the input msg, split by triple backticks, replace the content delimited by triple backticks with "segment {segment_num}"
    modified_content = "```".join(msg["content"].split("```")[:-2] + [f"segment {segment_num}", f""])
    msg["content"] = modified_content
    return msg
    
def save_snapshots(snapshot, folder_name, filename):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    with open(os.path.join(folder_name, filename + '.json'), 'w') as f:
        json.dump(snapshot, f)

def get_segment_summaries(context):
    return [msg["content"] for msg in context if msg["role"] == "assistant"]
    

def print_debugging_info(context, summaries):
    print(f"Last context list:\n {context}")
    print(f"Accumalted summaries:\n {summaries}")

def test_user(user):
    user.parse_manifest()
    user.parse_logs(include_docs=True)
    user.get_interaction_types()
    print(f"Divide the interaction logs into {len(user.interaction_logs)} segments")
    print(f"Interaction types: {user.interaction_types}")
    print(f"Number of interaction types: {len(user.interaction_types)}")
    get_user_message_final(user=user, summaries="")
    get_system_message(user=user)

if __name__ == "__main__":
    user = User('../data/Dataset_1/User Interactions/Arms_P3_InteractionsLogs.json', '../original_web_interface/ApplicationManifest.json', dataset_id=1, user_id=3) # 1-based
    # test_user(user)
    user.parse_manifest()
    user.parse_logs(include_docs=True)
    user.get_interaction_types()
    print(f"Divide the interaction logs into {user.num_segments} segments")

    folder_name = f"snapshots_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    if prompt_config["final"] == "false":
        sys_msg = get_system_message(user)
        assistant_msg = None
        context = [sys_msg]
        segment_summaries = []
        segment_summary = None
        
        ## prompt ChatGPT 
        for segment_num in range(1, user.num_segments+1):
            # Create user message
            user_msg = get_user_message(user, segment_num=segment_num)
            
            # Append the assistant message (could be None) and the user message to the context list
            collect_messages(context=context, assistant_prompt=assistant_msg, user_prompt=user_msg)

            # Save intermediate results
            save_snapshots(context, folder_name=folder_name, filename=f"snapshot_{segment_num}")

            # Check token limit
            token_count = utils.num_tokens_from_messages(messages=context)
            print(f"segment {segment_num}: {token_count}")
            if token_count < 4096:
                segment_summary = utils.get_completion_from_messages(messages=context)
                segment_summaries.append(segment_summary)
                assistant_msg = {"role": "assistant", "content": segment_summary}

                # update the user message to reduce the number of tokens
                old_user_msg = process_old_user_msg(user_msg, segment_num)
                context[-1] = old_user_msg

                if segment_num == user.num_segments:
                    # add the assistant message of the last segment to context and save the final snapshot
                    collect_messages(context=context, assistant_prompt=assistant_msg, user_prompt=None)
                    save_snapshots(context, folder_name=folder_name, filename=f"snapshot_{segment_num}_assistant")
            else:
                print("Accumulated too many tokens!")
                print_debugging_info(context, segment_summaries)
                sys.exit()

    ## Load from existing snapshots if needed
    if prompt_config["final"] == "true":
        final_snapshot_path = "./baseline/snapshots_2023-06-03_23-05-35/snapshot_11_assistant.json"
        context = utils.load_json_to_dict(final_snapshot_path)
        segment_summaries = get_segment_summaries(context)
    
    user_msg_final = get_user_message_final(user, " ".join(segment_summaries))

    ## Including memory or not
    if prompt_config["with_memory"] == "true":
        collect_messages(context=context, user_prompt=user_msg_final)
    elif prompt_config["with_memory"] == "false":
        context = [get_system_message(user)] + [user_msg_final]

    save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final")
    token_count = utils.num_tokens_from_messages(messages=context)
    print(f"Final summary: {token_count}")
    if token_count < 4096:
        overall_summary = utils.get_completion_from_messages(messages=context)
        assistant_msg = {"role": "assistant", "content": overall_summary}
        collect_messages(context=context, assistant_prompt=assistant_msg, user_prompt=None)
        save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final_assistant")
        
        ## Run evaluation
        for metric_type in prompt_config["metrics"]:
            print(f"running metric: {metric_type}")
            scores_manual = utils.run_evaluate([utils.load_json_to_dict("../dataset1_doc_manual.json")["manualSummaries"][2]["summary"]], [overall_summary], metric_type)
            scores_baseline = utils.run_evaluate([utils.load_json_to_dict("./p3/none_none/snapshot_final_assistant.json")[-1]["content"]], [overall_summary], metric_type)
            scores_baseline_summaries = utils.run_evaluate([utils.load_json_to_dict("./p3/none_summaries/snapshot_final_assistant.json")[-1]["content"]], [overall_summary], metric_type)
            context.append(scores_manual)
            context.append(scores_baseline)
            context.append(scores_baseline_summaries)
        save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final_assistant_with_scores")
    else:
        print("Accumulated too many tokens!")
        print_debugging_info(context, segment_summaries)
    print(overall_summary)
