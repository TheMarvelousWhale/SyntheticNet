## we will collect all sentences with the word cat as center word
import re
import os
from nltk.corpus import stopwords
from tqdm import tqdm


stopword_list = stopwords.words('english')

def extract(sentence,target_word,context_length,pad,debug=True):
    target_word = target_word.lower()
    sentence = sentence.lower()
    if target_word not in sentence: #reduce processing
        return
    
    s = sentence.lower().strip()
    s = re.sub('[\n\r\ ]+',' ',s)
    s = re.sub('[^a-z ]+','',s)
    
    t = target_word
    raw_tokens = s.split(' ')
    tokens = [i for i in raw_tokens if i != '' and i not in stopword_list]
    word_list = []
    if t in tokens:
        __index = tokens.index(t)        # this only get one utterance, what about other utterances? 
        if __index < context_length:      #pad front
            word_list += [pad for _ in range(context_length-__index)]
            word_list += tokens[:__index]      #pad back
        else:
            word_list += tokens[__index-context_length:__index]
        if __index + context_length >= len(tokens):
            word_list += tokens[__index+1:]
            word_list += [pad for _ in range(context_length + __index + 1 - len(tokens))]
        else:
            word_list += tokens[__index+1:__index+context_length+1]
        return word_list


    else:   #target not found:
        return None
    
    
#collect filepaths

wiki_dataset_dir = "../../Datasets/text"
gigaword_dir = "../../Datasets/gigaword"
filepath_list = []
wiki = False
giga = True
#Extracting from wiki 
if wiki == True:
    for folder in os.listdir(wiki_dataset_dir):
        for file in os.listdir(wiki_dataset_dir+'/'+folder):
            filepath_list.append(wiki_dataset_dir+'/'+folder+'/'+file)
        
#Extracting from gigaword 
if giga == True:
    for file in os.listdir(gigaword_dir):
        filepath_list.append(gigaword_dir+'/'+file)
print(f"Number of files is: {len(filepath_list)}")

target_words = ['area', 'authority', 'cat', 'city', 'class', 'command', 'computer', 'contagion', 'cute', 'director', 'district', 'dog', 'flu', 'governor', 'infection', 'influence', 'land', 'leader', 'location', 'mentor', 'pandemic', 'place', 'poison', 'position', 'president', 'shark', 'site', 'speak', 'teacher', 'university', 'whale']
                
context_length = 10
corpusname = "giga" if giga == True else "wiki"
for target_word in target_words:
    line_written = 0
    corpus = f"../processed_data/{corpusname}_only/{target_word}_corpus_stopwords_c{context_length}.txt"
    with open(corpus,'a') as o10:
        for file in tqdm(filepath_list):
            with open(file,'r',encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    result = extract(line,target_word,context_length,"<pad>",True)
                    if result == None:
                        continue
                    else:
                        o10.write(f'{target_word}:')
                        o10.write(''.join([i+' ' for i in result] ))
                        o10.write('\n')
                        line_written += 1
                        if line_written % 10000 == 0:
                            print(f"Written {line_written} into file {corpus}")
        print(f"\n\n DONE WITH CORPUS {corpus}\n\n")


