from document import Document
import json
import toml

DOC_PATH = "../data/Dataset_1/Documents/Documents_Dataset_1.json"
config = toml.load("config.toml")
doc_config = config["document"]

def process_docs(doc_path=None):
    """
    Takes in the path to the documents in Dataset 1
    Call functions implemented in the document module to extract summaries, topics, and entities
    Save the results to a new file that has the same name as the original file but has "_preprocessed_part#" appended to the end
    """
    with open(doc_path, 'r') as f:
        docs = json.load(f)
    new_docs = []

    # We have to manually set the number of documents to be processed because there is a limit on the number of requests we can send to the API in a certain amount of time
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

def combine_docs(doc_path, doc_list):
    """
    Combines different parts of the preprocessed documents into one file that has the same name as the original file but has "_preprocessed" appended to the end
    """
    final_docs = []
    for path in doc_list:
        with open(path, 'r') as f:
            docs = json.load(f)
        final_docs += docs
    new_path = get_new_file_path(doc_path, '_preprocessed')
    with open(new_path, 'w') as f:
        json.dump(final_docs, f)

def get_new_file_path(doc_path, to_append):
    new_filename = doc_path.split('/')[-1].split('.')[0] + to_append + '.json'
    new_path = '/'.join(doc_path.split('/')[:-1]) + '/' + new_filename
    return new_path
    
if __name__ == "__main__":
    doc_list = [get_new_file_path(DOC_PATH, "_preprocessed_part" + str(i)) for i in range(1, doc_config["num_parts"] + 1)]
    combine_docs(DOC_PATH, doc_list)