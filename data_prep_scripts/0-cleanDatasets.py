# Ran on 1/31/2023 to clean up dataset documents

# 
# This script adjusts a document that does not have a date field and an id with capital letters and reduces that.
# Takes documents like: 
#     {
#         "id": "ArmsDealing 1",
#         "date": "unknown",
#         "title": "Feb 2008, drilling equipment scheduled to arrive, Kiev to Iran",
#         "contents": "US GOVERNMENT TELEPHONE INTERCEPT: 5 FEBRUARY 2008<br><br>Call placed from Kiev, Ukraine to Tabriz, Iran.  <br><br> The call from Kiev was from a prepaid cell phone using an unlisted ID datasetNumberber supplied by an Internet café.  The receiver of the call was at the address: 24 Janbazan St, West Ajerbaijan, Tabriz, Iran.  This address is the residence of Sattari Khurshid. The caller says, “The drilling equipment is scheduled to arrive at Urmia on the 12th.”  The receiver says, “All is well then.  Soltan will handle all the arrangements.”  "
#     }
# produces documents like:
#     {
#         "id": "armsdealing1",
#         "date": "Feb 2008",
#         "title": "drilling equipment scheduled to arrive, Kiev to Iran",
#         "contents": "US GOVERNMENT TELEPHONE INTERCEPT: 5 FEBRUARY 2008<br><br>Call placed from Kiev, Ukraine to Tabriz, Iran.  <br><br> The call from Kiev was from a prepaid cell phone using an unlisted ID datasetNumberber supplied by an Internet café.  The receiver of the call was at the address: 24 Janbazan St, West Ajerbaijan, Tabriz, Iran.  This address is the residence of Sattari Khurshid. The caller says, “The drilling equipment is scheduled to arrive at Urmia on the 12th.”  The receiver says, “All is well then.  Soltan will handle all the arrangements.”  "
#     }

import json
import re
datasetNumber = 1
path = "data/Dataset_"+str(datasetNumber)+"/Documents/Documents_Dataset_"+str(datasetNumber)+".json"

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

def peel_off_date(docTitle):
    titleParts = docTitle.split(",")
    return titleParts[0],titleParts[1:]

# def findNumberInString(str):
#     x = re.findall('[0-9]+', str)
#     return x[0]

data = load_json_data_from_file(path)

outdata=[]

for item in data:
    splitDate = peel_off_date(item["title"])
    # if datasetNumber == 1:
    #     item["id"] = "Armsdealing "+str(findNumberInString(item["id"]))
    #     print(item)
    newItem = {
        "id": item["id"].lower(),
        "date":splitDate[0],
        "title": ",".join(splitDate[1])[1:],
        "contents": item["contents"]
    }
    print(newItem)
    outdata.append(newItem)

write_json_data_to_file(path,outdata)
