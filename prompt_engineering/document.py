import json
import toml

class Document:
    def __init__(self, doc):
        self.id = doc["id"]
        self.title = doc["title"]
        self.contents = doc["contents"]
        self.story = None

    def get_story(self):
        self.story = f"""Title: {self.title}\nContents: {self.contents}
        """
        print(self.story)

    def summarize(self):
        prompt = f"""Act as a intelligence analyst, your task is to generate a short summary of classified documents. Summarize the document delimited by triple backticks in at most 3 sentences. Review: ```{self.story}```"""
        print(prompt)
        

    def topics(self):
        number_of_topics = 5
        length_of_topic = 2
        prompt = f"""
        Determine {number_of_topics} topics that are being discussed in the following text, which is delimited by triple backticks.
        
        Make each item one to {length_of_topic} words long. 

        Format your response as a list of items separated by commas.

        Text sample: '''{self.story}'''
        """
        pass

    def entities(self):
        pass

    def save_to_new_doc(self, path):
        pass

if __name__ == "__main__":
    doc_path = "../data/Dataset_1/Documents/Documents_Dataset_1.json"
    with open(doc_path, 'r') as f:
        docs = json.load(f)
    for doc in docs[:1]:
        d = Document(doc)
        d.get_story()
        d.summarize()