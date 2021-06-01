import numpy as np
import pandas as pd
import os
import re

# 清洗原始数据 得到形如"<BOS>i love china<EOS>"这样的句子 并将其放到同一个列表list_cleaned_sentences中
def get_cleaned_sentences():
    list_cleaned_sentences = []
    punctuations = '.!,;:?\-"\''
    with open("./metadata.txt",encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip().split("|")[-1]
            cleaned_sentence = re.sub(r'[{}]+'.format(punctuations), '', line)
            cleaned_sentence = cleaned_sentence.lower()
            cleaned_sentence = "<BOS>" + " " + cleaned_sentence + " " + "<EOS>"
            list_cleaned_sentences.append(cleaned_sentence)
    return list_cleaned_sentences

# 根据list_cleaned_sentences得到所有的单词及其频数 放置于字典dict_words_frequency中
def get_words_frequency(list_cleaned_sentences):
    dict_words_frequency = {}
    for single_sentence in list_cleaned_sentences:
        for word in single_sentence.split():
            if word in dict_words_frequency:
                dict_words_frequency[word] += 1
            else:
                dict_words_frequency[word] = 1
    return dict_words_frequency

# 根据清洗后的语料库和词频得到 矩阵 smooth表示是否使用数据平滑 True表示使用加一平滑 
def get_bigram_matrix(list_cleaned_sentences,dict_words_frequency,smooth=False):
    n = len(dict_words_frequency)
    m_index = dict_words_frequency.keys()
    m_columns = dict_words_frequency.keys()
    if smooth == True:
        dataframe_bigram_matrix = pd.DataFrame(np.ones((n,n)),index=m_index,columns=m_columns)
        iav = pd.Series(list(dict_words_frequency.values()),index=dict_words_frequency.keys()) + n
    else:
        dataframe_bigram_matrix = pd.DataFrame(np.zeros((n,n)),index=m_index,columns=m_columns)
        iav = pd.Series(list(dict_words_frequency.values()),index=dict_words_frequency.keys())
    for single_sentence in list_cleaned_sentences:
        list_words = single_sentence.split()
        for i in range(1,len(list_words)):
            front_word = list_words[i-1]
            rear_word = list_words[i]
            dataframe_bigram_matrix.at[front_word,rear_word] += 1
   
    dataframe_bigram_matrix = dataframe_bigram_matrix.div(iav,axis=0)
    return dataframe_bigram_matrix

# 获得处理后语料库中单个句子的MLE概率
def get_single_sentence_probability(dataframe_bigram_matrix,sentence):
    probability = 1
    list_words = sentence.split()
    for i in range(1,len(list_words)):
        front_word = list_words[i-1]
        rear_word = list_words[i]
        probability = dataframe_bigram_matrix.at[front_word,rear_word]
    return probability

# 根据用户的输入句子得到其MLE概率
def get_user_input_sentence_probability(dataframe_bigram_matrix,sentence):
    probability = 1
    punctuations = '.!,;:?\-"\''
    cleaned_sentence = re.sub(r'[{}]+'.format(punctuations), '', sentence)
    cleaned_sentence = cleaned_sentence.lower()
    cleaned_sentence = "<BOS>" + " " + cleaned_sentence + " " + "<EOS>"
    cleaned_sentence = cleaned_sentence.split()
    set_words = dataframe_bigram_matrix.index
    for x in cleaned_sentence:
        if x in set_words:
            continue
        else:
            print(x+" "+"is not in raw corpus!")
            return 0
    for i in range(1,len(cleaned_sentence)):
        front_word = cleaned_sentence[i-1]
        rear_word = cleaned_sentence[i]
        probability = dataframe_bigram_matrix.at[front_word,rear_word]
    return probability

# 获得推荐词语
def get_recommend_words(dataframe_bigram_matrix,word):
    m_index = dataframe_bigram_matrix.index
    if word not in m_index:
        print(word+" "+"is not in raw corpus!")
        return
    sr = dataframe_bigram_matrix.loc[word].sort_values(ascending=False) 
    return sr[0:5]

def main():
    list_cleaned_sentences = get_cleaned_sentences()
    dict_words_frequency = get_words_frequency(list_cleaned_sentences)
    # dataframe_bigram_matrix = get_bigram_matrix(list_cleaned_sentences,dict_words_frequency,smooth=True)
    print("Data smoothing?('y' or 'n')")
    is_smooth = str(input())
    if is_smooth == 'y':
        dataframe_bigram_matrix = get_bigram_matrix(list_cleaned_sentences,dict_words_frequency,smooth=True)
    elif is_smooth == 'n':
        dataframe_bigram_matrix = get_bigram_matrix(list_cleaned_sentences,dict_words_frequency,smooth=False)
    list_sentences_probability = []
    for sentence in list_cleaned_sentences:
        probability = get_single_sentence_probability(dataframe_bigram_matrix,sentence)
        list_sentences_probability.append(probability)
    while True:
        os.system("cls")
        print("***********Welcome to word recommened system!***********")
        print("1.Print the probability of a sentence in raw corpus.")
        print("2.Input a sentence, get the probability of this sentence (input 'q' to quit)")
        print("3.Enter recommended system (input 'q' to quit)")
        print("Input 'Q' or 'q' to quit!")
        input_str = str(input()).strip()
        if input_str == "1":
            print(list_sentences_probability)
            os.system("pause")
        elif input_str == "2":
            while True:
                print("Please input a sentence:",end="")
                user_input = str(input())
                if user_input == 'q':
                    break
                else:
                    usr_probability = get_user_input_sentence_probability(dataframe_bigram_matrix,user_input)
                    print("probability:"+str(usr_probability))
        elif input_str == "3":
            while True:
                print('Please input a word: ', end="")
                input_word = input().lower().strip()
                if input_word == 'q':
                    break
                else:
                    sr = get_recommend_words(dataframe_bigram_matrix, input_word)
                    print(sr)
        elif input_str == "Q" or input_str == "q":
            print("Bye!")
            os.system("pause")
            exit(0)
        else:
            continue


if __name__=="__main__":
    main()