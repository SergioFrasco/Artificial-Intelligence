# Imports for math and regular expressions
import math
import re

# List of filenames
filenames = ['merchant.txt', 'romeo.txt', 'tempest.txt', 'twelfth.txt', 'othello.txt',
             'lear.txt', 'ado.txt', 'midsummer.txt', 'macbeth.txt', 'hamlet.txt']

# this function removes puctuation etc using regex
def clean_words(text):
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = cleaned_text.split()
    cleaned_words = ' '.join(words)
    return cleaned_words

# this function is used to count the words
def bag_of_words(filename):
    word_counts = {}
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            cleaned_line = clean_words(line)
            for word in cleaned_line.split():
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1

    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    common_words = []

    # get the 3 most common words
    for word, count in sorted_words[:3]:
        common_words.append(word)
    words = ' '.join(common_words)

    return words

def train_model(filenames):
    models = {}
    for filename in filenames:
        word_counts = {}
        total_words = 0
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                cleaned_line = clean_words(line)
                words = cleaned_line.split()
                for word in words:
                    word_counts[word] = word_counts.get(word, 0)+1
                    total_words += 1
        models[filename] = (word_counts, total_words)
    return models

def classify_sentence(sentence, models, num_plays):
    cleaned_sentence = clean_words(sentence)
    sentence_words = cleaned_sentence.split()
    
    max_score = -1
    most_likely_play = None
    for play, (word_counts, total_words) in models.items():
        prob = 1/num_plays
        for word in sentence_words:
            if word_counts.get(word, 0) != 0:
                word_prob = (word_counts.get(word, 0) + 1) / (total_words + len(word_counts) + 1)
                prob += math.log(word_prob)
            else:
                prob += math.log(1e-6)
        if prob > max_score:
            max_score = prob
            most_likely_play = play

    # Replace the filename with the play name
    if most_likely_play is not None:
        most_likely_play = most_likely_play.replace('merchant.txt', 'The Merchant of Venice')
        most_likely_play = most_likely_play.replace('romeo.txt', 'Romeo and Juliet')
        most_likely_play = most_likely_play.replace('tempest.txt', 'The Tempest')
        most_likely_play = most_likely_play.replace('twelfth.txt', 'Twelfth Night')
        most_likely_play = most_likely_play.replace('othello.txt', 'Othello')
        most_likely_play = most_likely_play.replace('lear.txt', 'King Lear')
        most_likely_play = most_likely_play.replace('ado.txt', 'Much Ado About Nothing')
        most_likely_play = most_likely_play.replace('midsummer.txt', "Midsummer Night's Dream")
        most_likely_play = most_likely_play.replace('macbeth.txt', 'Macbeth')
        most_likely_play = most_likely_play.replace('hamlet.txt', 'Hamlet')

    return most_likely_play

def classifyWithProb(sentence, models, num_plays):
    cleaned_sentence = clean_words(sentence)
    sentence_words = cleaned_sentence.split()
    prob_logs = []

    for play, (word_counts, total_words) in models.items():
        num_logs = math.log(1/num_plays)  # Uniform prior
        for word in sentence_words:
            if word_counts.get(word, 0) != 0:
                word_prob = (word_counts.get(word, 0)+ 1)/(total_words + len(word_counts) + 1)
                num_logs += math.log(word_prob)
            else:
                num_logs += math.log(1/1000000)  #unseen words

        den_log = 0
        for _, (other_word_counts, other_total_words) in models.items():
            term_log = 0
            for word in sentence_words:
                if other_word_counts.get(word, 0) != 0:
                    word_prob = (other_word_counts.get(word, 0)+ 1)/(other_total_words + len(other_word_counts) + 1)
                    term_log += math.log(word_prob)
                else:
                    term_log += math.log(1e-6)
            den_log += math.exp(term_log)
        den_log = math.log(den_log)
        prob_log = num_logs-den_log
        prob_logs.append((play, prob_log))

    # ormalize log probabilities to probabilities
    log_prob_sum = sum(math.exp(log_prob) for _, log_prob in prob_logs)
    probabilities = [(play, round(100 * math.exp(log_prob) / log_prob_sum, 2)) for play, log_prob in prob_logs]

    #Sort and print
    sorted_probabilities = sorted(probabilities, key=lambda x: x[1], reverse=True)
    for play, prob in sorted_probabilities:
        play_name = play.replace('merchant.txt', 'The Merchant of Venice')
        play_name = play_name.replace('romeo.txt', 'Romeo and Juliet')
        play_name = play_name.replace('tempest.txt', 'The Tempest')
        play_name = play_name.replace('twelfth.txt', 'Twelfth Night')
        play_name = play_name.replace('othello.txt', 'Othello')
        play_name = play_name.replace('lear.txt', 'King Lear')
        play_name = play_name.replace('ado.txt', 'Much Ado About Nothing')
        play_name = play_name.replace('midsummer.txt', "Midsummer Night's Dream")
        play_name = play_name.replace('macbeth.txt', 'Macbeth')
        play_name = play_name.replace('hamlet.txt', 'Hamlet')
        print(f"{play_name}: {round(prob)}%")


x = input() #Take in input
models = train_model(filenames) #Train the model
classifyWithProb(x, models, len(filenames)) #Get the porbabilites