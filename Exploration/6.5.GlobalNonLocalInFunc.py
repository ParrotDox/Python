name = "Egor"

def ChangeAndPrintGlobalName(name_param):
	#Объявление, что работаем с глобальной переменной
	global name 
	name = name_param
	print(name)

ChangeAndPrintGlobalName("Bob")
print(name)

def MainFunction():
	n = 5
	def SecondFunction():
		nonlocal n
		n = 25 #Обращаемся к переменной MainFunction
	
	SecondFunction()
	print(n)

MainFunction()
