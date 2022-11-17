#pytorch
#!pip install transformers==4.20.0
#!pip install https://github.com/kpu/kenlm/archive/master.zip
#!pip install pyctcdecode==0.4.0
from transformers.file_utils import cached_path, hf_bucket_url
from importlib.machinery import SourceFileLoader
from transformers import Wav2Vec2ProcessorWithLM
from IPython.lib.display import Audio
import torchaudio
import torch

# Load model & processor
model_name = "nguyenvulebinh/wav2vec2-base-vi-vlsp2020"
# model_name = "nguyenvulebinh/wav2vec2-large-vi-vlsp2020"
model = SourceFileLoader("model", cached_path(hf_bucket_url(model_name,filename="model_handling.py"))).load_module().Wav2Vec2ForCTC.from_pretrained(model_name)
processor = Wav2Vec2ProcessorWithLM.from_pretrained(model_name)

# Load an example audio (16k)
# audio, sample_rate = torchaudio.load(cached_path(hf_bucket_url(model_name, filename="t2_0000006682.wav")))
audio, sample_rate = torchaudio.load("37303134325f3137.wav")
input_data = processor.feature_extractor(audio[0], sampling_rate=16000, return_tensors='pt')

# Infer
output = model(**input_data)

# Output transcript without LM
print(processor.tokenizer.decode(output.logits.argmax(dim=-1)[0].detach().cpu().numpy()))

# Output transcript with LM
print(processor.decode(output.logits.cpu().detach().numpy()[0], beam_width=100).text)