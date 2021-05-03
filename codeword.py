#!/usr/bin/python3
# codeword.py
# Solve the the codeword puzzle
#
#
# John Clarke, john@johnclarke.net
# V0.1 2021-03-30

import re, os, time

# Set the puzzle, at present a hand encoded version of a sample puzzle.
# Ideally this will somehow aut import a puzzled from a puzzle source and encode it.

# A few of "constants" for use in laying out a puzzle
# If it 
SQ_BLOCK =  0 # A blocked square that never has anything in it.
SQ_UNSET = -1 # Awaiting a letter but with no hint as to what that letter is.
# If it's not one of those, it will be a number between 1 and 26, and it's a codeword

LIST_UNSET = -1

def setPuzzle():
    """
    Returns a tuple of tuples containing the puzzle to be solved
    :return: matrix: tuple
    """
    matrix = tuple()  # This will be a tuple of tuples to hold the original puzzle set

    matrix += ((SQ_BLOCK, 25, SQ_BLOCK, 21, SQ_BLOCK,  4, SQ_BLOCK,  8, SQ_BLOCK, 17, SQ_BLOCK),)
    matrix += ((12,       22, 13,        8, 18,        8, SQ_BLOCK, 18, 2,        13,  8),)
    matrix += ((SQ_BLOCK, 14, SQ_BLOCK, 24, SQ_BLOCK, 21, SQ_BLOCK, 22, SQ_BLOCK, 22, SQ_BLOCK),)
    matrix += ((5,        13, 26,       20, SQ_BLOCK, 16, 20,        9, 13,        7, 13),)
    matrix += ((SQ_BLOCK,  7, SQ_BLOCK,  5, SQ_BLOCK, 20, SQ_BLOCK,  3, SQ_BLOCK, SQ_BLOCK, 9),)
    matrix += ((20,       16, 22, SQ_BLOCK, SQ_BLOCK, SQ_BLOCK, SQ_BLOCK, 0,  21, 17,  3),)
    matrix += ((17, SQ_BLOCK, SQ_BLOCK,  8, SQ_BLOCK, 23, SQ_BLOCK,  1, SQ_BLOCK, 21, SQ_BLOCK),)
    matrix += ((9,        21, 10,       11, 4,        20, SQ_BLOCK, 10, 21,        3, 18),)
    matrix += ((SQ_BLOCK, 18, SQ_BLOCK,  4, SQ_BLOCK,  8, SQ_BLOCK, 13, SQ_BLOCK,  3, SQ_BLOCK),)
    matrix += ((7,        22, 6,        21, SQ_BLOCK, 18, 21,       25, 17,       20, 18),)
    matrix += ((SQ_BLOCK,  9, SQ_BLOCK, 18, SQ_BLOCK, 19, SQ_BLOCK,  8, SQ_BLOCK, 15, SQ_BLOCK),)

    return matrix

# ============ Put stuff on the screen ==========
# 
# A couple of functions to output the state of play.

def showPuzzle(matrix, knownLetters):
    for row in matrix:
        print("+--"*len(row),end="+\n")
        print(end="|")
        for element in row:
            if element == SQ_BLOCK:
                print("XX", end="|")
            else:
                print(f"{element:2d}", end="|")
        print()
        print(end="|")
        for element in row:
            if element == SQ_BLOCK:
                print("XX", end="|")
            else:
                letter = knownLetters.get(element)
                if letter != None:
                    print(letter.capitalize(),end=" |")
                else:
                    print("  ", end="|")
        print()
    print("+--"*len(row),end="+\n")
    

def showLetterCode(letterCode):
    print("+--"*13,end="+\n")
    for j in [0,13] :
        print(end="|")
        for i in range(1,14) :
            print(f"{j+i:2d}", end="|")
        print()
        print(end="|")
        for i in range(1,14) :
            letter = letterCode.get(j+i)
            if letter == None:
                letter = '  '
            else:
                letter = ' '+letter.capitalize()
            print(letter,end="|")
        print()
        print("+--"*13,end="+\n")


