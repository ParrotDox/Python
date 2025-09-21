def StarDef(quantity, *, symbol1, symbol2):
    ctr = 0
    while(ctr != quantity):
        if(ctr % 2 == 0):
            print(symbol1, end=" ")
        else:
            print(symbol2, end=" ")
        ctr += 1

def SumNumbers(mas, /, name):
    sum = 0
    for i in range(len(mas)):
        sum += mas[i]
    else:
        print(f"Operation of sum has been done, {name}")
    return sum

def OutputAllParams(name, /, *params):
    print(f"Outputting all params, {name}!")
    for el in params:
        print(el, end=" ")

StarDef(10, symbol1='a',symbol2='1')
print(SumNumbers([2,2,4,5], "Gorvald"))
OutputAllParams("Nova",2,3, "good", 2.4, '1')