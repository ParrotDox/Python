def choose_operation(option):
	if option == 1:
		return lambda num1, num2: num1 + num2
	elif option == 2:
		return lambda num1, num2: num1 * num2
	else:
		return None

operation = choose_operation(1)
print(operation(5,7))
