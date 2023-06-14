from document import Document
import json
import toml

DOC_PATH = "../data/Dataset_1/Documents/Documents_Dataset_1.json"
config = toml.load("config.toml")
doc_config = config["document"]

def process_docs(doc_path=None):
    with open(doc_path, 'r') as f:
        docs = json.load(f)
    new_docs = []
    n = len(docs)

    # for doc in docs:
    for i in range(90, 102):
        doc = docs[i]
        d = Document(doc)
        d.summarize()
        d.get_topics()
        d.get_entities()
        new_docs.append(d.__dict__)
        
    new_path = get_new_file_path(doc_path, '_preprocessed_part8')
    with open(new_path, 'w') as f:
        json.dump(new_docs, f)

# write a function that takes a list of documents and combine the json objects into one big json file
# then write that file to a new file path
def combine_docs(doc_path, doc_list):
    final_docs = []
    for path in doc_list:
        with open(path, 'r') as f:
            docs = json.load(f)
        final_docs += docs
    new_path = get_new_file_path(doc_path, '_preprocessed')
    with open(new_path, 'w') as f:
        json.dump(final_docs, f)

# write a function that takes a doc_path and appends to_append to the end of the file path
def get_new_file_path(doc_path, to_append):
    new_filename = doc_path.split('/')[-1].split('.')[0] + to_append + '.json'
    new_path = '/'.join(doc_path.split('/')[:-1]) + '/' + new_filename
    # print(new_path)
    return new_path
    
if __name__ == "__main__":
    doc_list = [get_new_file_path(DOC_PATH, "_preprocessed_part" + str(i)) for i in range(1, doc_config["num_parts"] + 1)]
    # process_docs(DOC_PATH)
    combine_docs(DOC_PATH, doc_list)