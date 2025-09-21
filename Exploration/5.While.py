stars = int(input("How many stars have you got?: "))
score = stars * "X"

ind = 0
while(ind < len(score)):
    if(ind == len(score) - 1):
        print("X")
        ind += 1
        continue
    print("X", end=" ")
    ind += 1
else:
    print("Score has been printed! Awesome job!")

spellWord = "sPell WorD"

for s in spellWord:
    print(s, end=" ")
else:
    print()
    print("Word has been spelled! Wow!")