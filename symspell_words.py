import os
import re
import unicodedata
from symspellpy import SymSpell

sym_spell = SymSpell()
sym_spell.load_dictionary('/home/jimmys/glossapi/spellcheck/el_GR_freq_zero_nfkc.txt', term_index=0, count_index=1)

dataset_dir = '/home/jimmys/glossapi/spellcheck/dataset'
files = sorted([f for f in os.listdir(dataset_dir) if f.endswith('.md')])

with open('/home/jimmys/glossapi/spellcheck/symspell_wrong_words.csv', 'w', encoding='utf-8') as f:
    for filename in files:
        with open(os.path.join(dataset_dir, filename), 'r', encoding='utf-8') as file:
            text = file.read()
        
        words = set()
        for word in text.split():
            # Skip numbers, emails, links
             # if 
            # 1. Normalize NFKC
            word_norm = unicodedata.normalize("NFKC", word)
            # 2. Lowercase
            word_norm = word_norm.lower()
            # 3. Remove punctuation
            word_norm = ''.join(c for c in word_norm if not unicodedata.category(c).startswith('P'))
            # 4. Check if the word is Greek
            if bool(re.search(r'[α-ωΑ-Ω]', word_norm)):
                # Strip all accent marks
                word_norm = ''.join(c for c in word_norm if unicodedata.category(c) != 'Mn')
                # Check if the word is in the dictionary
                if word_norm not in sym_spell.words:
                    # Check if the string is 2>= words
                    word_segments = sym_spell.word_segmentation(word_norm)
                    if len(word_segments.words) > 1:
                        words.add(word_norm)
                else:
                    words.add(word_norm)
            # 5. Its English
            else:
                pass
                    

            
        if words:
            f.write(f"{filename}\n")
            for word in sorted(words):
                f.write(f"{word}\n")

print("Done!")
