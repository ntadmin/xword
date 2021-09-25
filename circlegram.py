#!/usr/bin/python3
# codeword.py
# Solve the the codeword puzzle
#
#
# John Clarke, john@johnclarke.net
# V0.1 2021-03-30

import re, os, time

# This problem has three collections of letters:
# each pair of collection share one ketter, and all theee share one.
# common shared letter is unknown and the challenge is to find that letter such that
# all three sets of letters can form a word.
# those three works share a common theme.

# Set a puzzle up
def setPuzzle():
    puzzle  = tuple()
    puzzle += (('r', 'e', 'u', 'h', 'p', 'b'),)
    puzzle += (('b', 'g', 'm', 'a', 'r', 'e'),)
    puzzle += (('e', 'i', 't', 's', 'w', 'r'),)
    
    return puzzle


class CircleGramToSolve:
    def __init__(self, starting_puzzle: tuple, base_dictionary: dict):
        self.starting_puzzle = starting_grid
        self.base_dictionary = base_dictionary

        self.verbose = True
        
    class Result:
        def __init__(self, solution_letter, three_words):
            self.soltuion_letter = solution_letter
            self.three_words = three_words
        
        def show():
            print("Common Letter: "+self.solution_letter)
            print("Three words: "+self.three_words
            
     def showResult(r: result):
         CircleGramToSolve.Result.show(r)
         
     def solve():
         results = list()
         
         # There are 26 possibilities for the unknown letter, just go through them and
         # get anagram lists for each of the three letter combinations. If any combination
         # yields zero words, then this solution letter is invalid. If the letter yields
         # words for each of the three, create a potential result for each combination of
         # words (with the shared letter)
         
         
         # Now cull those where the words don't have a common theme.
         
         return results

if __name__ == "__main__":

    # Get the thing you need to solve it: the puzzle and the dictionary
    puzze = setPuzzle()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/ukenglish.txt", "r", encoding="latin-1") as myfile:
        my_dictionary = myfile.read().splitlines()


    # Set up the class and solve
    cgts = CircleGram(puzzle, my_dictionary)
    results = cgts.solve()

    # Output results
    if (len(results) == 0) :
        print("FAILED TO SOLVE PUZZLE")
    else :
        print("Solutions found: %d" % len(results))
        for r in results:
            print("RESULT:")
            cgts.showResult(r)
