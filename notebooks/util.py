

import numpy as np
import json
import re
import random

def load_glove(
        weight_file = '../processed_data/glove6B100d.npy',
        vocab_file = '../processed_data/glove_vocab.json',
        ivocab_file='../processed_data/glove_ivocab.json'
        ):
    #Loading the data
    W_norm = np.load(weight_file)
    with open(vocab_file,'r') as f:
        vocab = json.load(f)
    with open(ivocab_file,'r') as f:
        ivocab = json.load(f)
    return W_norm,vocab,ivocab

def load_training_batch(train_iter,batch_size):
    train_data = []
    if type(train_iter) == type([]):   #list of files
        for file in train_iter:
            with open(file,'r') as f:
                lines = f.readlines()
                for i in range(0,len(lines)-batch_size,batch_size):
                    train_data.append(lines[i:i+batch_size])
    if type(train_iter) == str:   #single file
        with open(train_iter,'r') as f:
            lines = f.readlines()
            for i in range(0,len(lines)-batch_size,batch_size):
                train_data.append(lines[i:i+batch_size])
    random.shuffle(train_data)
    return  train_data #shuffle the data


pad_tensor = np.zeros(100)
unk_tensor = np.ones(100)

def get_glove_vec(word,W_norm,vocab):
    if word == '<pad>':
        return pad_tensor
    elif word not in vocab:
        return unk_tensor
    else: 
        return W_norm[vocab[word]]
    
#Creating training tensor - list of tuple of (feats,labels), both of which are np array
def get_embedding(train_data,W_norm,vocab):
    train_tensor = []
    for i,batch in enumerate(train_data):
        tensor_list = []
        label_list = []
        for sentence in batch:
            y,x = sentence.split(':')
            s = re.sub('[\n\r\ ]+',' ',x).strip()
            tensor_list.append([get_glove_vec(word,W_norm,vocab) for word in s.split(' ')])
            label_list.append(get_glove_vec(y,W_norm,vocab))
        train_tensor.append((np.array(tensor_list),np.array(label_list)))
    return train_tensor