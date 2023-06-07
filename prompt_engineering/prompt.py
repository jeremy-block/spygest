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

def get_system_message(user, manual_sum=None):
    """
    return a system message
    - "Act as" [an intelligence analyst]
    - task: 
        - your task is to [generate a summary of]/[extract relevant information from] the interaction logs of a user who was trying to [investigate an event in the intelligence domain]. The logs are written in sentences.
        # - the entire interaction is [time of the interaction]
        - The entire interaction session is divided into [number of segments] segments
        - You will be summarizing the entire interaction session [step by step] by summarizing one segment at a time
        - when you are summarizing a segment, make sure you take into account summaries of previous segments
        - Please summarize a segment in at most [number of sentences/words] words
        - with a focus on [dataset theme]
    - persona: manager vs. peer
      - style: conversational (informal) vs. formal
      - tone: assertive vs. non-assertive (suggestive)
      - length: short (concise) vs. long (verbose)
      - [Your audience will be a [manager] who expects the summarization to be short (i.e., concise). The tone should be formal and assertive.]
    - [The goal is to communicate findings and progress in a collaborative investigation scenario]
    # - steps
    #     - [TODO]
    """
    # baseline: prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]} with a focus on {prompt_config["theme"]}. The goal is to communicate findings and progress in a collaborative investigation scenario."""
    # [2023-06-05_12-37-12] without focus: prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario."""
    # [2023-06-05_12-44-39] without focus, with example: prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Here's an EXAMPLE (delimited by triple backticks) of the summarization for an overall interaction session. EXAMPLE: ```{manual_sum}```"""
    # [2023-06-05_12-51-12] without focus, manager style: prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Your audience will be a manager who expects the summarization to be short (i.e., concise). The tone should be formal and assertive."""
    # prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Your audience will be a manager who expects the summarization to be short (i.e., concise). The tone should be formal and assertive."""
    # [core features] prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Please focus on these core features delimited by triple backticks when you summarize: ```relevance, proper citation, objectivity, engaging, conciseness, coherence, clarity, accuracy.```"""
    # [manager] prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Your audience will be a manager who expects the summarization to be relevant, concise, clear, and objective. More specifically, you should follow a list of the instructions delimited by triple backticks: ```1. The tone should be formal and assertive. 2. Please use more descriptive language. 3. Do not focus on the specific statistics but focus on the general behaviors. 4. Please provide a sense of how much work was completed. 5. Please avoid being too vague and overly detailed.```"""
    prompt = f"""Act as {system_config["role"]}, your task is to generate a summary of the interaction logs of a user who was trying to investigate an event in the intelligence domain. The logs are written in sentences. The entire interaction is divided into {user.num_segments} segments. You will be summarizing the entire interaction session step by step by summarizing one segment at a time. When you are summarizing a segment, make sure you take into account summaries of previous segments. Please summarize a segment in at most {system_config["long_length"]}. The goal is to communicate findings and progress in a collaborative investigation scenario. Your audience will be a peer who expects the summarization to be relevant and accurate. The summarization could be less objective. They are more comfortable working with team members’ uncertainty and hedged statements. More specifically, you should follow a list of the instructions delimited by triple backticks: ```1. The tone should be conversational and suggestive. 2. Could be more subjective. 3. Focus more on the specific statistics. 4. Does not need to be concise. 5. Please avoid being too vague and overly detailed.```"""
    # prompt_audience = prompt + " " + "Your audience will be a manager who expects the summarization to be short (i.e., concise). The tone should be formal and assertive."
    # print(prompt)
    # print(prompt_audience)
    return {"role": "system", "content": prompt}
    # return {"role": "system", "content": prompt_audience}

