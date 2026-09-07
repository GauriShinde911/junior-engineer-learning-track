import string
from collections import Counter

# reads a text file, strips punctuation, and counts word occurrences
def count_words_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
        
    # remove punctuation and convert to lowercase
    cleaned_text = text.translate(str.maketrans("", "", string.punctuation)).lower()
    words = cleaned_text.split()
    
    word_counts = Counter(words)
    return word_counts

if __name__ == "__main__":
    file_path = "sample_text.txt"
    print(f"Analyzing word frequency in '{file_path}'...\n")
    
    counts = count_words_in_file(file_path)
    
    print("Top 5 Most Common Words:")
    for word, count in counts.most_common(5):
        print(f"  - '{word}': {count} times")
