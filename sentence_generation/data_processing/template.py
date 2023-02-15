class Template:
    def __init__(self):
        self.start = "The user worked on solving a mystery based on relevant documents"
        self.topics = "They searched for"
        self.highlighted = "They highlighted"
        self.keywords = "Their search include keywords such as"
        pass

    def get_template_based_sentences(self, data):
        topics = " ".join([self.topics, ", ".join(data.topics)])
        highlighted = " ".join([self.highlighted, ", ".join(data.highlighted)])
        keywords = " ".join([self.keywords, ", ".join(data.keywords)])
        documents = f"They explored {data.num_docs} documents."
        return ". ".join([self.start, topics, highlighted, keywords, documents])