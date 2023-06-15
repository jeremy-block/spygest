# write a class User that stores statisitics of the interaction log of a session
# the class is initialized by 
# - a path to the interaction log file
# - a path to the interaction manifest: "./original_web_interface/ApplicationManifest.json"
# the class should have the following fields parsed from the manifest:
# - dataset_id
# - user_id
# - print out one of the superlatives for now

import json
import toml
import random
import utils

config = toml.load("./config.toml")
user_config = config["user"]

class User:
    def __init__(self, log_path, manifest_path, dataset_id, user_id):
        self.log_path = log_path
        self.manifest_path = manifest_path
        self.dataset_id = dataset_id
        self.user_id = user_id # number, for example, 1 for P1
        self.superlatives = None
        self.raw_logs = None
        self.interaction_logs = []
        self.docs = utils.load_json_to_dict(user_config["docs_path"])
        # self.parse_manifest()
        # self.parse_logs()
        # define important documents, see if there's a "no relevant information" message for these docs

    def parse_manifest(self):
        with open(self.manifest_path, 'r') as f:
            manifest = json.load(f)
        # print(f"Number of datasets: {manifest['superlatives']}")
        # print(f"Number of users: {len(manifest['superlatives'][0])}")
        self.superlatives = manifest['superlatives'][self.dataset_id-1][self.user_id-1]
        # print(f"Number of superlatives: {len(self.superlatives)}")
        # print(f"Superlatives: {self.superlatives.keys()}")
        
        # self.num_segments = self.superlatives['segCount']
        self.num_segments = user_config['num_segments'] # or just set to 10?
        
        # print(f"Segment counts: {self.num_segments}")

    def parse_logs(self, skipped=False, include_docs=False):
        with open(self.log_path, 'r') as f:
            logs = json.load(f)
        self.raw_logs = logs
        self.num_logs = len(logs)
        # print(f"Number of logs: {self.num_logs}")
        if skipped:
            self.get_segments_skip()
        elif include_docs:
            self.get_segments_with_doc(has_sum=True, has_topics=True, has_entities=True)
        else:
            self.get_segments()
            
        # print(len(self.interaction_logs))

    def get_segments_with_doc(self, has_sum=False, has_topics=False, has_entities=False):
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
                # print(f"adding log {j} to segment {i+1}")
                # segment_logs.append(" ".join(["The user", self.raw_logs[j]["summary"]+"."]))
                interaction_log = self.raw_logs[j]["summary"]
                # if self.raw_logs[j]["interactionType"] == "Reading" and self.raw_logs[j]["duration"] > 50:
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
                        # print(entities)
                        interaction_log += " Important named entities: " + ("; ".join(entities))
                    segment_reading_set.add(doc_id)
                    # print(interaction_log)
                # elif self.raw_logs[j]["interactionType"] == "Connection":
                #     id1, id2 = self.raw_logs[j]["id"].split(",")
                #     if user_config["theme_id"] not in id1 or user_config["theme_id"] not in id2:
                #         interaction_log += ","
                #     else:
                #         doc_id1 = int(id1[len(user_config['theme_id']):])-1
                #         doc_id2 = int(id2[len(user_config['theme_id']):])-1 
                #         interaction_log += f", with the titles: {self.docs[doc_id1]['title']} and {self.docs[doc_id2]['title']},"
                #     # print(interaction_log)
                # elif self.raw_logs[j]["interactionType"] in user_config["title_interaction"]:
                #     doc_id = self.get_doc_id(j)
                #     interaction_log += f', with the title: {self.docs[doc_id]["title"]},'
                #     # print(interaction_log)
                elif self.raw_logs[j]["interactionType"] == "Think_aloud":
                    continue
                else:
                    interaction_log += ","
                # segment_logs.append(self.raw_logs[j]["summary"]+",")
                segment_logs.append(interaction_log)
                # print(interaction_log)
            self.interaction_logs.append(" ".join(segment_logs))
    
    def get_doc_id(self, log_ix):
        return int(self.raw_logs[log_ix]["id"][len(user_config["theme_id"]):])-1
    
    def get_segments(self):
        # divide raw_logs into self.num_segments segments
        # each segment takes a list of logs
        # get the "summary" from these logs (JSON objects)
        # add "The user" to the beginning of the "summary"
        # concatenate the summaries into a single string, append it to "self.interaction_logs"
        segment_length = self.num_logs // self.num_segments
        for i in range(self.num_segments):
            segment_logs = ["The user"]
            for j in range(i*segment_length, min((i+1)*segment_length, self.num_logs)):
                print(f"adding log {j} to segment {i}")
                # segment_logs.append(" ".join(["The user", self.raw_logs[j]["summary"]+"."]))
                segment_logs.append(self.raw_logs[j]["summary"]+",")
            self.interaction_logs.append(" ".join(segment_logs))

    def get_segments_skip(self):
        segment_length = self.num_logs // self.num_segments
        
        # get a random integer between 0 and self.num_segments-1 (inclusive)
        skip_segment = random.randint(0, self.num_segments-1)

        for i in range(self.num_segments):
            segment_logs = ["The user"]
            if i == skip_segment:
                continue
            for j in range(i*segment_length, min((i+1)*segment_length, self.num_logs)):
                # print(f"adding log {j} to segment {i}")
                # segment_logs.append(" ".join(["The user", self.raw_logs[j]["summary"]+"."]))
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

    def check_token_limitation(self):
        pass

    def add_details(self, doc):
        pass

    def get_limited_interactions(self):
        pass