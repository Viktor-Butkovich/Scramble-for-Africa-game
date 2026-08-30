# Contains functions that randomly generate village names

import random
from modules.constants import constants, status, flags


def create_village_name():
    """
    Description:
        Returns a randomly generated village name
    Input:
        None
    Output:
        string: Randomly generated village name
    """
    l = random.randrange(1, 4) + 1 + random.randrange(1, 4) + 1
    vname = ""
    ch = random.randrange(1, 6) + 1
    if ch < 6:
        lm = 1
    elif ch == 6:
        lm = -1
    if lm == 1:
        vname += get_weighted_consonant()
    elif lm == -1:
        vname += get_weighted_vowel()
    for i in range(0, l):  # lowercase L, not 1
        ch = random.randrange(1, 19) + 1
        if ch < 15:
            lm = lm * -1
        elif ch == 19:
            vname += " "
        if lm == 1:
            vname += get_weighted_consonant()
        elif lm == -1:
            vname += get_weighted_vowel()
    return postprocess_village_name(vname)


def postprocess_village_name(vname: str) -> str:
    """
    Description:
        Returns a postprocessed version of the inputted village name, adding capitalization, avoiding triple consonants, and adding apostrophes
    Input:
        string vname: Village name to postprocess
    Output:
        string: Postprocessed version of the inputted village name
    """
    # Avoid triple consonants
    chars = list(vname)
    i = 0
    while i < len(chars) - 2:
        if (
            (chars[i] in constants.consonants)
            and (chars[i + 1] in constants.consonants)
            and (chars[i + 2] in constants.consonants)
            and (random.randrange(1, 11) != 1)
        ):
            chars[i + 1] = get_weighted_vowel()
            i += 2
        else:
            i += 1

    # Add apostrophes
    if len(chars) > 2 and random.randrange(1, 11) == 1:
        valid_positions = [
            i
            for i in range(1, len(chars) - 1)
            if chars[i - 1] != " " and chars[i] != " " and chars[i + 1] != " "
        ]
        if valid_positions:
            apostrophe_index = random.choice(valid_positions)
            chars.insert(apostrophe_index, "'")

    # Capitalization formatting
    vname = "".join(chars)
    final_vname = ""
    for letter_index in range(0, len(vname)):
        if (
            not vname[letter_index] == " "
            and not letter_index == 0
            and not vname[letter_index - 1] == " "
        ):
            current_letter = vname[letter_index].lower()
        else:
            current_letter = vname[letter_index]
        final_vname += current_letter
    return final_vname


def get_weighted_vowel() -> str:
    """
    Description:
        Returns a vowel chosen from a weighted list
    Input:
        string base: string to add a vowel to
    Output:
        string: Random weighted vowel
    """
    return random.choices(
        list(constants.weighted_vowels.keys()),
        weights=list(constants.weighted_vowels.values()),
        k=1,
    )[0]


def get_weighted_consonant() -> str:
    """
    Description:
        Returns a consonant chosen from a weighted list
    Input:
        string base: string to add a consonant to
    Output:
        string: Random weighted consonant
    """
    return random.choices(
        list(constants.weighted_consonants.keys()),
        weights=list(constants.weighted_consonants.values()),
        k=1,
    )[0]
