import json
import toml
import utils

config = toml.load("config.toml")
doc_config = config["document"]
armsdealing78_entities = '{"person": ["crew","officers"],"organization": ["Bangkok Post","Thai authorities","police","customs","immigration","air force","Ebina House"],"location": ["Bangkok","North Korea","Don Mueang airport"],"miscellaneous": ["Russian cargo plane"]}'

class Document:
    """
    Parameters
    - doc: a dictionary parsed from the JSON file that contains a list of documents, each having the following keys:
        - id
        - date
        - title
        - contents
    """
    def __init__(self, doc):
        self.id = doc["id"]
        self.date = doc["date"]
        self.title = doc["title"]
        self.contents = doc["contents"]

    def summarize(self):
        story = f"""Title: {self.title}\nContents: {self.contents}"""
        summ_config = doc_config["summary"]
        prompt = f"""Act as {summ_config["role"]}, your task is to generate a short summary of classified documents. Summarize the document delimited by triple backticks in at most {summ_config["long_length"]}. Document:\n ```{story}```"""
        self.summary = utils.get_completion(prompt)
        print(self.summary)

    def get_topics(self):
        story = f"""Title: {self.title}\nContents: {self.contents}"""
        topics_config = doc_config["topics"]
        prompt = f"""Act as {topics_config["role"]}, your task is to determine topics that are being discussed in classified documents. Determine up to {topics_config["num_topics"]} topics in the document delimited by triple backticks. Make each item one to {topics_config["len_topic"]} words long. Format your response as "a list of items separated by commas". Document:\n ```{story}```"""
        self.topics = utils.get_completion(prompt)
        print(self.topics)

    def get_entities(self):
        story = f"""Title: {self.title}\nContents: {self.contents}"""
        ent_config = doc_config["entities"]
        prompt = f"""Act as {ent_config["role"]}, your task is to identify named entities in classified documents. There are {ent_config["num_entities"]} entities, which are {ent_config["entities"]}. Identify the entities in the document delimited by triple backticks. Format your response in a JSON format. Document:\n ```{story}```"""
        json_res = utils.get_completion(prompt)
        if self.id == "armsdealing78":
            # We have to address this edge case where the API always makes the same mistake on the JSON format
            self.entities = json.loads(armsdealing78_entities)
        else:
            self.entities = json.loads(json_res)
        print(self.entities)
