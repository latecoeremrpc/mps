def LetterCountI(str):
    greatest = "-1"
    greatestCount = 0;

    def findRepeats(word):
        storage = {}
        rep = 0
        for letter in list(word):
            try:
                storage[letter] = storage[letter] + 1
            except: 
                storage[letter] = 1
        for n in storage:
            if storage[n] > 1:
                rep = rep + storage[n]
        return rep

    arr = str.split()

    for word in arr:
        c = findRepeats(word)
        if c > greatestCount:
            greatest = word
            greatestCount = c

    return greatest


print(LetterCountI("No words"))