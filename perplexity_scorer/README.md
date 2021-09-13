## Perplexity Scorer

This tool is used to evaluate the perplexity of a sentence/list of sentences using one of the transformer models. 

Run python perplexity_scorer.py -s "\[Your Sentence\]" or python perplexity_scorer.py -f \[input_file\]

The model being used is a masked language model - roberta-base. You can change it with the -m flag

Dependencies:
* transformers
* tqdm 
* torch 
* datasets (for demo only) 

We can use AutoModelForCausalLM for causal LM model like GPT-2, or MaskedLM like Bert, or Seq2seq LM
I used the AutoModelWithLMHead so we can ignore this decision, but it's a deprecated method (beware!) 

Any other issues can be helped by running the -h flag :> 