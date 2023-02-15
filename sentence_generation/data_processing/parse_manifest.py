import json

def parse(manifest_path):
    with open(manifest_path, "r") as read_file:
        data = json.load(read_file) 
    # print(type(data))
    # print(len(data.keys()))
    # print(data.keys())
    for k,v in data.items():
        print(k)
    print(len(data["segments"]))
    print(len(data["interactionLogs"]))
    print(len(data["superlatives"]))

    print(data["interactionLogs"])
        # for kk, vv in v.items():
        #     print(kk)
    # print(data)
