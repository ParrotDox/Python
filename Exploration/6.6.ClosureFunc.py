def Container(variable1):
	variable2 = 10
	def ClosureFunc(x):
		return variable1 + variable2 + x
	return ClosureFunc

ClosureLink = Container(15)
print(ClosureLink(50))