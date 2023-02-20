from data_processing.parse_manifest import Parser
from data_processing.template import Template
from data_type.extracted_data import ExtractedData
from data_type.interaction_data import InteractionData
from data_type.entity_data import EntityData

import torch
# from transformers import PegasusForConditionalGeneration, PegasusTokenizer

def printer(name, arr):
    print(f"==={name}===")
    for item in arr:
        print(item)
    print(" ")

def get_response(input_text,num_return_sequences,num_beams):
    batch = tokenizer([input_text],truncation=True,padding='longest',max_length=240, return_tensors="pt").to(torch_device)
    translated = model.generate(**batch,max_length=240,num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    return tgt_text

if __name__ == "__main__":
    manifest_parser = Parser("../original_web_interface/ApplicationManifest.json")
    arms_P1_parser = Parser("../data/Dataset_1/User Interactions/Arms_P1_InteractionsLogs.json")
    arms_entity_parser = Parser("../data/Dataset_1/Documents/Entities_Dataset_1.json")

    manifest_data = ExtractedData(manifest_parser.get_manifest_superlatives_user(0,0))
    arms_P1_data = InteractionData(arms_P1_parser.get_logs_from_idx(0))
    arms_entity_data = EntityData(arms_entity_parser.get_entities_from_idx(0))

    printer("extracted properties", list(vars(manifest_data).keys()))
    printer("interaction properties", list(vars(arms_P1_data).keys()))
    printer("named entities", list(vars(arms_entity_data).keys()))

    # t = Template()
    # dummy.get_dummy()
    # sentences = t.get_template_based_sentences(dummy)
    # print(sentences)

    # model_name = 'tuner007/pegasus_paraphrase'
    # torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # tokenizer = PegasusTokenizer.from_pretrained(model_name)
    # model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)
    
    # num_beams = 50
    # num_return_sequences = 5

    # print(get_response(sentences, num_return_sequences, num_beams))
