import re #package to help clean the text

def cleanWords(text):
    cleanedText = re.sub(r'[^a-zA-Z\s]', '', text).lower() # remove non-alphabetic characters
    words = cleanedText.split() # split
    cleanedWords = ' '.join(words) # join words with space
    return cleanedWords

x = input()
print(cleanWords(x))

# print(cleanWords("Your Grace hath ta'en great pains to qualify"))
# print(cleanWords("_Juliet._ How art thou out of breath, when thou hast breath?"))
# print(cleanWords("To hear good counsel; O, what learning is!"))