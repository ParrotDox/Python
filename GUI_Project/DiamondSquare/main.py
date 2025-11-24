import random

class vertex:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        if isinstance(other, vertex):
            return vertex(self.x + other.x, self.y + other.y, self.z + other.z)
        if isinstance(other, (int, float)):
            return vertex(self.x + other, self.y + other, self.z + other)

    def __sub__(self, other):
        if isinstance(other, vertex):
            return vertex(self.x - other.x, self.y - other.y, self.z - other.z)
        if isinstance(other, (int, float)):
            return vertex(self.x - other, self.y - other, self.z - other)

    def __truediv__(self, other):
        if isinstance(other, vertex):
            return vertex(self.x / other.x, self.y / other.y, self.z / other.z)
        if isinstance(other, (int, float)):
            return vertex(self.x / other, self.y / other, self.z / other)

    def setXYZ(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class chunk:
    def __init__(self, chunk_sample):
        self.data = chunk_sample

def diamondSquare(chunk: chunk, roughness):

    data = chunk.data
    n = len(data)

    # RECURSION STOP — smallest valid size is 3×3
    if n <= 3:
        processChunk(chunk, roughness)
        return

    center = n // 2

    # SPLIT into 4 sub-chunks
    lu = chunk([row[:center+1] for row in data[:center+1]])
    ru = chunk([row[center:]  for row in data[:center+1]])
    ld = chunk([row[:center+1] for row in data[center:]])
    rd = chunk([row[center:]  for row in data[center:]])

    # RECURSION
    diamondSquare(lu, roughness)
    diamondSquare(ru, roughness)
    diamondSquare(ld, roughness)
    diamondSquare(rd, roughness)

    # PROCESS THIS LEVEL
    processChunk(chunk, roughness)

def processChunk(chunk: chunk, roughness):

    data = chunk.data
    n = len(data)
    center = n // 2

    # corners
    A = data[0][0]
    B = data[0][n - 1]
    C = data[n - 1][n - 1]
    D = data[n - 1][0]

    # square center
    center_v = data[center][center]
    length = (B - A).x

    center_v.setXYZ(*applyDiamond([A, B, C, D], length, roughness))

    # diamond — edge midpoints
    M = data[0][center]
    M.setXYZ(*applyDiamond([A, center_v, B], length, roughness))

    N = data[center][n - 1]
    N.setXYZ(*applyDiamond([B, center_v, C], length, roughness))

    P = data[n - 1][center]
    P.setXYZ(*applyDiamond([C, center_v, D], length, roughness))

    Q = data[center][0]
    Q.setXYZ(*applyDiamond([A, center_v, D], length, roughness))

def applyDiamond(vertices, length, roughness):
    avg = vertex(0,0,0)
    for v in vertices:
        avg += v
    avg = avg / len(vertices)

    rnd = random.uniform(-length * roughness, length * roughness)

    return avg.x, avg.y, avg.z + rnd
