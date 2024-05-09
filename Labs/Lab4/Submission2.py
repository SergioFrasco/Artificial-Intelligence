import re

def cleanWords(text):
    cleanedText = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    words = cleanedText.split()
    cleanedWords = ' '.join(words)
    return cleanedWords

def bagOfWords(filename):
    word_counts = {}
    
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            cleanedLine = cleanWords(line)
            for word in cleanedLine.split():
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1
    
    sortedWords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    commonWords = []
    for word, count in sortedWords[:3]:
        commonWords.append(word)
    
    words = ' '.join(commonWords)
    return words

x = input()
print(bagOfWords(x))