class WordToSolve:
    def __init__(self, x, y, direction, wordInCode, candidateWordsList=None):
        # Integers with the start position and direction of the first letter and the word.
        # Different puzzle tpyes can and will use this differently.
        self.posX = x
        self.posY = y
        # A string with the direction of the word.
        # Different puzzlie types can and will use this differently
        self.direction = direction
        # The word as a array of numbers, the numbers which represent a letter, known or unknown.
        self.wordInCode = wordInCode.copy()
        self.length = len(self.wordInCode)
        # The dictionary from which this word must come. If None, use the overall puzzle one
        self.candidateWordsList = None
        self.setCandidateWordsList(candidateWordsList)

    def string(self):
        return "at "+"{:,}".format(self.posX)+", "+"{:,}".format(self.posY)+" "+self.direction+"; "+"["+",".join(str(c) for c in self.wordInCode)+"]"

    def show(self):
        print(self.string())

    def showList(wtsList):
        depth = 0
        for wts in wtsList:
            numOpts = wts.numberCandidateWords
            print("%2d Word %s has %s option%s (first: %s)" %
              (depth,
               wts.string(),
               "{:,}".format(numOpts),
               '' if numOpts == 1 else 's',
               "----" if numOpts == 0 else wts.candidateWordsList[0]))
            depth = depth + 1

    def copy(self):
        return WordToSolve(self.posX, self.posY, self.direction, self.wordInCode, self.candidateWordsList)

    def setCandidateWordsList(self, candidateWordsList):
        if candidateWordsList == None :
            self.candidateWordsList = None
            self.numberCandidateWords = LIST_UNSET
        else :
            self.candidateWordsList = candidateWordsList.copy()
            self.numberCandidateWords = len(self.candidateWordsList)

    def numberOfCandidates(self):
        return self.numberCandidateWords
    


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
    wordToSolveList = list() # Stores the list of words to solve.

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
                        if direction == 'across' :
                            startX = x
                            startY = y
                        else :
                            startX = y
                            startY = x
                    word.append(square)  # First letter

                if square == 0 or x == 10:  # Encountered a blank space
                    if len(word) > 3:  # Then we collected a word and have come to the end of it
                        wordToSolveList.append(WordToSolve(startX, startY, direction, word[1:]))
                        word = list()  # Reset word

                    word = list()

                if direction == 'down':  # flips x and y back before we reach the loop tests
                    x, y = y, x
    return wordToSolveList


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
    # build the match for letters which are not known - they can be any letter
    # except an already used one. The brackets make it a capture group, so
    # so repeats can be used to reduce further search space.
    unknown_r  = '([^'
    for letter in rubric.values() :
        unknown_r += letter
    unknown_r += '])'

    # Keep a track of the unkonwns already seen
    seen_unknowns = list()
    
    # Build the regex string
    r = '^'                 # Regex for start of string
    anyclue = False         # Indicates whether we know any letters yet

    for code in codes:      # Each code number in the codes list
        letter = rubric.get(code)       # Return any matches from the rubric dictionary (if we know the code)
        if letter != None:
            r += letter
            anyclue = True
        else:
            if seen_unknowns.count(code) == 0 :
                # Haven't seen this number yet, so it is unknown, and won't
                # have previously been macthed
                r += unknown_r
                seen_unknowns.append(code)
            else :
                # This unknown is the same as a previous unkown, so match to
                # whatever that macthed to.
                r += "\\{}".format(seen_unknowns.index(code)+1)

    r += "$"                # Regex for end of string

    print("r for", codes, " is ", r)

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

def answerLength(answer):
    """
    Give the length of the answer/word for a word/answer in the puzzle
    """
    return len(answer) - 1

# ======= More hard core stuff ========

