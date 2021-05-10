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

    rubric = {22 : 'o', 10 : 'r', 3 : 'p'}      # Note to add to a dictionary, use rubric[n] = 'x'
    # Use this verions if you want to make it hunt harder.
#    rubric = {}      # Note to add to a dictionary, use rubric[n] = 'x'

    return matrix, rubric




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
               "----" if numOpts <= 0 else wts.candidateWordsList[0]))
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

    # finds the matches for this wordInCode, from within the supplied list, or it's own if none provided
    # it then updteas its list to the new collection of candidate words.
    # KNOWN ISSUE: The inital lists above have not culled candidate words which allocate the same letter
    #              to different numbers. I cannot see how to do this, iwith my kowledge of regex.
    def updateCandidateList(self, rubric, newCandidateWordsList=None, verbose=False):
        if newCandidateWordsList == None:
            newCandidateWordsList = self.candidateWordsList
        if newCandidateWordsList == None:
            print("WordToSolve.updateMatched FAIL - no wordlist to select word from")
            return

        # build the match for letters which are not known - they can be any letter
        # except an already used one. The brackets make it a capture group, so
        # so repeats can be used to reduce further search space.
        if len(rubric) == 0 :
            unknown_r = 'A-Za-z'
        else :
            unknown_r = '^'
            for letter in rubric.values() :
                unknown_r += letter

        # Keep a track of the unkonwns already seen
        seen_unknowns = list()
    
        # Build the regex string
        r = '^'                 # Regex for start of string
        anyclue = False         # Indicates whether we know any letters yet

        for code in self.wordInCode:      # Each code number in the codes list
            letter = rubric.get(code)       # Return any matches from the rubric dictionary (if we know the code)
            if letter != None:
                r += letter
                anyclue = True
            else:
                if seen_unknowns.count(code) == 0 :
                    # Haven't seen this number yet, so it is unknown, and won't
                    # have previously been macthed
                    r += '([' + unknown_r + '])'
                    seen_unknowns.append(code)
                else :
                    # This unknown is the same as a previous unkown, so match to
                    # whatever that macthed to.
                    r += "\\{}".format(seen_unknowns.index(code)+1)

        r += "$"                # Regex for end of string

        if verbose:
            print("r for", self.wordInCode, " is ", r)

        self.setCandidateWordsList(list(filter(lambda x : re.match(r, x) != None, newCandidateWordsList)))



"""
This is the class for solving a collection of number to letter words with a dcitionary,
and a starting rubric (if any). It is the engine used by the codeword puzzle solver, but
it can serve for other problems of a similar type.
"""
        
