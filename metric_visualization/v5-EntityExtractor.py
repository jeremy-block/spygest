import pandas as pd
import csv
import spacy
  
nlp = spacy.load('en_core_web_sm')#trf')

csv_file = "metric_visualization/data/data.csv"
out_file = "metric_visualization/data/entityCounts.csv"


  
# sentence = "The user investigated an event in the intelligence domain by analyzing multiple documents related to arms dealing, fraudulent schemes, and intercepted emails. They searched for information related to Nigeria, Kenya, Syria, Pakistan, Saudi Arabia, Venezuela, Yemen, Dubai, Gaza, Russia, Thailand, and Columbia. The user found evidence of proposed and realized arms deals and the involvement of Leonid Minsky, an international gun smuggler, in these deals. They also found intercepted emails discussing a coded account at the Central Bank of Nigeria containing $30,600,000.00 and a potential fraudulent scheme involving bank transfers, contract details, and approval processes. The user analyzed a surveillance report on Akram Basra, suspected to be associated with a top leader in the Karachi faction of Lashkar-e-Jhangvi. They also read about the deaths of Thabiti Otieno and Nahid Owiti, a married couple from Narok, who passed away on May 1, 2009, at Nairobi Hospital. The user found an intercepted US government telephone conversation discussing the safe arrival of Tanya's jewels, Nicolai, Nahid, Nairobi, and Dubai. They also read about North Korea's sales of missiles, missile parts, and other arms to countries like Iran, Syria, and Myanmar, which violate a U.N. resolution designed to punish North Korea for consistently violating UN-imposed sanctions over the past year. The user added notes about Kasem and Khouri in Gaza and Minsky and Nikolai in Russia. They also found an intercepted email from Mikhail Dombrovski to Dr. George discussing a transaction to take place at an upcoming meeting on April 15. The user searched for information related to sickness and infection and added notes about Jhon and Hombre exchanging birthday presents. Overall, the user's investigation revealed a complex network of arms dealing, fraudulent schemes, and illegal activities involving multiple countries and individuals."


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


