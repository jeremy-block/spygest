from user import User
import json
import os
import utils
import collections

def generate_samples(file_path, interaction_logs):
    """
    generate samples for the entire interaction session in the format of {"summary": summary, "article": article} for checking factuality using FactGraph.
    """
    with open(os.path.join(file_path, "snapshot_final_assistant_with_scores.json"), "r") as f:
        final_snapshot = json.load(f)
    summary = final_snapshot[-13]["content"]
    res = {"summary": summary, "article": interaction_logs}
    return res

def generate_segment_evals(file_path, interaction_logs):
    """
    generate samples for each segment in the format of {"summary": summary, "article": article} for checking factuality using FactGraph    
    """
    res = []
    with open(os.path.join(file_path, "snapshot_10_assistant.json"), "r") as f:
        snapshots = json.load(f)
        n = len(snapshots)
        for i in range(2, n, 2):
            sample = {"summary": snapshots[i]["content"], "article": interaction_logs[i // 2 -1]}
            res.append(sample)
    with open(os.path.join(file_path, "segment_evals.json"), "w") as f:
        for sample in res:
            print(sample)
            f.write(json.dumps(sample) + "\n")