def get_user_message(user, segment_num):
    """
    return a user message
    # - "Act as" [an intelligence analyst]
    - task:
      - Summarize the sentences describing the interactions of segment [#] delimited by triple backticks in at most [number of words/sentences]. 
      - Make sure you take into account summaries of previous segments. 
      - Document: ```{user.interaction_logs[segment_num]}```
    """
    prompt = f"""Summarize the sentences describing the interactions of segment {segment_num} delimited by triple backticks in at most {system_config["long_length"]}. Make sure you take into account summaries of previous segments. Description: ```{user.interaction_logs[segment_num-1]}```"""
    return {"role": "user", "content": prompt}

def get_user_message_final(user, summaries: str, manual_sum=None):
    # baseline: prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}. Summaries: ```{summaries}```"""
    # [2023-06-04_22-00-07] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}, highlighting the key points, outcomes, and any notable insights gained from each session. For example, a list of final conclusions or a set of topics most explored. Summaries: ```{summaries}```"""
    # [2023-06-04_22-17-08] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}, highlighting the key points, outcomes, and any notable insights gained from each session. For example, a list of final conclusions or a set of topics most explored. Please focus on specific dates, names, and keywords most explored. Summaries: ```{summaries}```"""
    # [2023-06-04_22-24-40] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}. Please provide an overall summary that focuses on the key points and main ideas, rather than a step-by-step explanation. For example, a list of final conclusions or a set of topics most explored. Please focus on specific dates, names, and keywords most explored. Summaries: ```{summaries}```"""
    # [2023-06-04_22-29-14] prompt = f"""Please provide a comprehensive summary of the entire interaction in at most {user_config["final_length"]}. Summaries of {user.num_segments} segments are delimited by triple backticks. Please provide an overall summary that focuses on the key points and main ideas, rather than a step-by-step explanation. For example, a list of final conclusions or a set of topics most explored. Please focus on specific dates, names, and keywords most explored. Summaries: ```{summaries}```"""
    # [2023-06-04_22-33-40] prompt = f"""Please provide a comprehensive summary of the entire interaction in at most {user_config["final_length"]}. Please provide an overall summary that focuses on the key points and main ideas, rather than a step-by-step explanation. For example, a list of final conclusions or a set of topics most explored. Please focus on specific dates, names, and keywords most explored. Summaries: ```{summaries}```"""
    # [2023-06-04_22-37-19] prompt = f"""Please provide a comprehensive summary of the entire interaction in at most {user_config["final_length"]}. Please provide an overall summary that focuses on the key points and main ideas, rather than a step-by-step explanation. For example, a list of final conclusions or a set of topics most explored. Please focus on specific dates, names, and keywords most explored."""
    # [2023-06-04_22-43-55] prompt = f"""Please provide a comprehensive summary of the entire interaction in at most {user_config["final_length"]} in a statistical style. For example, They focused on NUMBER main topics in this analysis session, exploring PERCENTAGE of the dataset. The topics that received the most attention were TOPICS. They started searching for KEYWORD1, before transitioning to KEYWORD2 and finally looking for KEYWORD3. They conducted NUMBER searches throughout their session."""
    # [2023-06-05_05-59-59] prompt = f"""Please provide a comprehensive summary of the entire interaction session in at most {user_config["final_length"]} following a similar style shown in the example delimited by triple backticks. Example: ```{manual_sum}```"""
    # [2023-06-07_01-59-02] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}. Summaries: ```{summaries}```"""
    # [2023-06-07_02-06-37] prompt = f"""Please provide a comprehensive summary of the entire interaction session in at most {user_config["final_length"]} following a similar style shown in the example delimited by triple backticks. Example: ```{manual_sum}```"""
    # [2023-06-07_09-46-31] prompt = f"""Please provide a comprehensive summary of the entire interaction in at most {user_config["final_length"]} in a statistical style. For example, They focused on NUMBER main topics in this analysis session, exploring PERCENTAGE of the dataset. The topics that received the most attention were TOPICS. They started searching for KEYWORD1, before transitioning to KEYWORD2 and finally looking for KEYWORD3. They conducted NUMBER searches throughout their session."""
    # [masked template] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}. Please provide the overall summary using the template delimited by triple backticks. Template: ```They focused on [NUMBER] main topics in this analysis session, exploring [PERCENTAGE] of the documents. The topics that received the most attention were [TOPICS]. They started searching for [KEYWORD1], before transitioning to [KEYWORD2] and finally looking for [KEYWORD3]. They conducted NUMBER searches throughout their session. [CONCLUSION]```"""
    # [manual example] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}. Please provide the overall summary based on the example delimited by triple backticks. Example: ```This session began by searching for the word \"Nigeria\" and looking at the documents returned. They noted that Dr. George and Mikhail emailed and then transitioned to searches about \"Kenya\" and the Middle East. At this time, they were reviewing people like Leonid Minsky and Anna Nicole Smith. By the end of the session, they had transitioned to exploring documents from Russia and middle eastern countries. They searched for \"death,\" \"kasem\" and \"dubai.\" In the end, they returned to some of the same documents they had opened at the beginning but also opened many different documents for the first time. Out of the 46 topics and 102 documents, they reviewed 39 topics, opened 45% of the total documents at least once, and spent an average of 30 seconds with each document. The people they returned to most frequently were Leonid Minsky, Mikhail Dombrovski, and Dr. George.```"""
    # [masked manual example] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}. Please provide the overall summary based on the example delimited by triple backticks. Example: ```This session began by searching for [KEYWORD1] and looking at the documents returned. They noted that [KEYWORD2] and [KEYWORD3] emailed and then transitioned to searches about [KEYWORD4] and [KEYWORD5]. At this time, they were reviewing people like [KEYWORD6] and [KEYWORD7]. By the end of the session, they had transitioned to exploring documents from [KEYWORD8] and [KEYWORD9]. They searched for [[KEYWORD10], [[KEYWORD11] and [KEYWORD12]. In the end, they returned to some of the same documents they had opened at the beginning but also opened many different documents for the first time. Out of the [NUMBER] topics and [NUMBER] documents, they reviewed [NUMBER] topics, opened [NUMBER]% of the total documents at least once, and spent an average of [NUMBER] seconds with each document. The people they returned to most frequently were [PERSON1], [PERSON2], and [PERSON3].```"""
    # [manager with summaries] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments delimited by triple backticks in at most {user_config["final_length"]}. Summaries: ```{summaries}```. Your audience will be a manager who expects the summarization to be relevant, concise, clear, and objective. More specifically, you should follow a list of the instructions delimited by triple backticks: ```1. The tone should be formal and assertive. 2. Please use more descriptive language. 3. Do not focus on the specific statistics but focus on the general behaviors. 4. Please provide a sense of how much work was completed. 5. Please avoid being too vague and overly detailed.```"""
    # [sys manager] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments."""
    # [manager final user] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments. Your audience will be a manager who expects the summarization to be relevant, concise, clear, and objective. More specifically, you should follow a list of the instructions delimited by triple backticks: ```1. The tone should be formal and assertive. 2. Please use more descriptive language. 3. Do not focus on the specific statistics but focus on the general behaviors. 4. Please provide a sense of how much work was completed. 5. Please avoid being too vague and overly detailed.```"""
    # [manager final user with masked template] prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}. Please provide the overall summary using the template delimited by triple backticks. Template: ```They focused on [NUMBER] main topics in this analysis session, exploring [PERCENTAGE] of the documents. The topics that received the most attention were [TOPICS]. They started searching for [KEYWORD1], before transitioning to [KEYWORD2] and finally looking for [KEYWORD3]. They conducted NUMBER searches throughout their session. [CONCLUSION].``` Your audience will be a manager who expects the summarization to be relevant, concise, clear, and objective. More specifically, you should follow a list of the instructions delimited by triple backticks: ```1. The tone should be formal and assertive. 2. Please use more descriptive language. 3. Do not focus on the specific statistics but focus on the general behaviors. 4. Please provide a sense of how much work was completed. 5. Please avoid being too vague and overly detailed.```"""
    prompt = f"""Please provide a comprehensive summary of the entire interaction based on the summaries of {user.num_segments} segments in at most {user_config["final_length"]}."""
    # Thought: provide steps (CoT) for the model to follow
    # Thought: we do have three examples, maybe we can try few-shot prompting
    return {"role": "user", "content": prompt}