class XwordToSolve:
    def __init__(self, starting_rubric: dict):
        if starting_rubric == None:
            self.starting_rubric = dict()
        else:
            self.starting_rubric = starting_rubric.copy

        self.verbose = True
        self.veryVerbose = True

    def setWordsToSolve(self, start_wts_list):
        self.start_wts_list = start_wts_list.copy()

    def setBaseDictionary(self, base_dictionary):
        self.base_dictionary = base_dictionary

    class Solution:
        # Used for storing a solution ...
        def __init__ (self, solvedWordList, solvedRubric):
            self.solvedWordList = solvedWordList.copy()
            self.solvedRubric = solvedRubric.copy()


    def showRubric(self, rubric=None):
        if rubric == None :
            rubric = self.starting_rubric

        print("+--"*13,end="+\n")
        for j in [0,13] :
            print(end="|")
            for i in range(1,14) :
                print(f"{j+i:2d}", end="|")
            print()
            print(end="|")
            for i in range(1,14) :
                letter = rubric.get(j+i)
                if letter == None:
                    letter = '  '
                else:
                    letter = ' '+letter.capitalize()
                print(letter,end="|")
            print()
            print("+--"*13,end="+\n")

    def solve(self, multipleResults=False):
        self.multipleResults = multipleResults
        if self.verbose:
            print ("Initial list of words to solve, will have no solutions yet")
            WordToSolve.showList(self.start_wts_list)

        start1 = time.time()
        
        # For each word in word_list, generate a list of all possible matches, based on the letters we know so far
        dictionary_by_word_length = dict()

        # Create the initial list of allowed words for each word if it hasn't been given.
        for wts in self.start_wts_list:
            if wts.candidateWordsList == None:
                dictionary_subset = dictionary_by_word_length.get(wts.length)
                if dictionary_subset == None :
                    r = "^" + "."*wts.length + "$"
                    dictionary_subset = list(filter(lambda x : re.match(r, x) != None, my_dictionary))
                    dictionary_by_word_length[wts.length] = dictionary_subset
                wts.updateCandidateList(rubric, dictionary_subset, self.veryVerbose)
                if wts.numberOfCandidates() == 0 :
                    print("One of the words has no options at all before even starting. Stopping now.")
                    exit()

        # order by number of possible solutions
        self.start_wts_list.sort(key=WordToSolve.numberOfCandidates)

        start2 = end1 = time.time()

        # And recurse to a soltuion
        result = list()
        self.recurseThroughAllCandidates(self.start_wts_list, rubric, 0, result)

        end2 = time.time()

        if self.veryVerbose :
            print("Parsing and getting first long list of word options: ", end1 - start1)
            print("Rescursion / solving: ", end2 - start2)

        return result

    # Actually do the exhaustive search
    # 
    # depth: the first call will have this at 0 meaning that the start
    #        all_word_candidates list has beed created and sorted but no
    #        examinataion of it has been done
    # letterList: the letter list currently being used / evaluated.
    # all_wc: the collection of word clues and current options being explored.
    #
    # returns:
    # On failure False ; resultList will be an empty list
    # On success True  ; resultList will be a list of XwordToSolve.Solution with the solutions in
    def recurseThroughAllCandidates(self,
                                    wordToSolveList,
                                    letterList,
                                    depth,
                                    resultList):
        if self.verbose:
            print("===== Ordered list incoming at depth %d =====" % depth)
            WordToSolve.showList(wordToSolveList)
    
        # Try all the words this answer might be for the current scenario
        wordToSolve = wordToSolveList[depth]
        haveFoundSomething = False;
        for candidate in wordToSolve.candidateWordsList:
            if self.verbose:
                print("\nTrying %s for word %s at depth %d" % (candidate, wordToSolve.string(), depth))

            potentialLetterList = self.createPotentialLetterList(letterList, candidate, wordToSolve.wordInCode)

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
            wts_list_test = self.createNewWCsortedList(wordToSolveList, potentialLetterList, depth, candidate)


            # If the word we've just put in is actually the word for the final
            # one to be solved, we have succeeded (but we did have to put it in, hence this
            # is after the line above.)
            if depth == len(wts_list_test) - 1:
                if self.verbose :
                    print("Got to the last word in the puzzle with no failures = found a solution")
                resultList.append(XwordToSolve.Solution(wts_list_test, potentialLetterList))
                if self.multipleResults == False :
                    return True
                haveFoundSomething = True

            # Otherwise Look at the subsequent layers (word candidates) and
            # find one that doesn't fail.
            else :
                exploreMore = True
                for wts in wts_list_test[depth + 1:]:
                    numCandidatesHere = wts.numberOfCandidates()
                    if numCandidatesHere == 0:
                        if self.verbose :
                            print("That's a branch with no solutions on it")
                        exploreMore = False
                        break

                if exploreMore == True:
                    # All the lower levels have at least one option, so let's explore them
                    haveFoundSomething = self.recurseThroughAllCandidates(wts_list_test,
                                                               potentialLetterList,
                                                               depth + 1,
                                                               resultList)
                    if haveFoundSomething == True and self.multipleResults == False:
                        return True

        # If we get here, we've failed to find a valid word for this level
        # and so we need to go back up a level and try again.
        if self.verbose :
            print("Depth %d completed one way or another, going back up a step" % depth)
        return haveFoundSomething

    def createPotentialLetterList(self, startingList, word, codes):
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
    def createNewWCsortedList(self, startingWordToSolveList, letterToNumberList, depth, wordForThisDepth):
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
                copyWTS.updateCandidateList(letterToNumberList)
                newWTSlistBelow.append(copyWTS)

            myDepth = myDepth + 1

        # Sort the below list and then append all of its entries to the result
        newWTSlistBelow.sort(key=WordToSolve.numberOfCandidates)
        newWTSlist.extend(newWTSlistBelow)

        return newWTSlist



