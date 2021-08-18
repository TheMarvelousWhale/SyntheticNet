# Report for EunbiNet

![7](./../assets/index.jpg)

### 1. Preliminaries work 

We aim to create new embeddings from scratch at a low cost, via a neural compositional approach. 

The steps proposed are as followed:
1. Build a shallow net that take in 4 word context (c = 2). Filter words that are not in the vocab
2. Train the net on the examples
3. Compare the word vector produced with:
   *    For original GloVe, its own embedding mean difference across dims 
   *    For outside Glove, analogy (nearest neighbours)
4. Further optimized the following:
   *    The architecture (deeper, cnn like)
   *    Adopting attention 

**2021/05/09**
* able to load the [stanford glove vectors](https://nlp.stanford.edu/projects/glove/) and build vocab from there 
* need to crawl a corpus of certain words (covid, pfizer) and run a simple dense layer on it. 

Task:
* what is the cost function? 
* Visualizing vectors 


### Current Progress (dated July 2021)

# Current result:
Successfully replicate embeddings for several keywords (cat, pneumonia, sick, etc. )