def process_old_user_msg(msg, segment_num):
    # take the input msg, split by triple backticks, replace the content delimited by triple backticks with "segment {segment_num}"
    modified_content = "```".join(msg["content"].split("```")[:-2] + [f"segment {segment_num}", f""])
    msg["content"] = modified_content
    return msg

def test_prompting(results):
    references_1 = ['The user started investigating the origin of a disease that started in Nigeria in Feb 2011 and spread to other countries. They decided to focus on figuring out the disease first and then investigating arms dealing in these countries to see if there was a connection. They read documents related to arms dealing in Nigeria and Kenya, including an email from an engineer discussing a deal with a foreign company and a blog post about the recovery of 150 guns in Kenya. They searched for information on gun dealers in Nigeria and Kenya and started reading a new blog post about Kenya.', 'In segment 2, the user searched for information on arms dealing in Kenya and Nigeria. They read several documents related to arms dealing in these countries and searched for information on gun dealers. They found a New York Times article from Feb 1st, 2002 about an international gun smuggler in Milan who was arrested by the police. The user tried to find a connection between the smuggler and the disease outbreak in Nigeria. They also connected several documents related to arms dealing in Nigeria and Kenya. The user found some similarities between the information in different documents.', 'In segment 3, the user continued to search for a connection between the disease outbreak and arms dealing in Nigeria and Kenya. They searched for information on gun dealers and found some documents related to arms dealing in these countries. They read an email from a guy in Moscow to an engineer and found some suspicious information. They also found an email from Dr. George and Mikhail and created a note about it. The user connected several documents related to arms dealing in Nigeria and Kenya and found a link between a new document and an old one.', 'In segment 4, the user continued to investigate arms dealing in Nigeria and Kenya. They opened and read several documents related to arms dealing, including armsdealing85, armsdealing97, armsdealing100, armsdealing65, armsdealing84, armsdealing72, armsdealing79, and armsdealing95. They highlighted and reviewed specific dates and information related to gun dealers and arms dealing. The user also read a phone call transcript between Dr. George and a Russian guy and searched for information on weapons and Nigeria and Russia. They found some information related to arms dealing in Nigeria and highlighted a date in armsdealing24.', 'In segment 5, the user continued to search for information on arms dealing and a possible connection to the disease outbreak. They read several documents related to arms dealing in different countries, including Russia, Saudi Arabia, Kenya, and North Korea. They searched for specific keywords related to weapons and illegal activities. The user also reviewed old documents and connected some of them. They highlighted a location in a document related to Pakistan and continued to read it. The user searched for information on the time when the disease first appeared and found a document related to Pakistan.', 'In segment 6, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They searched for information on Dubai and found several documents related to arms dealing in different countries. They highlighted specific keywords related to weapons and illegal activities. The user also reviewed old documents and connected some of them. They found some suspicious information related to textbooks and searched for more information on them. The user connected several documents related to textbooks and found a possible link to arms dealing. They continued to read and connect different documents related to arms dealing and textbooks.', 'In segment 7, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They read several documents related to arms dealing in different countries, including Pakistan, Dubai, and Yemen. They searched for specific keywords related to textbooks, basra, and bukhari. The user also highlighted and reviewed specific dates and information related to transactions and searched for information on the people involved. They found some suspicious information related to a meeting in Dubai and searched for more information on it. The user also searched for information on hospitals and Burj. They continued to read and connect different documents related to arms dealing and the disease outbreak.', 'In segment 8, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They read several documents related to arms dealing in different countries, including Pakistan, Dubai, and Yemen. They highlighted specific keywords related to transactions, meetings, and hospitals. The user found some suspicious information related to a meeting in Borj al Arab in April 2009 and searched for more information on it. They also searched for information on people involved in the meeting and found some connections between them. The user continued to read and connect different documents related to arms dealing and the disease outbreak, including an arms exhibition scheduled in Dubai in April 17th.', 'In segment 9, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They read several documents related to arms dealing in different countries, including Dubai, Iran, and Kenya. They searched for specific keywords related to meetings, people involved, and sickness. The user found some suspicious information related to a meeting in Dubai in April 2009 and a woman named Nahid who died in a hospital in May 2009. They connected several documents related to arms dealing and found a possible link between the disease outbreak and the meeting in Dubai. The user also searched for information on people involved in the meeting and found some connections between them.', 'In segment 10, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They opened and read several documents related to arms dealing in different countries, including Dubai, Iran, and Kenya. They searched for specific keywords related to meetings, people involved, and sickness. The user connected several documents related to arms dealing and found a possible link between the disease outbreak and the meeting in Dubai. They also searched for information on people involved in the meeting and found some connections between them. The user grouped documents by moving them aside and continued to connect different documents related to arms dealing and the disease outbreak. They searched for information on Tabriz and connected several documents related to it. The user continued to connect different documents related to arms dealing and the disease outbreak.', 'In segment 11, the user continued to investigate the possible connection between arms dealing and the disease outbreak. They opened and read several documents related to arms dealing in different countries, including Syria, Lebanon, Saudi Arabia, and Venezuela. They searched for specific keywords related to meetings, people involved, and the disease outbreak. The user connected several documents related to arms dealing and found a possible link between the disease outbreak and a meeting in Dubai. They also searched for information on people involved in the meeting and found some connections between them. The user searched for information on Columbia but could not find any connection to the meeting. They continued to connect different documents related to arms dealing and the disease outbreak.']
    references_2 = ['The user started investigating the origin of a disease that started in Nigeria in Feb 2011 and spread to other countries. They decided to focus on figuring out the disease first and then investigating arms dealing in these countries to see if there was a connection. They read documents related to arms dealing in Nigeria and highlighted the name "FUNSHO KAPOLALUM" in an email from an engineer. They also searched for gun dealers in Nigeria and Kenya and found a blog post about the recovery of 150 guns in Kenya. They started reading a new document about guns in Kenya.', 'In segment 2, the user searched for information on arms dealing in Nigeria and Kenya. They read several documents related to guns and arms dealing in these countries, highlighting the name "FUNSHO KAPOLALUM" in an email from an engineer. They also found an article from the New York Times about an international gun smuggler in Milan who had connections to Nigeria. The user tried to find a connection between the smuggler and the disease outbreak in Nigeria. They connected several documents related to arms dealing in Nigeria and Kenya.', "In segment 3, the user continued to search for a connection between the disease outbreak in Nigeria and arms dealing. They connected several documents related to arms dealing in Nigeria and Kenya, including armsdealing65 and armsdealing72. They searched for articles related to guns and Nigeria, but couldn't find any. They changed the topic to look for evidence of sickness and searched for articles related to the spread of the disease. They read several documents related to arms dealing, including armsdealing95, armsdealing79, and armsdealing84, and connected them. They found suspicious emails between Dr. George and Mikhail and created a note about it. They also found evidence of payment in one of the documents.", 'In segment 4, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Nigeria and Kenya, including armsdealing85, armsdealing97, armsdealing100, armsdealing72, armsdealing79, armsdealing81, armsdealing95, and armsdealing84. They highlighted specific dates in these documents and tried to connect them to the disease outbreak. They also found a phone call between Dr. George and a Russian man and decided to focus on reading emails and phone calls between Dr. George and Mikhail to make connections between dates. They searched for weapons and Nigeria and Russia, but found nothing important.', 'In segment 5, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Nigeria, Kenya, Russia, Saudi Arabia, North Korea, and Pakistan. They searched for specific keywords such as "sickness," "firearms," "illegal," "Iran," "Syria," "Lagos," "Nigeria," "Boyo," "Mikhail," and "Dombrovski." They connected documents related to arms dealing in Minsk and made a connection between two old documents. They also searched for the time when the disease first appeared and found a document related to an event in Pakistan.', 'In segment 6, the user searched for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Dubai, Nigeria, and Pakistan, highlighting the name "Dubai" in several documents. They searched for textbooks and found several documents related to the sale of textbooks in Moscow. They suspected that the textbooks were a cover for the sale of guns. They connected several documents related to textbooks and found connections between them. They also found a connection between the textbook documents and the arms dealing documents in Dubai and Pakistan.', 'In segment 7, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Dubai, Pakistan, Yemen, and Moscow. They highlighted the name "Bukhari" and searched for him in several documents. They found a transaction identification number related to Bukhari in document armsdealing12. They also found several documents related to a meeting in Dubai and searched for information about who attended and what happened. They found connections between the meeting and the disease outbreak. They searched for information about hospital and Burj and found several documents related to sick people attending the meeting.', 'In segment 8, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Dubai, Pakistan, Yemen, and Moscow, highlighting the name "Bukhari" and searching for him in several documents. They found a transaction identification number related to Bukhari in document armsdealing12. They also found several documents related to a meeting in Borj Al Arab, Dubai, in April 2009, where some attendees went to the hospital. They searched for information about the attendees and found connections between them and the disease outbreak. They also found documents related to an arms exhibition scheduled in Dubai on April 17th, which was attended by the same people who had the meeting in Borj Al Arab.', 'In segment 9, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They read several documents related to arms dealing in Dubai, Pakistan, Yemen, and Moscow, highlighting specific keywords and names such as "Dubai," "Bukhari," "Nahid," "George," "Funsho," and "Kapolalum." They found connections between the people who attended a meeting in Dubai in April 2009 and the disease outbreak in Nigeria in February 2009. They also found evidence of phone calls and transactions related to arms dealing and farming equipment. They created a note summarizing their findings.', 'In segment 10, the user opened several documents related to arms dealing in Dubai, Pakistan, Yemen, and Moscow, highlighting specific keywords and names such as "Dubai," "Bukhari," "Nahid," "George," "Funsho," and "Kapolalum." They connected several documents related to the meeting in Dubai in April 2009 and the disease outbreak in Nigeria in February 2009. They searched for information about other places that attended the meeting and found documents related to Tabriz. They connected several documents related to arms dealing and farming equipment. They also grouped important documents together and connected them.', 'In segment 11, the user continued to search for connections between the disease outbreak in Nigeria and arms dealing. They opened several documents related to arms dealing in different countries, including Dubai, Syria, Lebanon, Saudi Arabia, and Venezuela. They searched for specific keywords and names such as "Burj," "Ahmed," "Kasem," and "Columbia." They found connections between people who attended a meeting in Dubai and the disease outbreak in Nigeria. They also found evidence of arms dealing and connections between different countries. They connected several documents related to the meeting and the attendees. They couldn\'t find any evidence related to Columbia.']
    
    if len(results) != len(references_1):
        print("Number of results does not match the number of references")
        return
    
    for ix, (result, reference) in enumerate(zip(results, references_1)):
        highlighted_text = utils.highlight_differences(result, reference)
        if highlighted_text:
            print(f"segment {ix+1}:", highlighted_text)
    
