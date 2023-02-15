class ExtractedData:
    def __init__(self, segment=-1, topics=None, highlighted=None, keywords=None, noted=None, num_docs=0, doc_summaries=None, manifest=None):
        self.segment = segment
        self.topics = topics
        self.highlighted = highlighted
        self.keywords = keywords
        self.noted = noted
        self.num_docs = num_docs
        self.doc_summaries = {} # {doc#: (name, number of times this doc is opened)}
        self.manifest = manifest

    def get_dummy(self):
        self.segment = 2
        self.topics = ["nigeria", "gun", "kenya"]
        self.highlighted = ["Kenya"]
        self.keywords = ["nigeria", "gun", "kenya", "february"]
        self.num_docs = 4
