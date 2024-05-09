import math
import re
# List of filenames
filenames = ['merchant.txt', 'romeo.txt', 'tempest.txt', 'twelfth.txt', 'othello.txt',
             'lear.txt', 'ado.txt', 'midsummer.txt', 'macbeth.txt', 'hamlet.txt']

def clean_words(text):
    cleaned_text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = cleaned_text.split()
    cleaned_words = ' '.join(words)
    return cleaned_words

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
                    word_counts[word] = word_counts.get(word, 0) + 1
                    total_words += 1
        models[filename] = (word_counts, total_words)
        # print(filename, "\n")
        # if filename == "ado.txt":
        #     print(models[filename])

    return models

def classify_sentence(sentence, models, num_plays):
    cleaned_sentence = clean_words(sentence)
    sentence_words = cleaned_sentence.split()
    
    max_score = float('-inf')
    most_likely_play = None
    for play, (word_counts, total_words) in models.items():
        prob = 1/10
        # score = 0
        for word in sentence_words:
            if (word_counts.get(word, 0) != 0):
                word_prob = (word_counts.get(word, 0) +1) / (total_words + len(word_counts) + 1)
                # score += math.log(word_prob)
                prob += math.log(word_prob)
            else:
                prob += math.log(1/1000000)
        # score += -math.log(num_plays)  # Uniform prior
        if prob > max_score:
            # print("New high score! ", play, " with probability: ", prob)
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


# Train the model
models = train_model(filenames)

x = input()
print(classify_sentence(x,models, len(filenames)))
