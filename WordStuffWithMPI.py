#Some sort of project thing
#Proposal: 1) whats the project, 2) use case, 3) test data, 4) timelines

#Group project topics:

# 1: word count 
#     load a large txt file(1,000,000): example “Free eBooks | Project Gutenberg”
#     report word frequent analysis in a txt file 
#     report the word-count time using multiple threads from 1 – 8

# HLD: explains the architecture that would be used to develop a system

# HLD for the group project in this class:

# proposal, 
# -- what’s the project? 
# – use cases,
# -- test data
# -- timelines

import os
import threading
import time
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
worker = comm.Get_rank()

def stripWord(word):
    for i in range(len(word) - 1, -1, -1):
        if (word[i] < 'a' or word[i] > 'z'):
            word = word.replace(word[i], "", 1)
    return word

def countWords(title, result, seconds, dict):
    start = time.time()
    wordCount = 0
    f = open(title, 'r')
    for lines in f.readlines():
        line = lines.split()
        # print(len(line), line)
        wordCount += len(line)
        for word in line:
            word = word.lower()
            word = stripWord(word)
            if(word in dict):
                dict[word] = dict.get(word) + 1
            else:
                dict[word] = 1


    # print("Total found in ", title, ": ", wordCount, end="\n")
    result.append(wordCount)
    finalTime = time.time() - start
    seconds.append(finalTime)
    print(f"{title} took {finalTime} ms")


# f = open("LesMiserablesbyVictorHugo", 'r') #open a readable file

Num_Of_Threads = worker + 1 #cant have zero threads
title = "LesMiserablesbyVictorHugo.txt"
title_list = []
text = title.split('.')

print("Creating titles")
for i in range(Num_Of_Threads):
    newTitle = text[0] + "_" + str(worker + 1) + "_" +  str(i) +  "." + text[1] #change title to include associated worker (title_worker#_thread)
    print(newTitle)
    title_list.append(newTitle)

print("Setup") #get total words from original text, and the number of files to split the words into
f = open(title, 'r')
wordCount = 0
lines = f.readlines()
w = [] 
SIZE = int(len(lines))
split = (int(SIZE / Num_Of_Threads)) + 1 #better to go over then under as going under can potentially cut out lines of text
# print(f"Total: {SIZE}, split: {split}")

print("Splitting the text")
for i in range(Num_Of_Threads):
    print(f"Writing to file: {title_list[i]}")
    w = open(title_list[i], 'w')
    start = i * split
    end = start + split
    if end > SIZE: end = SIZE
    # print(f"Start: {start}, End: {end}")
    for line in lines[start:end]:
        # print(line, end="")
        w.write(line)
    w.close() #close document so it can be read properly

print("Creating threads, results, and seconds")
threads = []
result = []
seconds = []
dict = {}
startTime = time.time() #start time to do all threads

print("Starting to count")
for i in range(Num_Of_Threads):
    # print("Counting in ", title_list[i])
    threads.append(threading.Thread(target=countWords, args=(title_list[i], result, seconds, dict, )))
    threads[i].start()

for i in range(Num_Of_Threads):
    threads[i].join()
    # print(f"End thread[{i}] in {seconds[i]} seconds")
    wordCount += result[i]

finalTime = time.time() - startTime
data = comm.gather(finalTime, root = 0)

# print("Total words: ", wordCount)

#deleting flies
for i in title_list:
    os.remove(i)

# sortedList = sorted([(values, keys) for (keys, values) in dict.items()], reverse=True)

# for i in sortedList:
#     print(i[0], i[1])

# for i in dict:
#     print(i, dict[i])

if worker == 0:
    for i in range(len(data)):
        print(f"Worker {i} took {data[i]} ms")