def createPotentialLetterList(startingList, word, codes):
    """
    Give a starting number to letter list (startingList) a word (word)
    and the letters codes (codes) for ech letter of that word create a new
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
def createNewWCsortedList(startingWordToSolveList, letterToNumberList, depth, wordForThisDepth):
    """
    Given the currently being explores WC list andan updated number to letter
    list, remove all the words which no longer word from the candidates lists
    and put the resutls in a fresh WC list, sorted so that layer up to depth
    retain their current order (they should be 1 by definition, and should keep
    recursion order), lower ayer reordered to have lowest number of options first.
    """

    # NOTE: we probably don't need to redo the previously done levels here ...
    
    newWTSlist      = list()
    newWTSlistBelow = list()
    myDepth = 0;
    for wts in startingWordToSolveList:

        # If we've alreday got this one down to one option, simply copy
        # it trhough to the new list or create and append the one that is being
        # fixed to one answer
        copyWTS = wts.copy()
        if myDepth < depth :
            newWTSlist.append(copyWTS)
        elif myDepth == depth:
            copyWTS.setCandidateWordsList([wordForThisDepth])
            newWTSlist.append(copyWTS)
        else :
            # Create trimmed list for this word/answer given the new code letter
            # list
            copyWTS.setCandidateWordsList(findMatch(wts.wordInCode, letterToNumberList, wts.candidateWordsList))
            newWTSlistBelow.append(copyWTS)

        myDepth = myDepth + 1

    # Sort the below list and then append all of its entries to the result
    newWTSlistBelow.sort(key=WordToSolve.numberOfCandidates)
    newWTSlist.extend(newWTSlistBelow)

    return newWTSlist

# Actually do the exhaustive search
# 
# depth: the first call will have this at 0 meaning that the start
#        all_word_candidates list has beed created and sorted but no
#        examinataion of it has been done
# letterList: the letter list currently being used / evaluated.
# all_wc: the collection of word clues and current options being explored.
#
# return three pieces of information:
# On Failure (False, None, None)
# On success (True, solved list of Word candidates (ie one ancswer each), number to letter list)
def recurseThroughAllCandidates(wordToSolveList, letterList, depth):
    print("===== Ordered list incoming at depth %d =====" % depth)
    WordToSolve.showList(wordToSolveList)
    
    # Try all the words this answer might be for the current scenario
    wordToSolve = wordToSolveList[depth]
    for candidate in wordToSolve.candidateWordsList:
        print("\nTrying %s for word %s at depth %d" % (candidate, wordToSolve.string(), depth))
        potentialLetterList = createPotentialLetterList(letterList, candidate, wordToSolve.wordInCode)

        # Now, that letter list is be applied to all the words (one at a time) that
        # are after this one. If any of them then gives a zero option, it means that
        # this substitutaion has failed. If it hasn't failed, keep digging deeper.
        
        # You might thinkg that if one of them gives one option, it means we have
        # a definite
        # part of the answer. But that's not the case. It might only have one answer
        # because of a previous but wrong substitution. The sorting means that we will
        # dive down the "single option" levels quickly and see if when we make those
        # substitutions they provide options for lower levles. Or not.

        # Create a fresh wordToSolve list using the new potential letters
        wts_list_test = createNewWCsortedList(wordToSolveList, potentialLetterList, depth, candidate)

        # If the word we've just put in is actually the word for the final
        # one to be solved, we have succeeded (but we did have to put it in, hence this
        # is after the line above.)
        if depth == len(wts_list_test) - 1:
            print("Got to the last word in the puzzle with no failures = SUCCESS")
            return True, wts_list_test, potentialLetterList

        # Otherwise Look at the subsequent layers (word candidates) and
        # find one that doesn't fail.
        success = True
        for wts in wts_list_test[depth + 1:]:
            numCandidatesHere = wts.numberOfCandidates()
            if numCandidatesHere == 0:
                print("That's a fail - at least one zero option results")
                success = False
                break

        if success == True:
            # All the lower levels have at least one option, so let's explore them
            print("Going deeper")
            result = recurseThroughAllCandidates(wts_list_test, potentialLetterList, depth + 1)
            success = result[0]

            if success == True:
                return result

    # If we get here, we've failed to find a valid word for this level
    # and so we need to go back up a level and try again.
    print("All options at depth %d failed, going back up a step" % depth)
    return False, None, None


if __name__ == "__main__":

    matrix = setPuzzle()

    wordToSolveList = parse(matrix)

    for wtc in wordToSolveList:
        wtc.show()

    rubric = {22 : 'o', 10 : 'r', 3 : 'p'}      # Note to add to a dictionary, use rubric[n] = 'x'

    # Show starting position
    showPuzzle(matrix, rubric)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(dir_path + "/ukenglish.txt", "r", encoding="latin-1") as myfile:
        my_dictionary = myfile.read().splitlines()

    start1 = time.time()
    # For each word in word_list, generate a list of all possible matches, based on the letters we know so far

    dictionary_by_word_length = dict()

    # Create the initial list of allowed words for each word if it hasn;t been given.
    # KNOWN ISSUE: The inital lists above have nt culled words which allocate the same letter to different numbers.
    for wts in wordToSolveList:
        if wts.candidateWordsList == None:
            dictionary_subset = dictionary_by_word_length.get(wts.length)
            if dictionary_subset == None :
                r = "^" + "."*wts.length + "$"
                dictionary_subset = list(filter(lambda x : re.match(r, x) != None, my_dictionary))
                dictionary_by_word_length[wts.length] = dictionary_subset
            word_candidates = findMatch(wts.wordInCode, rubric, dictionary_subset)
            if len(word_candidates) == 0 :
                print("One of the words has no options at all before even starting. Stopping now.")
                exit()
            wts.setCandidateWordsList(word_candidates)

    # order by number of possible solutions
    wordToSolveList.sort(key=WordToSolve.numberOfCandidates)

    start2 = end1 = time.time()

    # And recurse to a soltuion
    result = recurseThroughAllCandidates(wordToSolveList, rubric, 0)

    end2 = time.time()

    if (result[0] == False) :
        print("FAILED TO SOLVE PUZZLE")
    else :
        print("RESULT:")
        showPuzzle(matrix, result[2])
        #and a sorted version of the number to letter result:
        showLetterCode(result[2]);
        print("Parsing and getting first long list of word options: ", end1 - start1)
        print("Rescursion / solving: ", end2 - start2)
