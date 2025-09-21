def DoOperations(a, b):
	return a + b

def DoFunction(func1, a, b):
	return func1(a,b)
	
operation_delegate = DoOperations
print(operation_delegate(2,5))
print(DoFunction(operation_delegate, 2, 9))

