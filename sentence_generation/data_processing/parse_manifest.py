import json

class Parser:
    def __init__(self, path):
        with open(path, "r") as read_file:
            self.data = json.load(read_file) 
        
    def get＿manifest_superlatives_user(self, dataset_id, uid):
        return self.data["superlatives"][dataset_id][uid]
    
    def get_logs_from_idx(self, log_idx):
        return self.data[log_idx]
    
    def get_entities_from_idx(self, doc_idx):
        return self.data[doc_idx]
