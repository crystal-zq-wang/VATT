import crepe
import numpy
import csv
import os

lst = list()
filename = 'Recording'
cmd = 'crepe ' + filename + '.wav'
os.system(cmd)


with open (filename+'.f0.csv',newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        lst.append(row[1])

lst = lst[1:]
lst = [float(s) for s in lst]
# print(type(lst[1]))

lst.sort()

length = len(lst)

DELTA = 0.1
assert DELTA < 0.5, "not gonna work bro"

lst = lst[int(length*DELTA):-int(length*DELTA)]
average = sum(lst) / len(lst)
print(average)

    
