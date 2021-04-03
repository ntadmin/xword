#!/usr/bin/python3
# codeword.py
# Solve the the codeword puzzle
#
#
# John Clarke, john@johnclarke.net
# V0.1 2021-03-30

import re, os

def setPuzzle():
    """
    Returns a tuple of tuples containing the puzzle to be solved
    :return: matrix: tuple
    """
    matrix = tuple()  # This will be a tuple of tuples to hold the original puzzle set

    matrix += ((0, 25, 0, 21, 0, 4, 0, 8, 0, 17, 0),)
    matrix += ((12, 22, 13, 8, 18, 8, 0, 18, 2, 13, 8),)
    matrix += ((0, 14, 0, 24, 0, 21, 0, 22, 0, 22, 0),)
    matrix += ((5, 13, 26, 20, 0, 16, 20, 9, 13, 7, 13),)
    matrix += ((0, 7, 0, 5, 0, 20, 0, 3, 0, 0, 9),)
    matrix += ((20, 16, 22, 0, 0, 0, 0, 0, 21, 17, 3),)
    matrix += ((17, 0, 0, 8, 0, 23, 0, 1, 0, 21, 0),)
    matrix += ((9, 21, 10, 11, 4, 20, 0, 10, 21, 3, 18),)
    matrix += ((0, 18, 0, 4, 0, 8, 0, 13, 0, 3, 0),)
    matrix += ((7, 22, 6, 21, 0, 18, 21, 25, 17, 20, 18),)
    matrix += ((0, 9, 0, 18, 0, 19, 0, 8, 0, 15, 0),)

    return matrix


# =============== Extract words ===============

# Horizontal words: Have a word list. This will be a list of lists. First two elements
# are the position of the first letter.
# For each row, start at [0] and test if non-zero.
# If it's non-zero, test whether next element is non-zero. If it is, this is becoming a word.
# Add the first two letters to a tentative word, then progress until we hit a zero. Add
# the word to the word list - also need to store the location of the word (or at least of
# the first letter).

def showPuzzle(matrix, knownLetters):
    for row in matrix:
        print("+--"*len(row),end="+\n")
        print(end="|")
        for element in row:
            if element == 0:
                print("XX", end="|")
            else:
                print(f"{element:2d}", end="|")
        print()
        print(end="|")
        for element in row:
            if element == 0:
                print("XX", end="|")
            else:
                letter = knownLetters.get(element)
                if letter != None:
                    print(letter.capitalize(),end=" |")
                else:
                    print("  ", end="|")
        print()
    print("+--"*len(row),end="+\n")
    

def showAwcList(wcList):
    for word_candidates in wcList:
        print("Word %s has %s possible solutions" % (word_candidates[0], "{:,}".format(len(word_candidates) - 1)))
 

def parse(m: tuple):
    """
    Parse the puzzle matrix both across and down to find words to solve.
    Return results as a list of lists. Each inner list represents one word and is structured:
    [(direction, row, col), n1, n2, n3,...] where n1... is the code for the letter

    :param m:
    :return: word_list: list
    """
    directions = ['across', 'down']
    word = list()  # Used to store the word we're working on
    word_list = list()  # Stores the growing list of words

    for direction in directions:

        for y in range(len(m)):          # number of rows (size of outer tuple)
            # word = list()              # todo: can probably be deleted as word is reset at end of row already

            for x in range(len(m[0])):   # number of columns (size of inner tuple)

                if direction == 'down':  # flips so x is rows and y is columns if we are reading down
                    x, y = y, x

                square = matrix[y][x]

                if square != 0:  # Encountered a letter
                    if len(word) == 0:
                        word.append((direction, y, x), )  # If start of a word, start with direction & coordinates
                    word.append(square)  # First letter

                if direction == 'down':  # flips x and y back before we reach the loop tests
                    x, y = y, x

                if square == 0 or x == 10:  # Encountered a blank space
                    if len(word) > 3:  # Then we collected a word and have come to the end of it
                        word_list.append(word)  # Add it to the list of words
                        word = list()  # Reset word

                    word = list()

    return word_list

def extractWord(word: list):
    """
    Strip out the actual word from the combination list object [(direction, row, col), n1, n2, n3,...]
    So select index [2] onward

    :param word: list
    :return: list
    """

    return word[2:]

