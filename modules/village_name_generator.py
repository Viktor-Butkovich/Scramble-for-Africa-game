import random

def create_village_name():
    l = random.randrange(1, 4) + 1 + random.randrange(1, 4) + 1
    vname = ''
    ch = random.randrange(1, 6) + 1
    if ch < 6:
        lm = 1
    elif ch == 6:
        lm = -1
    if lm == 1:
        vname = add_consonant(vname)
    elif lm == -1:
        vname = add_vowel(vname)
    for i in range(0, l):#lowercase L, not 1
        ch = random.randrange(1, 19) + 1
        if ch < 15:
            lm = lm * -1
        #elif ch > 14 and ch < 19:
        #    do nothing
        elif ch == 19:
            vname = add_space(vname)
        if lm == 1:
            vname = add_consonant(vname)
        elif lm == -1:
            vname = add_vowel(vname)
    final_vname = ''
    for letter_index in range(0, len(vname)):
        if not vname[letter_index] == 'space' and not letter_index == 0 and not vname[letter_index - 1] == ' ':
            current_letter = vname[letter_index].lower()
        else:
            current_letter = vname[letter_index]
        final_vname = final_vname + current_letter
    return(final_vname)

def add_space(base):
    return(base + ' ')

def add_vowel(base):
    weighted_vowels = ['A', 'A', 'A', 'A', 'A', 'E', 'E', 'I', 'I', 'O', 'O', 'O', 'U', 'U']
    return(base + random.choice(weighted_vowels))

def add_consonant(base):
    weighted_consonants = ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'N', 'N', 'N', 'N', 'N', 'N', 'P', 'Q', 'R', 'S', 'S', 'S', 'T', 'T', 'T', 'V', 'W', 'X', 'Y', 'Z']
    return(base + random.choice(weighted_consonants))

#for i in range(1, 10):
#    print(create_village_name())
