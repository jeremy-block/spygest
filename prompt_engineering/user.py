import json
import toml
import random
import utils

config = toml.load("./config.toml")
user_config = config["user"]

class User:
    """
    Parameters
    - log_path: the path to a user interaction log file
    - manifest_path: the path to the manifest file that contains superlatives
    - dataset_id: the id of the dataset (1-based)
    - user_id: the id of the user (1-based)
    """
    def __init__(self, log_path, manifest_path, dataset_id, user_id):
        self.log_path = log_path
        self.manifest_path = manifest_path
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.superlatives = None
        self.raw_logs = None
        self.interaction_logs = []
        self.docs = utils.load_json_to_dict(user_config["docs_path"])

    def parse_manifest(self):
        with open(self.manifest_path, 'r') as f:
            manifest = json.load(f)
        self.superlatives = manifest['superlatives'][self.dataset_id-1][self.user_id-1]
        self.num_segments = user_config['num_segments']

    def parse_logs(self, skipped=False, include_docs=False, doc_only=False):
        with open(self.log_path, 'r') as f:
            logs = json.load(f)
        self.raw_logs = logs
        self.num_logs = len(logs)
        if skipped:
            self.get_segments_skip()
        elif include_docs:
            self.get_segments_with_doc(has_sum=True, has_topics=True, has_entities=True)
        elif doc_only:
            self.get_segments_doc_only(has_sum=True, has_topics=True, has_entities=True)
        else:
            self.get_segments()
    
    def get_segments(self):
        """
        - Return interaction sentences (without document information) for a segment
        - Implementation:
            - divide raw_logs into self.num_segments segments
            - each segment takes a list of logs
            - get the "summary" from these logs (JSON objects)
            - add "The user" to the beginning of the "summary"
            - concatenate the summaries into a single string, append it to "self.interaction_logs"
        """
        segment_length = self.num_logs // self.num_segments
        for i in range(self.num_segments):
            segment_logs = ["The user"]
            for j in range(i*segment_length, min((i+1)*segment_length, self.num_logs)):
                print(f"adding log {j} to segment {i}")
                segment_logs.append(self.raw_logs[j]["summary"] + ",")
            self.interaction_logs.append(" ".join(segment_logs))

    def get_segments_with_doc(self, has_sum=False, has_topics=False, has_entities=False):
        """
        Advanced version of get_segments()
        Add information extracted from documents to interaction sentences
        """
        segment_length = self.num_logs // self.num_segments
        for i in range(self.num_segments):
            segment_logs = ["The user"]
            start = i*segment_length
            end = (i+1)*segment_length
            if i == self.num_segments-1:
                end = self.num_logs
            segment_reading_set = set()
            for j in range(start, end):
                interaction_log = self.raw_logs[j]["summary"]
                if self.raw_logs[j]["interactionType"] == "Reading" and self.raw_logs[j]["duration"] > 150:
                    # Only include the information from documents the user engaged with
                    doc_id = self.get_doc_id(j)
                    if has_sum:
                        interaction_log += ", with the content: " + self.docs[doc_id]["summary"]
                    if has_topics:
                        interaction_log += " Important topics: " + self.docs[doc_id]["topics"]
                    if has_entities and doc_id not in segment_reading_set:
                        entities = []
                        entity = ""
                        for et, en in self.docs[doc_id]["entities"].items():
                            entity = f"{et}: {','.join(en)}"
                            entities.append(entity)
                        interaction_log += " Important named entities: " + ("; ".join(entities))
                    segment_reading_set.add(doc_id)
                elif self.raw_logs[j]["interactionType"] == "Think_aloud":
                    # Skip the think aloud interaction
                    continue
                else:
                    interaction_log += ","
                segment_logs.append(interaction_log)
            self.interaction_logs.append(" ".join(segment_logs))

    def get_segments_doc_only(self, has_sum=False, has_topics=False, has_entities=False):
        """
        Only return sentences for reading interactions for factuality check using FactGraph
        """
        segment_length = self.num_logs // self.num_segments
        print(self.num_logs)
        print(segment_length)
        for i in range(self.num_segments):
            segment_logs = ["The user"]
            start = i*segment_length
            end = (i+1)*segment_length
            if i == self.num_segments-1:
                end = self.num_logs
            segment_reading_set = set()
            for j in range(start, end):
                interaction_log = self.raw_logs[j]["summary"]
                if self.raw_logs[j]["interactionType"] == "Reading" and self.raw_logs[j]["duration"] > 150:
                    doc_id = self.get_doc_id(j)
                    if has_sum:
                        interaction_log += ", with the content: " + self.docs[doc_id]["summary"]
                    if has_topics:
                        interaction_log += " Important topics: " + self.docs[doc_id]["topics"]
                    if has_entities and doc_id not in segment_reading_set:
                        entities = []
                        entity = ""
                        for et, en in self.docs[doc_id]["entities"].items():
                            entity = f"{et}: {','.join(en)}"
                            entities.append(entity)
                        interaction_log += " Important named entities: " + ("; ".join(entities))
                    segment_reading_set.add(doc_id)
                    segment_logs.append(interaction_log)
            self.interaction_logs.append(" ".join(segment_logs))
    
    def get_doc_id(self, log_ix):
        return int(self.raw_logs[log_ix]["id"][len(user_config["theme_id"]):])-1

    def get_segments_skip(self):
        """
        For experimental purposes, randomly skips a certain number of segments
        """
        segment_length = self.num_logs // self.num_segments
        skip_segment = random.randint(0, self.num_segments-1)

        for i in range(self.num_segments):
            segment_logs = ["The user"]
            if i == skip_segment:
                continue
            for j in range(i*segment_length, min((i+1)*segment_length, self.num_logs)):
                segment_logs.append(self.raw_logs[j]["summary"]+",")
            self.interaction_logs.append(" ".join(segment_logs))
        print("segment skipped: {skip_segment}")
        print(len(self.interaction_logs))
        self.num_segments -= user_config["num_skipped_seg"]
    
    def get_interaction_types(self):
        if not self.raw_logs:
            self.parse_logs()
        interaction_types = set()
        for log in self.raw_logs:
            if log["interactionType"] not in interaction_types:
                interaction_types.add(log["interactionType"])
        self.interaction_types = interaction_types
        return self.interaction_types