def findMatch(codes: list, rubric: dict, my_dictionary : list):
    """
    Return a list of possible matches for a given partial string. The input (codes) is a list of integers,
    each corresponding to a letter. Only some of the codes are known: these are defined by the input dict dictionary.
    The function will construct a RegEx string and apply it to
    :param codes: list      # The code list
    :param rubric: dict     # The set of known codes and corresponding letters
    :param my_dictionary:   # Master word list to search
    :return: list           # The set of matches based on the pattern
    """
    # Build the ReEx string
    r = '^'                 # Regex for start of string
    anyclue = False         # Indicates whether we know any letters yet

    for code in codes:      # Each code number in the codes list
        letter = rubric.get(code)       # Return any matches from the rubric dictionary (if we know the code)
        if letter != None:
            r += letter
            anyclue = True
        else:
            r += '.'        # Regex for any single character

    r += "$"                # Regex for end of string

    if anyclue == True:
        return list(filter(lambda x : re.match(r, x) != None, my_dictionary))


def candidatesNumOptions(candidates):
    return len(candidates) - 1


def createPotentialLetterList(startingList, word, codes):
    newList = startingList
    i = 0;
    for code in codes:
        newList[code] = word[i]
        i = i + 1
    return newList


def createNewWClist(startingWClist, rubric, depth):
    newWClist = list()
    for word_candidates in startingWClist:
        newWC = findMatch(word_candidates[0][1:], rubric, word_candidates[1:])
        if newWC != None:
            newWC.insert(0, word_candidates[0])
        else:
            newWC = list()
        newWClist.append(newWC)
    return newWClist


if __name__ == "__main__":

    matrix = setPuzzle()

    word_list = parse(matrix)

    rubric = {22 : 'o', 10 : 'r', 3 : 'p'}      # Note to add to a dictionary, use rubric[n] = 'x'

    # Show starting position
    showPuzzle(matrix, rubric)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + "/ukenglish.txt", "r", encoding="latin-1") as myfile:
        my_dictionary = myfile.read().splitlines()

    # breakpoint()

    # For each word in word_list, generate a list of all possible matches, based on the letters we know so far
    # What's the best way to store them?

    all_word_candidates = list()

    for word in word_list:
        word_candidates = findMatch(word[1:], rubric, my_dictionary)
        if word_candidates != None:
            word_candidates.insert(0,word) # Changed so that the code sequence remains associated with the potential answers
            all_word_candidates.append(word_candidates)

    # print(*candidates)

    # breakpoint()
    # print("=== First list ===")
    # for word_candidates in all_word_candidates:
    #     print("Word %s has %s possible solutions" % (word_candidates[0], "{:,}".format(len(word_candidates) - 1)))

    # order by number of possible solutions
    all_word_candidates.sort(key=candidatesNumOptions)
    print("=== Ordered list ===")
    showAwcList(all_word_candidates)
    

    # And now try some solutions starting with the word with the least possiblities ...
    # This is fundamentally the wrong way, but it will get us going. It should really be a
    # recursive function.
    letterListToDate = rubric

    # how deep into the word list (ie how far into all_word_candidates have we fixed
    # (potentially) a candidate word
    depth = 0
    for word_candidates in all_word_candidates:
        depth = depth + 1
        for candidate in word_candidates[1:]:
            print("\nTrying %s for word %s\nGives:" % (candidate, word_candidates[0]))
            potentialLetterList = createPotentialLetterList(letterListToDate, candidate, word_candidates[0][1:])

            # Now, that list should be applied to all the words (one at a time) that are after this one.
            # If any of them give a zero option, it has failed. If one of them gives one option, it has
            # succeeded. If neither, either try antoher top level option, or go down to the next word.

            # Create a fresh word_list using the new potential letters
            all_wc_test = createNewWClist(all_word_candidates, potentialLetterList, depth)
            showAwcList(all_wc_test)
            failed = False
            soloOption = False
            for wc in all_wc_test[depth:]:
                numCandidatesHere = len(wc[1:])
                if numCandidatesHere == 0:
                    print("That's a fail - at least one zero option results")
                    failed = True
                    break
                elif numCandidatesHere == 1:
                    print("This has a one option outcome, and so should positively be recursed into (but that's not coded yet")
                    soloOption = True
                    # don't break out of loop - failed trumps soloOption (I think, but they should never happen together. hmmm)
                          
            print("No code to do cleverer stuff, so just trying the next option for this level.")

        # Complete hack to stop it after trying all the options for the first word at the moment.
        if depth == 1:
            exit()
            


