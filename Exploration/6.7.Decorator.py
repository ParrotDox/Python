def uppercase(func):
    def formatter(*args):
        sentence = func(*args)
        uppercaseSentence = sentence.upper()
        return uppercaseSentence
    return formatter

@uppercase
def GreetPerson(name):
    return f"Greetings, {name}"

print(GreetPerson("egor"))