ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LENGTH = len(ALPHABET)

#Rotor consists of static and moving parts
class Rotor:
    def __init__(self, wheel: str, key: str):
        self.wheel = wheel
        self.key = key
        self.position = wheel.find(key)

    #Rotate wheel and return true if full cycle is done
    def Rotate(self):
        self.position = (self.position + 1) % LENGTH
        if (self.position == 0):
            return True
        else:
            False
    
    def ConvertSymbol(self, symbol: str, reverse: bool):
        rotatedWheel = self.wheel[(-1) * self.position:] + self.wheel[:(-1) * self.position]
        if (reverse == False):
            symbolIndex = ALPHABET.find(symbol)
            return rotatedWheel[symbolIndex]
        else:
            symbolIndex = rotatedWheel.find(symbol)
            return ALPHABET[symbolIndex]

#Mirror to encode and decode symbols
class Mirror:
    def __init__(self, encodedAlphabet):
        self.encodedAlphabet = encodedAlphabet
    def MirrorSymbol(self, symbol):
        return self.encodedAlphabet[ALPHABET.find(symbol)]
    
class Enygma:
    def __init__(self, mirror: Mirror, rotors: list[Rotor]):
        self.mirror = mirror
        self.rotors = rotors
    
    #Convert symbol using rotors and mirror
    def EncryptSymbol(self, symbol):
        symbolBuffer = symbol
        for rtr in self.rotors:
            symbolBuffer = rtr.ConvertSymbol(symbolBuffer, False)

        symbolBuffer = self.mirror.MirrorSymbol(symbolBuffer)

        for rtr in self.rotors[::-1]:
            symbolBuffer = rtr.ConvertSymbol(symbolBuffer, True)
        return symbolBuffer
    
    #Rotates wheels of enygma machine
    def RotateWheels(self):
        firstWheelRotation = True
        flag = False
        for rtr in self.rotors:
            if(firstWheelRotation == True):
                flag = rtr.Rotate()
                firstWheelRotation = False
            elif(flag == True):
                flag = rtr.Rotate()
            else:
                break
