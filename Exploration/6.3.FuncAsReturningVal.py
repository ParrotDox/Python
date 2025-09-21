def sum(a,b):
    return a + b
def multiplication(a,b):
    return a * b
def Division(a,b):
    return a/b
def ChooseOption(option):
    if option == 0:
        return sum
    elif option == 1:
        return multiplication
    elif option == 2:
        return Division
    else:
        return None

option = int(input("Input option 0-2: "))
number1 = int(input("Input number1: "))
number2 = int(input("Input number2: "))
func = ChooseOption(option)
print(f"Function {option} | Result is {func(number1, number2)}")