class CodewordToSolve:
    def __init__(self, starting_grid: tuple, starting_rubric: dict, base_dictionary: dict):
        self.starting_grid = starting_grid
        self.starting_rubric = starting_rubric.copy()
        self.base_dictionary = base_dictionary

        self.xwts = XwordToSolve(rubric)

        self.verbose = True
        self.multipleResults = False

    def assumeManySolutions(self):
        self.multipleResults = True

    def showGrid(self, grid=None, knownLetters=None):
        if grid == None:
            grid = self.starting_grid
        if knownLetters == None:
            knownLetters = self.starting_rubric
        
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
    

    def showRubric(self, rubric):
        self.xwts.showRubric(rubric)

    
    def solve(self):
        if self.verbose == True :
            print("Starting grid.")
            self.showGrid()
        # Step one, parse the grid using the rubric, into a list of words to solve
        self.wts_list = self.parse()
        self.xwts.setWordsToSolve(self.wts_list)
        self.xwts.setBaseDictionary(self.base_dictionary)
        return self.xwts.solve(self.multipleResults)
        

    # =============== Extract words ===============
    # Horizontal words: Have a word list. This will be a list of lists. First two elements
    # are the position of the first letter.
    # For each row, start at [0] and test if non-zero.
    # If it's non-zero, test whether next element is non-zero. If it is, this is becoming a word.
    # Add the first two letters to a tentative word, then progress until we hit a zero. Add
    # the word to the word list - also need to store the location of the word (or at least of
    # the first letter).
    def parse(self, m: tuple = None):
        if m == None:
            m = self.starting_grid
            
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

        # There is probably a way of doing this in three nestled loops and handling
        # non-square unknown size grids. But I can;t work it out. So we have two loops.
        # It still assumes a rectangle.
        xLast = len(m[0]) - 1
        direction = 'across'
        for y in range(len(m)):          # number of rows (size of outer tuple)
            for x in range(len(m[y])):   # number of columns (size of inner tuple)
                square = m[y][x]

                if square != 0:  # Encountered a letter
                    if len(word) == 0:
                        startX = x
                        startY = y
                    word.append(square)  # First letter

                if square == 0 or x == xLast:  # Encountered a blank space or end of row
                    if len(word) > 3:  # Then we collected a word and have come to the end of it
                        wordToSolveList.append(WordToSolve(startX, startY, direction, word))

                    word = list() # Reset word (either it wasn't a word, or it has been noted)


        direction = 'down' # So now go through them the other way round running down.
        yLast = len(m) - 1
        for x in range(len(m[0])):    
            for y in range(len(m)):
                square = m[y][x]

                if square != 0:  # Encountered a letter
                    if len(word) == 0:
                        startX = x
                        startY = y
                    word.append(square)  # First letter

                if square == 0 or y == yLast:  # Encountered a blank space or end of column
                    if len(word) > 3:  # Then we collected a word and have come to the end of it
                        wordToSolveList.append(WordToSolve(startX, startY, direction, word))

                    word = list() # Reset word (either it wasn't a word, or it has been noted)


        return wordToSolveList


   




if __name__ == "__main__":

    # Get the thing you need to solve it: the puzzle and the dictionary
    matrix, rubric = setPuzzle()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/ukenglish.txt", "r", encoding="latin-1") as myfile:
        my_dictionary = myfile.read().splitlines()


    # Set up the class and solve
    cwts = CodewordToSolve(matrix, rubric, my_dictionary)
    cwts.assumeManySolutions()
    results = cwts.solve()

    # Output results
    if (len(results) == 0) :
        print("FAILED TO SOLVE PUZZLE")
    else :
        print("Solutions found: %d" % len(results))
        for r in results:
            print("RESULT:")
            cwts.showGrid(matrix, r.solvedRubric)
            #and a sorted version of the number to letter result:
            cwts.showRubric(r.solvedRubric)

