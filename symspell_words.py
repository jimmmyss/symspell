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
            #Normalization epeidi exoun diaforetiko encoding oi lekseis kai tis bgazei san lathos
            word_norm = unicodedata.normalize("NFKC", word)
            if bool(re.search(r'[α-ωΑ-Ωά-ώ]', word_norm)):
                if word_norm not in sym_spell.words:
                    words.add(word_norm)
        
        if words:
            f.write(f"{filename}\n")
            for word in sorted(words):
                f.write(f"{word}\n")

print("Done!")