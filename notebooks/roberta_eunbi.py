import json,re,os,random
import numpy as np

from datetime import date
from tqdm import tqdm 

import wandb

import torch
import torch.nn as nn
import torch.optim as optim 
from transformers import AutoTokenizer, AutoModel, AutoConfig

from util import *

####~~~~~~~~~~~~GLOBAL CONFIG~~~~~~~~~~~~~~~~~~~~~###


#setup roberta
checkpoint='roberta-base'
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
config = AutoConfig.from_pretrained(checkpoint)
roberta_model = AutoModel.from_pretrained(checkpoint)
vocab = tokenizer.vocab
roberta_embeddings = roberta_model.embeddings.word_embeddings.weight
special_token_ids = tokenizer.convert_tokens_to_ids([tokenizer.pad_token,tokenizer.unk_token])

#setup our model
class DenseNet(nn.Module):
    def __init__(self,context_length,embed_size=100):
        super().__init__()
        self.n = context_length*2
        self.embed_size = embed_size
        self.act = nn.ReLU()
        self.out = nn.Tanh() 
        self.hidden1 = nn.Linear(self.n*self.embed_size,2048)
        self.hidden2 = nn.Linear(2048,512)
        self.hidden3 = nn.Linear(512,self.embed_size)
 
    def forward(self,x):
        x = x.view(x.size(0), -1)
        x = self.act(self.hidden1(x))
        x = self.act(self.hidden2(x))
        x = self.out(self.hidden3(x))
        return x
    


#the functions
def token_to_id(word):
        if word in vocab:
            return vocab[word]
        elif word == tokenizer.pad_token:
            return special_token_ids[0]
        else:
            return special_token_ids[1]

def get_roberta_embedding(train_data):
    train_tensor = []
    for i,batch in enumerate(train_data):
        batch_tensor_list = []
        batch_label_list = []
        for sentence in batch:
            try:
                y,x = sentence.split(':')
                s = re.sub('[\n\r\ ]+',' ',x).strip()
                input_ids = [token_to_id(word) for word in s.split(' ')]
                context_embeddings = roberta_embeddings[input_ids].detach()
                batch_tensor_list.append(context_embeddings)
                y_id = token_to_id(y)
                label_embedding = roberta_embeddings[y_id].detach()
                batch_label_list.append(label_embedding)
            except Exception as e:
                print(sentence)
                print(e)
                return
        train_tensor.append(
            (torch.stack(batch_tensor_list),torch.stack(batch_label_list))
        )
    return train_tensor


#the data setup
corpus = 'giga'

files_available = [x[:x.find('_')] for x in os.listdir(f'../processed_data/{corpus}_only/') if x.endswith('.txt')]

def negative_sample(target,files,n=4):
    negatives = [x for x in files if x != target]
    return [target] + random.sample(negatives,n)

whatever_we_want_to_rerun = {x:negative_sample(x,files_available,2) for x in ['disease','pneumonia']}

#the master loop
for data_name,training_words in whatever_we_want_to_rerun.items():
    wandb.init(project='Synthetic Net Roberta')
    config = wandb.config
        #the hyper
    config.batch_size = 64
    model = DenseNet(context_length = 10,embed_size=768)
    training_files_fullpath = [f'../processed_data/{corpus}_only/{x}_corpus_stopwords_c10.txt' for x in training_words]
    training_data = load_training_batch(training_files_fullpath,config.batch_size)
    config.data = f"{corpus}_only_{'-'.join(training_words)}"
    

    #list of tuples of tensors

    train_tensor = get_roberta_embedding(training_data)

    config.lr = 0.0005
    config.momentum = 0.005
    optimizer = optim.SGD(model.parameters(),lr=config.lr,momentum=config.momentum,weight_decay=0.01)
    criterion = nn.L1Loss()

    def cosim(v1,v2):
        return np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))

    #scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, debug_set.shape[0], eta_min=config.lr)
    #learning rate adjustment -- try 0.001

    def train(model, iterator, optimizer, criterion):

        epoch_loss = 0
        epoch_acc = 0

        model.train()
        for batch in iterator:
            optimizer.zero_grad()
            features,labels = batch
            feat = features
            label = labels
            predictions = model(feat).squeeze(1)
            loss = criterion(predictions,label)  
            loss.backward()

            optimizer.step()
            epoch_loss += loss.item()

            cosim_score = np.mean([cosim(labels[i].detach().numpy(),predictions[i].detach().numpy()) for i in range(config.batch_size) ])

        return epoch_loss,cosim_score

    config.epochs = 40

    best_valid_loss = float('inf')

    for epoch in tqdm(range(config.epochs)):   
        train_loss,cosim_score= train(model,iter(train_tensor), optimizer, criterion)

        #epoch_mins, epoch_secs = epoch_time(start_time, end_time)

        #if valid_loss < best_valid_loss:
         #   best_valid_loss = valid_loss
          #  torch.save(model.state_dict(), 'tut1-model.pt')

        #print(f'Epoch: {epoch+1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s')
        wandb.log({"loss":train_loss,"cosim_score":cosim_score})
        print(f'Epoch:{epoch+1:02}\t|\tTrain Loss: {train_loss:.3f}\t|\tCosim score: {cosim_score:.3f}')

    torch.save(model.state_dict(),f'../outputs/{date.today().strftime("%Y-%m")}_{config.data}_{wandb.run.name}.pt')
    wandb.finish()