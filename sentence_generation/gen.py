from data_processing.parse_manifest import parse
from data_processing.template import Template
from data_type.extracted_data import ExtractedData

import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

def get_response(input_text,num_return_sequences,num_beams):
  batch = tokenizer([input_text],truncation=True,padding='longest',max_length=240, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=240,num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  return tgt_text

if __name__ == "__main__":
    # parse("../original_web_interface/ApplicationManifest.json")
    t = Template()
    dummy = ExtractedData()
    dummy.get_dummy()
    sentences = t.get_template_based_sentences(dummy)
    print(sentences)

    model_name = 'tuner007/pegasus_paraphrase'
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)
    
    num_beams = 50
    num_return_sequences = 5

    print(get_response(sentences, num_return_sequences, num_beams))
