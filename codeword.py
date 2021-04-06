#!/usr/bin/python3
# codeword.py
# Solve the the codeword puzzle
#
#
# John Clarke, john@johnclarke.net
# V0.1 2021-03-30

import re, os

# Set the puzzle, at present a hand encoded version of a sample puzzle.
# Ideally this will somehow aut import a puzzled from a puzzle source and encode it.


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

# ============ Put stuff on the screen ==========
# 
# A couple of functions to output the state of play.

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
        print("Word %s has %s possible solutions" % (word_candidates[0], "{:,}".format(candidatesNumOptions(word_candidates))))
 

# =============== Extract words ===============

# Horizontal words: Have a word list. This will be a list of lists. First two elements
# are the position of the first letter.
# For each row, start at [0] and test if non-zero.
# If it's non-zero, test whether next element is non-zero. If it is, this is becoming a word.
# Add the first two letters to a tentative word, then progress until we hit a zero. Add
# the word to the word list - also need to store the location of the word (or at least of
# the first letter).

def parse(m: tuple):
    """
    Parse the puzzle matrix both across and down to find words to solve.
    Return results as a list of lists. Each inner list represents one word and is structured:
    [(direction, row, col), n1, n2, n3,...] where n1... is the code for the letter

    NOTE: Currently assumes a square grid, and a size of 11x11.

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
                        # Neil: I have put x and y the way I think they should go, but why were they the other way round?
                        # They are now correct for accross rather than down, now I think about it.
                        word.append((direction, x, y), )  # If start of a word, start with direction & coordinates
                    word.append(square)  # First letter

                if square == 0 or x == 10:  # Encountered a blank space
                    if len(word) > 3:  # Then we collected a word and have come to the end of it
                        word_list.append(word)  # Add it to the list of words
                        word = list()  # Reset word

                    word = list()

                if direction == 'down':  # flips x and y back before we reach the loop tests
                    x, y = y, x
    return word_list


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
    # Build the regex string
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

# ======== A few access fucntions giving easy access tot he infromation stored
#
# in the list for an answer/word

def candidatesNumOptions(candidates):
    """
    Given the candidtaes list for a particular answer, return the number
    of words listed as fitting.
    """
    return len(candidates) - 1

def candidatesCodeNumberList(candidates):
    """
    Give the list of code numbers for the answer that these candidates point to
    """
    return candidates[0][1:]


# ======= More hard core stuff ========

def createPotentialLetterList(startingList, word, codes):
    """
    Give a starting number to letter list (startingList) a word (word)
    and the letters codes (cdoes) for ech letter of that word create a new
    number to letter list.
    Assumes that word and codeas are of the same length and that if there
    are duplicate numbers / letters they match,
    """
    newList = startingList.copy()
    i = 0;
    for code in codes:
        newList[code] = word[i]
        i = i + 1
    return newList

# depth is the depth to which words have been fixed in this allWClist
def createNewWCsortedList(startingAllWClist, letterToNumberList, depth, wordForThisDepth):
    """
    Given the currently being explores WC list andan updated number to letter
    list, remove all the words which no longer word from the candidates lists
    and put the resutls in a fresh WC list, sorted so that layer up to depth
    retain their current order (they should be 1 by definition, and should keep
    recursion order), lower ayer reordered to have lowest number of options first.
    """

    # NOTE: we probably don't need to redo the previously done levels here ...
    
    newWClist      = list()
    newWClistBelow = list()
    myDepth = 0;
    for wc in startingAllWClist:

        # If we've alreday got this one down to one option, simply copy
        # it trhough to the new list of create and append the one that is being
        # fixed to one answer
        if myDepth < depth :
            newWClist.append(wc.copy())
        elif myDepth == depth:
            newWClist.append([wc[0], wordForThisDepth])
        else :
            # Create trimmed list for this word/answer given the new code letter
            # list
            newWC = findMatch(candidatesCodeNumberList(wc), letterToNumberList, wc[1:])
            if newWC == None:
                newWC = list()
            newWC.insert(0, wc[0])
            newWClistBelow.append(newWC)

        myDepth = myDepth + 1

    # Sort the below list
    newWClistBelow.sort(key=candidatesNumOptions)
    newWClist.extend(newWClistBelow)

    return newWClist

# Actually do the exhaustive search
# 
# depth: the first call will have this at 0 meaning that the start
#        all_word_candidates list has beed created and sorted but no
#        examinstaion of it has been done
# letterList: the letter list currently being used / evaluated.
# all_wc: the collection of word clues and current options being explored.
#
# return three pieces of information:
# On Failure (False, None, None)
# On success (True, solved list of Word candidates (ie one ancswer each), number fo letter list)
def recurseThroughAllCandidates(all_wc, letterList, depth):
    print("===== Ordered list incoming at depth %d =====" % depth)
    showAwcList(all_wc)
    
    # Try all the words this answer might be for the current scenario
    this_depth_wc = all_wc[depth]
    for candidate in this_depth_wc[1:]:
        print("\nTrying %s for word %s at depth %d" % (candidate, this_depth_wc[0], depth))
        potentialLetterList = createPotentialLetterList(letterList, candidate, candidatesCodeNumberList(this_depth_wc))

        # Now, that letter list is be applied to all the words (one at a time) that
        # are after this one. If any of them then gives a zero option, it means that
        # this substitutaion has failed. If it hasn't succeeded, keep digging deeper.
        
        # In principle, if one of them gives one option, it means we have a definite
        # part of the answer. But we still have to flesh it out, and by having the
        # candidates in order of number of solutions, we must then explore a single
        # option layer next, which is what you should do.

        # If not, create a fresh word_list using the new potential letters
        all_wc_test = createNewWCsortedList(all_wc, potentialLetterList, depth, candidate)

        # If the word we've just put in is actually the word for the final
        # one to be solved, we have succeeded
        if depth == len(all_wc) - 1:
            print("Got to the last word in the puzzle with no failures")
            print(potentialLetterList)
            return True, all_wc_test, potentialLetterList


        # Otherwise Look at the subsequent layers (word candidates) and find one that doesn't fail.
        success = True
        for wc in all_wc_test[depth + 1:]:
            numCandidatesHere = candidatesNumOptions(wc)
            if numCandidatesHere == 0:
                print("That's a fail - at least one zero option results")
                success = False
                break

        if success == True:
            # We can recurse, but the number of options will have changed,
            # So we need to resort and recurse
            print("Going deeper")
            result = recurseThroughAllCandidates(all_wc_test, potentialLetterList, depth + 1)
            success = result[0]

            if success == True:
                print("Passing success back up the line")
                return result

    # If we're still looking, we've failed and need to go back up a level and try again.
    print("All options at depth %d failed, going back up a step" % depth)
    return False, None, None


if __name__ == "__main__":

    matrix = setPuzzle()

    word_list = parse(matrix)

    rubric = {22 : 'o', 10 : 'r', 3 : 'p'}      # Note to add to a dictionary, use rubric[n] = 'x'

    # Show starting position
    showPuzzle(matrix, rubric)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + "/ukenglish.txt", "r", encoding="latin-1") as myfile:
        my_dictionary = myfile.read().splitlines()

    # For each word in word_list, generate a list of all possible matches, based on the letters we know so far
    # What's the best way to store them?
    all_word_candidates = list()

    for word in word_list:
        word_candidates = findMatch(word[1:], rubric, my_dictionary)
        if word_candidates != None:
            word_candidates.insert(0,word) # Changed so that the code sequence remains associated with the potential answers
            all_word_candidates.append(word_candidates)

    print("%d words to solve found in the gride. %d appear to have macthes in the dictionary!!" % (len(word_list), len(all_word_candidates)))
    exit()

    # print(*candidates)

    # breakpoint()
    # print("=== First list ===")
    # for word_candidates in all_word_candidates:
    #     print("Word %s has %s possible solutions" % (word_candidates[0], "{:,}".format(len(word_candidates) - 1)))

    # order by number of possible solutions
    all_word_candidates.sort(key=candidatesNumOptions)

    # And recurse to a soltuion
    result = recurseThroughAllCandidates(all_word_candidates, rubric, 0)

    if (result[0] == False) :
        print("FAILED TO SOLVE PUZZLE")
    else :
        print("RESULT:")
        showPuzzle(matrix, result[2])
