from transformers import AutoModelWithLMHead, AutoTokenizer
import torch
from tqdm import tqdm
from datasets import load_dataset
import argparse

parser = argparse.ArgumentParser(description = "A tool that evaluate the perplexity of a sentence/list of sentence in a txt file\n"+
                                                 "Using transformers LM Model with pretrained weights"
                                 )

parser.add_argument("-f","--file-input", help="text file input, separated by carriage return")
parser.add_argument("-s","--single",help="Single line input, for single use case")
parser.add_argument("-m","--model",help="Model in hugging face")

arg = parser.parse_args()
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

if arg.model:
    model_id = arg.model
else:
    model_id = 'roberta-base'


if arg.single:
    test_sentences = [arg.single]
elif arg.file_input:
    with open(arg.file_input,'r',encoding='utf-8') as f:
        test_sentences = f.readlines()
#for demo
else:
    test_sentences = load_dataset('wikitext', 'wikitext-2-raw-v1', split='test')['text']
    
              
def main():
    model = AutoModelWithLMHead.from_pretrained(model_id).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    encodings = tokenizer('\n\n'.join(test_sentences), return_tensors='pt')

    #use sliding windows with big window to compute perplexity as model has fixed length
    max_length = 512
    stride = 1

    lls = []
    for i in tqdm(range(0, encodings.input_ids.size(1), stride)):
        begin_loc = max(i + stride - max_length, 0)
        end_loc = min(i + stride, encodings.input_ids.size(1))
        trg_len = end_loc - i    # may be different from stride on last loop
        input_ids = encodings.input_ids[:,begin_loc:end_loc].to(device)
        target_ids = input_ids.clone()
        target_ids[:,:-trg_len] = -100   #invalidate the context tokens

        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            log_likelihood = outputs[0] * trg_len

        lls.append(log_likelihood)

    ppl = torch.exp(torch.stack(lls).sum() / end_loc)
    print(f"The average perplexity is: {ppl}")

if __name__ == "__main__":
    main()