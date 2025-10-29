import os
import re
import unicodedata
import random
from symspellpy import SymSpell

sym_spell_el = SymSpell()
sym_spell_el.load_dictionary('/home/jimmys/glossapi/spellcheck/lexicon_freq.txt', term_index=0, count_index=1)
sym_spell_en = SymSpell()
sym_spell_en.load_dictionary('/home/jimmys/glossapi/spellcheck/en-80k.txt', term_index=0, count_index=1)

dataset_dir = '/home/jimmys/glossapi/spellcheck/dataset'
files = sorted([f for f in os.listdir(dataset_dir) if f.endswith('.md')])

wrong_words_file = '/home/jimmys/glossapi/spellcheck/symspell_wrong_words.csv'
corrected_words_file = '/home/jimmys/glossapi/spellcheck/symspell_corrected_words.csv'

wrong_words = []
corrected_words = []

def detect_language(word, previous_language):
    # Detect if word is Greek or English based on >50% character composition.
    # In case of 50-50, use previous word's language if provided.
    
    greek = sum(1 for c in word if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
    english = sum(1 for c in word if 'A' <= c <= 'Z' or 'a' <= c <= 'z')

    if greek + english == 0:
        return None
    elif greek > english:
        return 'el'
    elif greek < english:
        return 'en'
    elif greek == english and previous_language is not None:
        return      
    else:
        return random.choice(['el', 'en'])

previous_language = None

for filename in files:
    with open(os.path.join(dataset_dir, filename), 'r', encoding='utf-8') as file:
        text = file.read()
    
    for word in text.split():
        # Normalize NFKC
        word = unicodedata.normalize("NFKC", word)
        # Lowercase
        word = word.lower()
        # Check if the lanugage of the word
        language = detect_language(word, previous_language)
        previous_language = language

        # The word is Greek
        if language == 'el':
            # Check if the word is 1:1 match in the dictionary
            if word in sym_spell_el.words:
                corrected_words.append((word, word, 1, 'el'))
                continue

            # Remove regex
            word = re.sub(r"[^α-ωά-ώΑ-ΩΆ-Ώ]", '', word)
            # Check if the word is 1:1 match in the dictionary again
            if word in sym_spell_el.words:
                corrected_words.append((word, word, 1, 'el'))
                continue
            
            # If the word has an accent mark and has at least 2 vowels only
            # Check if the word is in the dictionary with max edit distance 3 and remove accent marks
            if (
                any(c in ['ά','έ','ή','ί','ό','ύ','ώ'] for c in word) and \
                sum(1 for c in word if c in ['α','ε','η','ι','ο','υ','ω','ά','έ','ή','ί','ό','ύ','ώ']) >= 2
            ):
                # Check if the word is in the dictionary with max edit distance 3 before removing accent marks
                suggestions = sym_spell_el.lookup(word, verbosity=0, max_edit_distance=2)
                if suggestions:
                    corrected_words.append((word, suggestions[0].term, 2, 'el'))
                    continue
                # Remove accent marks
                word = ''.join(c for c in word if unicodedata.category(c) != 'Mn')

            # Check if the word is in the dictionary with max edit distance 3 after removing accent marks
            suggestions = sym_spell_el.lookup(word, verbosity=0, max_edit_distance=2)
            if suggestions:
                corrected_words.append((word, suggestions[0].term, 2, 'el'))
                continue

            # Check if the word is a compound word with max edit distance 3
            # compound_suggestions = sym_spell_el.lookup_compound(word, max_edit_distance=2)
            # if compound_suggestions:
            #     corrected_words.append((word, " ".join([s.term for s in compound_suggestions]), 3, 'el'))
            #     continue

            else:
                wrong_words.append((word, 'el'))


        # The word is English
        elif language == 'en':
            # Check if the word is 1:1 match in the dictionary
            if word in sym_spell_en.words:
                corrected_words.append((word, word, 1, 'en'))
                continue

            # Check if its an email or a link
            if re.match(r"[^@]+@[^@]+\.[^@]+", word) or re.match(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)", word):
                wrong_words.append((word, 'en'))
                continue

            # Remove everything than not a character and a apostrophe
            word = re.sub(r"[^a-z']", '', word)

            # Check if the word is 1:1 match in the dictionary again
            if word in sym_spell_en.words:
                corrected_words.append((word, word, 1, 'en'))
                continue

            # Check if the word is in the dictionary with max edit distance 3
            suggestions = sym_spell_en.lookup(word, verbosity=0, max_edit_distance=2)
            if suggestions:
                corrected_words.append((word, suggestions[0].term, 2, 'en'))
                continue

            # compound_suggestions = sym_spell_en.lookup_compound(word, max_edit_distance=2)
            # if compound_suggestions:
            #     corrected_words.append((word, " ".join([s.term for s in compound_suggestions]), 3, 'en'))
            #     continue

            else:
                wrong_words.append((word, 'en'))
            
        # The word is unknown
        else:
            wrong_words.append((word, 'unknown'))


# Write wrong words (preserve order)
with open(wrong_words_file, 'w', encoding='utf-8') as f:
    for word, lang in wrong_words:
        f.write(f"{word}, {lang}\n")

# Write corrected words (preserve order)
with open(corrected_words_file, 'w', encoding='utf-8') as f:
    for original, correction, flag, lang in corrected_words:
        f.write(f"{original}, {correction}, {flag}, {lang}\n")

print("Done!")