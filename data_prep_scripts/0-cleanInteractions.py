# Ran on 1/31/2023 to clean up dataset interactions for all 8 participants in each dataset

# Takes an event like the following
# {
#   "duration": 32,
#   "Text": "Armsdealing 100",
#   "InteractionType": "Reading",
#   "ID": "Armsdealing 100",
#   "time": 6166
#  }, 
### and converts it to
#     {
#     "duration": 32,
#     "text": "",
#     "interactionType": "Reading",
#     "id": "armsdealing100",
#     "time": 6166
# },

import json
import re
# datasetNumber = [1, "Arms"]
# datasetNumber = [2, "Terrorist"]
datasetNumber = [3, "Disappearance"]

#Which types of events need to have their content changed? 
# "ID", "Text" - implies that there is duplicate information in both fields. "id" will be lowered and spaces removed, "text" will be made blank
# "ID" - implies that the "id" nees to be lowered and spaces removed.
# 0 - implies no changes other than the capitalization of property names.
conversionMap={
    "Mouse_hover": ["ID", "Text"],
    "Draging": ["ID", "Text"],
    "Doc_open": ["ID", "Text"],
    "Reading": ["ID", "Text"],
    "Connection": ["ID", "Text"],
    "Highlight": ["ID"],
    "Topic_change": [0],
    "Think_aloud": [0],
    "Search": [0],
    "Create Note": [0],
    "Add note": [0]
}

def load_json_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    file.close()
    return data


def write_json_data_to_file(file_path, data):
    with open(file_path, 'w') as file:
            d = json.dumps(data, indent=4, ensure_ascii=False)
            file.write(d)
    file.close()
    print("file written to ",file_path)

def lowerAndRemoveSpace(string):
    return string.lower().replace(" ", "")

def lowerEventByType(event,mapping=conversionMap):
     eventType = event["InteractionType"]
     try:
        if mapping[eventType] == [0]:
             newEvent = {
                "duration" : event["duration"],
                "text" : event["Text"],
                "interactionType" : event["InteractionType"],
                "id" : event["ID"],
                "time" : event["time"]              
            }
        elif mapping[eventType] == ["ID"]:
            newEvent = {
                "duration" : event["duration"],
                "text" : event["Text"],
                "interactionType" : event["InteractionType"],
                "id" : lowerAndRemoveSpace(event["ID"]),
                "time" : event["time"]              
            }
        elif mapping[eventType] == ["ID", "Text"]:
            newEvent = {
                "duration" : event["duration"],
                "text": "",
                "interactionType": event["InteractionType"],
                "id": lowerAndRemoveSpace(event["ID"]),
                "time": event["time"]
            }
     except KeyError:
        print("-!- KEY ERROR -!-\n", event,"\n\nContains an un-Mapped Event. Check script and redefine. Original File has not been changed yet.\n\n")
        exit()
     return newEvent

def convertFile(filePath):
    data = load_json_data_from_file(filePath)
    outdata=[]

    for item in data:
        newItem = lowerEventByType(item)
        outdata.append(newItem)

    write_json_data_to_file(filePath,outdata)


for userNumber in range(1, 9):
    path = "data/Dataset_"+str(datasetNumber[0])+"/User Interactions/"+str(
        datasetNumber[1])+"_P"+str(userNumber)+"_InteractionsLogs.json"
    convertFile(path)
