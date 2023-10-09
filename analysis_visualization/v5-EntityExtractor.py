####
# Function that calls on SpaCy to help extract entities and provide them to v5-entitiesbylength.R
# Did not find significant results.

import pandas as pd
import csv
import spacy
  
# todo Maybe try running with a more complext model? there is: ('en_core_web_trf')
nlp = spacy.load('en_core_web_sm')  

csv_file = "metric_visualization/data/data.csv"
out_file = "metric_visualization/data/entityCounts.csv"


# todo Extract only the types of entities we provided to gpt. https://spacy.io/universe/project/spacy-conll
def extract_entities(text):
    doc = nlp(text)
    entities = []

    for ent in doc.ents:
        entities.append({"text": ent.text, "start": ent.start_char, "end" : ent.end_char, "label": ent.label_})

    return entities


def group_by_label(data):
    grouped_data = {}
    for item in data:
        label = item.get('label')
        # print(item)
        if label in grouped_data:
            grouped_data[label].append(item.get('text'))
        else:
            grouped_data[label] = [item.get('text')]
    return grouped_data

# file_path = 'data.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)
print(df)

outputHeader = ["audience", "example", "person",
                  'type', 'count', 'OverSummaryLength']

with open(out_file, 'w', newline='') as file2:
        writer = csv.writer(file2)
        # writer.writerow()  # 'entity list'])
        
# Convert each row of the DataFrame to a dictionary, process it, and collect the results
processed_dicts = []
for _, row in df.iterrows():
    row_dict = row.to_dict()
    # print(row_dict["final_summary"])
    processed_dict = group_by_label(extract_entities(row_dict["final_summary"]))
    #todo We need some way of correcting for duplicate entities
    total_entities = 0
    for entity_type, entities in processed_dict.items():
        count = len(entities)
        total_entities = total_entities + count
        processed_dicts.append({"audience":row_dict["audience"], "example": row_dict["example"], "person": row_dict["person"], "entity_type": entity_type, "count":count, "over_summary_length":(count/len(row_dict["final_summary"]))})  # , ', '.join(entities)])
    # , ', '.join(entities)])
    processed_dicts.append({"audience": row_dict["audience"], "example": row_dict["example"], "person": row_dict["person"], "entity_type": "TOTAL", "count": total_entities, "over_summary_length": (total_entities/len(row_dict["final_summary"]))})

# Convert the processed dictionaries back to a DataFrame
processed_df = pd.DataFrame.from_records(processed_dicts)

# Save the processed DataFrame to a CSV file
processed_df.to_csv(out_file, index=False)


