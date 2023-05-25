# write a class User that stores statisitics of the interaction log of a session
# the class is initialized by 
# - a path to the interaction log file
# - a path to the interaction manifest: "./original_web_interface/ApplicationManifest.json"
# the class should have the following fields parsed from the manifest:
# - dataset_id
# - user_id
# - print out one of the superlatives for now

import json
class User:
    def __init__(self, log_path, manifest_path):
        self.log_path = log_path
        self.manifest_path = manifest_path
        self.dataset_id = None
        self.user_id = None
        self.superlatives = None

    def parse_manifest(self):
        with open(self.manifest_path, 'r') as f:
            manifest = json.load(f)
        self.superlatives = manifest['superlatives']
        # self.dataset_id = manifest['dataset_id']
        # self.user_id = manifest['user_id']

    def parse_log(self):
        with open(self.log_path, 'r') as f:
            log = json.load(f)
        self.superlatives = log['superlative']

    def print_superlatives(self):
        # print(self.superlatives)
        # print the keys, length
        print(len(self.superlatives))
        # print(self.superlatives.keys())

# write a test for the User class
# test that the superlative is parsed correctly
# test that the superlative is printed correctly
# test that the superlative is not printed if the log file is not found
def test_user():
    user = User('./data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json', './original_web_interface/ApplicationManifest.json')
    user.parse_manifest()
    # user.parse_log()
    user.print_superlatives()

# if __name__ == '__main__':
#     test_user()