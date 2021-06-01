import re
import numpy as np

def removePunctuation(sentence_str):
    '''给定字符串，进行特殊符号过滤，以及小写转换
    Args:
        sentence_str (str): 句子
    
    Returns:
        sentence_str.lower() (str): 预处理过的句子
    '''
    punctuation = '.!,;:?\-"\''
    sentence_str = re.sub(r'[{}]+'.format(punctuation),'',sentence_str)
    return sentence_str.lower()

def get_sentence(filename):
    '''从给定文件中获取句子
    Args:
        filename (str): 语料库的文件名
    
    Returns:
        sentences_list (list): 1-D，存放了所有经过预处理后的句子
    '''
    sentences_list = []
    with open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            sentence_str = removePunctuation(line.strip().split('|')[-1])
            sentences_list.append('<s> ' + sentence_str + ' </s>')
    return sentences_list

def count_word(sentences_list):
    '''给定大量句子，统计出所有单词出现的频次
    Args:
        sentences_list (list): 所有经过预处理后的句子
    
    Returns:
        wordcount_dict (dict): 键是str类型，表示单词；值是int类型，表示次数，例如{'the': 1234}
    '''
    wordcount_dict = {} 
    for sentence_str in sentences_list:
        for word in sentence_str.split():
            if word in wordcount_dict:
                wordcount_dict[word] += 1
            else:
                wordcount_dict[word] = 1
    return wordcount_dict

def word2idx(wordcount_dict):
    '''构建单词到索引的映射与逆映射
    Args:
        wordcount_dict (dict): 键是str类型，表示单词；值是int类型，表示次数
    
    Returns:
        word2idx_dict (dict): 键是str类型，表示单词；值是int类型，表示索引，例如{'the': 0}
        idx2word_dict (dict): 键是int类型，表示索引；值是str类型，表示单词，例如{0: 'the'}
    '''
    word2idx_dict = {}
    idx2word_dict = {}
    for idx, word in enumerate(list(wordcount_dict.keys())):
        word2idx_dict[word] = idx
        idx2word_dict[idx] = word
    return word2idx_dict, idx2word_dict

def c_table(word2idx_dict, sentences_list, smooth=False):
    '''构建两个单词连续出现的频次矩阵
    Args:
        word2idx_dict (dict): 键是str类型，表示单词；值是int类型，表示索引
        sentences_list (list): 所有经过预处理后的句子
        smooth (bool): 是否进行加一平滑
    
    Returns:
        c_table_np (numpy): 2-D，c_table_np[i][j] = a表示 前一个索引为i的词和当前索引为j的词 同时出现的次数为a
    '''
    n = len(word2idx_dict) # 单词个数
    c_table_np = np.zeros((n, n)) # n*n 全0矩阵
    for sentence_str in sentences_list:
        words_list = sentence_str.split() # ['i', 'like', 'apple']
        for i in range(1, len(words_list)):
            w_i = word2idx_dict[words_list[i]] # w_i
            w_j = word2idx_dict[words_list[i-1]] # w_{i-1}
            c_table_np[w_j][w_i] += 1
    
    if smooth: # 加一平滑
        c_table_np[c_table_np == 0] = 1
    
    return c_table_np

def compute_bigram_table(c_table_np, wordcount_dict):
    '''构建bigram概率矩阵
    Args:
        c_table_np (numpy): bigram频次矩阵
        wordcount_dict (dict): 所有单词出现的次数
    
    Returns:
        c_table_np / count_np[:, None] (numpy): 2-D，bigram概率矩阵
    '''
    count_np = np.array(list(wordcount_dict.values())) # [800, 900, 788, ...]
    return c_table_np / count_np[:, None]

def compute_sentence_bigram(bigram_table_np, word2idx_dict, sentences_list):
    '''计算每个句子的bigram概率
    Args:
        bigram_table_np (numpy): bigram概率矩阵
        word2idx_dict (dict): 单词到索引的映射
        sentences_list (list): 预处理后的句子
    
    Returns:
        scores_list (list): 所有句子的bigram概率
    '''
    scores_list = []
    for sentence_str in sentences_list:
        words_list = sentence_str.split()
        score = 1
        for i in range(1, len(words_list)):
            w_i = word2idx_dict[words_list[i]] # w_i
            w_j = word2idx_dict[words_list[i-1]] # w_{i-1}
            score *= bigram_table_np[w_j][w_i]
        scores_list.append(score)
    return scores_list

import heapq

def get_recommend_words(idx, bigram_table_np, idx2word_dict):
    m_list = list(bigram_table_np[idx])
    max_number = heapq.nlargest(7, m_list)
    max_index_list = []
    for t in max_number:
        index = m_list.index(t)
        max_index_list.append(index)
        m_list[index] = 0
    
    return [idx2word_dict[i] for i in max_index_list if idx2word_dict[i] not in ['<s>', '</s>']]


if __name__ == '__main__':
    # sentences_list = get_sentence('metadata.txt')
    # wordcount_dict = count_word(sentences_list)
    # word2idx_dict, idx2word_dict = word2idx(wordcount_dict)
    # c_table_np = c_table(word2idx_dict, sentences_list, True)
    # bigram_table_np = compute_bigram_table(c_table_np, wordcount_dict)
    # scores_list = compute_sentence_bigram(bigram_table_np, word2idx_dict, sentences_list)
    # print(scores_list[:10])
    sentences_list = get_sentence('metadata.txt')
    wordcount_dict = count_word(sentences_list)
    word2idx_dict, idx2word_dict = word2idx(wordcount_dict)
    c_table_np = c_table(word2idx_dict, sentences_list, True)
    bigram_table_np = compute_bigram_table(c_table_np, wordcount_dict)
    while True:
        print('Please input a word: ', end="")
        word = input().strip().lower()
        if word not in word2idx_dict:
            print('None')
            break
        else:
            recommend_word = get_recommend_words(word2idx_dict[word], bigram_table_np, idx2word_dict)
            print(recommend_word[:5])