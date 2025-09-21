def SumAndMultiplicate(num1, num2, multiplier):
    def sum():
        return num1 + num2
    def multiplication(s):
        return s * multiplier
    
    sumResult = sum()
    mult = multiplication(sumResult)
    return mult

def GreetPerson(surname, name="default"):
	print(f"Greetings, {surname} {name}")

print(SumAndMultiplicate(5,7,2))
GreetPerson(surname="Torvald")