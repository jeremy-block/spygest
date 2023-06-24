from user import User
import json
import os
import utils
import collections

_FOLDER_PATH = "p2/manager_none"

def generate_samples(file_path, interaction_logs):
    with open(os.path.join(file_path, "snapshot_final_assistant_with_scores.json"), "r") as f:
        final_snapshot = json.load(f)
    summary = final_snapshot[-13]["content"]
    res = {"summary": summary, "article": interaction_logs}
    return res

def generate_segment_evals(file_path, interaction_logs):
    res = []
    with open(os.path.join(file_path, "snapshot_10_assistant.json"), "r") as f:
        snapshots = json.load(f)
        n = len(snapshots)
        for i in range(2, n, 2):
            # print(interaction_logs[i // 2 -1])
            # print(snapshots[i]["content"])
            sample = {"summary": snapshots[i]["content"], "article": interaction_logs[i // 2 -1]}
            res.append(sample)
    # create a new file and write each element in res as a line in this new file
    with open(os.path.join(file_path, "segment_evals.json"), "w") as f:
        for sample in res:
            print(sample)
            f.write(json.dumps(sample) + "\n")
        

if __name__ == "__main__":
    user = User('../data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json', '../original_web_interface/ApplicationManifest.json', dataset_id=1, user_id=1) # change participant
    user.parse_manifest()
    # user.parse_logs(doc_only=True)
    user.parse_logs(include_docs=True)
    # print(user.interaction_logs)
    print(utils.num_tokens_from_messages([{"role": "user", "content": ",".join(user.interaction_logs)}]))
    # sample = generate_samples(_FOLDER_PATH, " ".join(user.interaction_logs))
    # print(sample)
    # utils.save_dict_to_json(sample, _FOLDER_PATH, "sample")
    # generate_segment_evals(_FOLDER_PATH, user.interaction_logs)