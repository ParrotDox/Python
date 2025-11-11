import math
class matrixTransformationClass():
    def __init__(self):

        #    X    Y    Z
        self.points = [
            [0,0,3], 
            [1,0,3],   
            [2,0,3],  
            [3,0,3],  
            [3,0,0],  
            [0,0,0],  
            [1,1,3],  
            [2,1,3],
            [0,2,3],
            [3,2,3],
            [3,2,0],
            [0,2,0],
            [2,3,0],
            [2,3,3]
        ]

    @staticmethod
    def useMatrix(points: list[list[float]], matrix: list[list[float]]):
        new_points = []
        for pt in points:
            x, y, z = pt
            x_new = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]*z + matrix[0][3]*1
            y_new = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]*z + matrix[1][3]*1
            z_new = matrix[2][0]*x + matrix[2][1]*y + matrix[2][2]*z + matrix[2][3]*1
            w_new = matrix[3][0]*x + matrix[3][1]*y + matrix[3][2]*z + matrix[3][3]*1
        
            if w_new != 0:
                new_points.append([x_new/w_new, y_new/w_new, z_new/w_new])
            else:
                new_points.append([x_new, y_new, z_new])
        return new_points
    @staticmethod
    def translateXYZ(x, y, z):
        return [
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def scaleXYZ(x, y, z):
        return [
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationX(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationY(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def rotationZ(angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        return [
            [c, s, 0, 0],
            [-s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def orthographicProjection():
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1]
        ]
    @staticmethod
    def cameraZ(Zvalue):
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, -1/Zvalue, 1]
        ]

figure = matrixTransformationClass()
pts_rX = matrixTransformationClass.useMatrix(figure.points, matrixTransformationClass.rotationX(30))
pts_rY = matrixTransformationClass.useMatrix(pts_rX, matrixTransformationClass.rotationY(45))
pts_Cz = matrixTransformationClass.useMatrix(pts_rY, matrixTransformationClass.cameraZ(8))