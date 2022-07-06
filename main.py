import json
import pdb
import math
from prompt_toolkit import prompt
import copy
import timeit

with open('words_list.json', 'r') as f:
    words_list=json.load(f)

with open('all_combi.json', 'r') as f:
    all_combi=json.load(f)

NBR_WORDS = len(words_list['list'])

def filtered(word, informations):
    for letter, info in informations.items():
        if 'nb' in info and word.count(letter) != info['nb']:
                return True

        if 'nb_min' in info and word.count(letter) < info['nb_min']:
                return True

        for pos in info.get('sure_pos', []):
            if word[pos] != letter:
                    return True
        if 'neg_pos' in info and letter in [l for i,l in enumerate(word) if i in info['neg_pos']]:
                return True
    return False



def update_info(word, info, output, copy_dict=False):
    new_info = copy.deepcopy(info) if copy else info
    for letter in word:
        new_info.setdefault(letter, {})
    word_dict = {x: [j for j,y in enumerate(word) if y==x] for i,x in enumerate(word)}

    for letter, positions in word_dict.items():

        zero_pos = [p for p in positions if output[p] == 0]
        neg_positions = [p for p in positions if output[p] == 1]
        sure_positions = [p for p in positions if output[p] == 2]


        # write/update of nb and nb_min informations
        if zero_pos:
            new_info[letter].update({'nb': len(positions) - len(zero_pos)})
            new_info[letter].pop('nb_min', None)
        elif 'nb' not in new_info[letter]:
            new_info[letter].update({'nb_min': len(positions)})


        # write/update of sure_pos
        if sure_positions:
            for sure_p in sure_positions:
                new_info[letter].setdefault('sure_pos', set())
                new_info[letter]['sure_pos'].add(sure_p)
            if new_info[letter].get('nb',0) == len(sure_positions) and 'neg_pos' in new_info[letter]:
                new_info[letter].pop('neg_pos')

        # write/update of neg_pos
        if neg_positions:
            for neg_p in neg_positions:
                new_info[letter].setdefault('neg_pos', set())
                new_info[letter]['neg_pos'].add(neg_p)

        if zero_pos and new_info[letter].get('nb',0)>0:
            for zero_p in zero_pos:
                new_info[letter].setdefault('neg_pos', set())
                new_info[letter]['neg_pos'].add(zero_p)
    return new_info


def compute_entropy(word, info, words_list):
    entropy = 0
    remaining_words_list = words_list.copy()
    while remaining_words_list:
        word_ans = remaining_words_list[0]
        combi = return_combinaison(word, word_ans)
        updated_info = update_info(word, info, combi, copy_dict=True)
        concerned_words = [r_word for r_word in remaining_words_list if not filtered(r_word, updated_info)]
        if concerned_words:
            proba = len(concerned_words)/len(words_list)
            entropy += (proba * math.log2(1/proba))
            remaining_words_list = [w for w in remaining_words_list if w not in concerned_words]
        else:
            remaining_words_list.pop(0)
    return entropy


def find_optimal_entropy(actual_words_list, info):
    max = 0
    retained_word = ""
    index = 0
    percent_list = [i for i in range(5,105,5)]
    for word in words_list['list']:
        percent = 100 * index / NBR_WORDS
        if percent > percent_list[0]:
            print(f'{percent_list[0]} %' )
            percent_list.pop(0)
        index+=1
        entropy = compute_entropy(word, info, actual_words_list)
        if entropy >= max:
            print(f'{word}  :  {entropy}')
            max = entropy
            retained_word = word
    return retained_word

def return_combinaison(word, answer):
    combi = []
    for ind, letter in enumerate(word):
        if letter == answer[ind]:
            combi.append(2)
            continue
        letter_in_answers = [i for i,l in enumerate(answer) if l==letter]
        if not letter_in_answers:
            combi.append(0)
            continue
        same_letter = [i for i,l in enumerate(word) if i!= ind and l==letter]
        if not same_letter:
            combi.append(1)
            continue

        up = set([i for i in same_letter if i<ind])-(set(letter_in_answers).intersection(set(same_letter)))
        down = set(letter_in_answers)-set(letter_in_answers).intersection(set(same_letter))
        if len(down)-len(up) >0:
            combi.append(1)
        else:
            combi.append(0)
    return combi


def get_combinaison(word, word_ans):
    return all_combi[word][word_ans]


all_combi = {}
for i, w_proposed in enumerate(words_list['list']):
    print(i)
    all_combi[w_proposed] = {}
    for w_answer in words_list['list']:
        all_combi[w_proposed][w_answer] = return_combinaison(w_proposed, w_answer)

with open("all_combi.json", "w") as outfile:
    json.dump(all_combi, outfile)

# info = update_info("TARIE", {}, [int(i) for i in '01000'])
# actual_words_list = words_list['list']
# actual_words_list = [word for word in actual_words_list if not filtered(word, info)]
#
#
# ent_comme = compute_entropy("COMME", info, actual_words_list)
# ent_blanc = compute_entropy("LOCUS", info, actual_words_list)
#
# print(f'entropy_comme: {ent_comme}')
# print(f'entropy_blanc: {ent_blanc}')

#########################################
############ MAIN LOOP ##################
#########################################

# proposed_word = find_optimal_entropy(words_list['list'], {})
# print('-----------------')
# print(proposed_word)

# print(timeit.repeat("for w in words_list['list']: return_combinaison('POMME', w)", "from __main__ import words_list, return_combinaison", number=1))



# c= True
# proposed_word = 'TARIE'
# nb_tries=0
# actual_words_list = words_list['list']
# info = {}
#
# print(f'Mot proposé: {proposed_word}')
# while c:
#     nb_tries += 1
#     input = prompt('Réponse ...: ')
#     if input == '22222':
#         print(f'Victoire en {nb_tries} coups')
#         break
#     info = update_info(proposed_word, info, [int(i) for i in input])
#     actual_words_list = [word for word in actual_words_list if not filtered(word, info)]
#     print(len(actual_words_list))
#     if len(actual_words_list) == 0:
#         print('Erreur: plus aucun mot possible')
#         break
#     elif len(actual_words_list) == 1:
#         proposed_word = actual_words_list[0]
#     else:
#         proposed_word = find_optimal_entropy(actual_words_list, info)
#     print(f'Mot proposé: {proposed_word}')
