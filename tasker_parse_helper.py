#!/usr/bin/env python
import math

def main():
    with open('plants.csv', encoding='utf-8') as file:
        lines = file.readlines()
    labels = [l for l in lines[0].strip().split(',')[1:] if l != '']
    names: list[str] = []
    offset: list[int] = []
    nums: list[list[int]] = []

    for i, label in enumerate(labels):
        splitlabel = label.split(' ')
        if splitlabel[-1].isdigit():
            name = ' '.join(splitlabel[:-1])
            num = int(splitlabel[-1])
        else:
            name = label
            num = 1
        if name not in names:
            names.append(name)
            offset.append(i)
            nums.append([])
        nums[-1].append(num)


    maxvals: list[int] = [0]*len(labels)
    minvals: list[int] = [-1]*len(labels)

    for line in lines[1:]:
        for i, value in enumerate(line.strip().split(',')[1:]):
            if value == '':
                continue
            intval = int(value)
            if intval > maxvals[i]:
                maxvals[i] = intval
            if minvals[i] == -1 or intval < minvals[i]:
                minvals[i] = intval

    with open('output.csv', 'w', encoding='utf-8') as file:
        file.write(','.join(labels)+'\n')
        for data in (offset,maxvals, minvals, *nums):
            file.write(','.join(map(str, data))+'\n')

if __name__ == '__main__':
    main()