# write a function to save snapshots to a file in JSON format
def save_snapshots(snapshot, folder_name, filename):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # write the snapshot to a file named "filemane.json" in the folder we just created
    with open(os.path.join(folder_name, filename + '.json'), 'w') as f:
        json.dump(snapshot, f)

def get_segment_summaries(context):
    # segment_summaries = []
    # for msg in context:
    #     if msg["role"] == "assistant":
    #         print(msg["content"])
    #         segment_summaries.append(msg["content"])
    # return " ".join(segment_summaries)
    return [msg["content"] for msg in context if msg["role"] == "assistant"]
    

def print_debugging_info(context, summaries):
    print(f"Last context list:\n {context}")
    print(f"Accumalted summaries:\n {summaries}")

def test_user(user):
    user.parse_manifest()
    user.parse_logs(include_docs=True)
    user.get_interaction_types()
    # print(user.interaction_logs)
    print(f"Divide the interaction logs into {len(user.interaction_logs)} segments")
    print(f"Interaction types: {user.interaction_types}")

if __name__ == "__main__":
    user = User('../data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json', '../original_web_interface/ApplicationManifest.json', 1, 1)
    # test_user(user)
    user.parse_manifest()
    # [2023-06-05_12-57-00] skipped one segment: user.parse_logs(skipped=True)
    user.parse_logs(include_docs=True)
    user.get_interaction_types()
    print(f"Divide the interaction logs into {user.num_segments} segments")

    folder_name = f"snapshots_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

    manual_sum = utils.load_json_to_dict("../dataset1_doc_manual.json")
    manual_sum_arms_p1 = manual_sum["manualSummaries"][0]["summary"]
    # print(manual_sum_arms_p1)

    if prompt_config["final"] == "false":
        # create a system message, an empty assistant message and the context list
        sys_msg = get_system_message(user, manual_sum_arms_p1)
        assistant_msg = None
        context = [sys_msg]
        segment_summaries = [] # a backup
        segment_summary = None
        
        ## prompt ChatGPT (will be a for loop)
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
                
        # print_debugging_info(context, segment_summaries)
        # test_prompting(segment_summaries)
        
    if prompt_config["final"] == "true":
        context = utils.load_json_to_dict("./baseline/snapshots_2023-06-03_23-05-35/snapshot_11_assistant.json")
        segment_summaries = get_segment_summaries(context)
    
    # user_msg_final = get_user_message_final(user, " ".join(segment_summaries), manual_sum_arms_p1)
    user_msg_final = get_user_message_final(user, " ".join(segment_summaries))

    if prompt_config["with_memory"] == "true":
        collect_messages(context=context, user_prompt=user_msg_final)
    elif prompt_config["with_memory"] == "false":
        context = [get_system_message(user, manual_sum_arms_p1)] + [user_msg_final]

    save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final")
    token_count = utils.num_tokens_from_messages(messages=context)
    print(f"Final summary: {token_count}")
    if token_count < 4096:
        overall_summary = utils.get_completion_from_messages(messages=context)
        assistant_msg = {"role": "assistant", "content": overall_summary}
        collect_messages(context=context, assistant_prompt=assistant_msg, user_prompt=None)
        save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final_assistant")
        scores = utils.run_evaluate([utils.load_json_to_dict("./baseline_focus_summaries/snapshot_final_assistant.json")[-1]["content"]], [overall_summary])
        context.append(scores)
        save_snapshots(context, folder_name=folder_name, filename=f"snapshot_final_assistant_with_scores")
    else:
        print("Accumulated too many tokens!")
        print_debugging_info(context, segment_summaries)
    print(overall_summary)

    # scores = utils.run_evaluate([utils.load_json_to_dict("./baseline_with_focus/snapshot_final_assistant.json")[-1]["content"]], [utils.load_json_to_dict("./core_features_manual_example_p1/snapshot_final_assistant.json")[-1]["content"]])
    # context = utils.load_json_to_dict("./core_features_manual_example_p1/snapshot_final_assistant.json")
    # context.append(scores)
    # save_snapshots(context, folder_name="core_features_manual_example_p1", filename=f"snapshot_final_assistant_with_scores")