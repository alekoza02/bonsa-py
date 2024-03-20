import numpy as np
from functools import cache

class Mate:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def versore(v: np.ndarray[float]) -> np.ndarray[float]:
        ...
        
    @staticmethod
    def modulo(v: np.ndarray[float]) -> float:
        ...
        
    @staticmethod
    def normale(v: np.ndarray[float]) -> np.ndarray[float]:
        ...
        
    @staticmethod
    def normale_tri_buffer(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        ...
    
    @staticmethod
    def centratura(dim):
        return np.array(
            [
                [dim[0]//8,  0,      0,  0],
                [0,     dim[1]//8,   0,  0],
                [0,     0,      1,  0],
                [dim[0]//2,  dim[1]//2,   0,  1]
            ]
        )

    @staticmethod
    def screen_world():
        return np.array([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1]
        ])

    @staticmethod
    def camera_world(camera):
        return np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [-camera.pos[0], -camera.pos[1], -camera.pos[2], 1]]
        ) @ np.array(
            [[camera.rig[0], camera.dir[0], camera.ups[0], 0],
             [camera.rig[1], camera.dir[1], camera.ups[1], 0],
             [camera.rig[2], camera.dir[2], camera.ups[2], 0],
             [0, 0, 0, 1]]
        )

    @staticmethod
    def rotx(ang):
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(ang), np.sin(ang), 0],
            [0, -np.sin(ang), np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def roty(ang):
        return np.array([
            [np.cos(ang), 0, np.sin(ang), 0],
            [0, 1, 0, 0],
            [-np.sin(ang), 0, np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotz(ang):
        return np.array([
            [np.cos(ang), np.sin(ang), 0, 0],
            [-np.sin(ang), np.cos(ang), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def trasl(array):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [array[0], array[1], array[2], 1]
        ])

    @staticmethod
    def frustrum(W,H, h_fov = np.pi / 6):
        # qua c'è un meno per sistemare l'orientamento della camera, altrimenti ottieni un'immagine specchiata in prospettiva
        v_fov = h_fov * H / W
        left = np.tan(h_fov / 2)
        right = -left
        top = np.tan(v_fov / 2)
        bottom = -top
        far = 100
        near = 0.01
        return np.array([
            [-2 / (right - left), 0, 0, 0],
            [0, 2 / (top - bottom), 0, 0],
            [0, 0, (far + near) / (far - near), 1],
            [0, 0, -2 * near * far / (far - near), 0]
        ])
    
    @staticmethod
    def proiezione(vertici):
        return vertici / vertici[:, -1].reshape(-1, 1)
    
    def add_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        
        shape = v.shape
        
        if len(shape) == 3:
            ones = np.ones((v.shape[0], v.shape[1], 4))
            ones[:, :, :3] = v
        
        elif len(shape) == 2:
            ones = np.ones((v.shape[0], 4))
            ones[:, :3] = v
        
        else:
            err_msg = f"Invalid vector shape: {shape}"
            raise IndexError(err_msg)
            
        return ones
    
    def remove_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        
        shape = v.shape
        
        if len(shape) == 3:
            return v[:, :, :3]
        
        elif len(shape) == 2:
            return v[:, :3]
        
        else:
            err_msg = f"Invalid vector shape: {shape}"
            raise IndexError(err_msg)
    
    
    @staticmethod
    def clear_cache_rotazioni() -> None:
        Mate.rotx.cache_clear()
        Mate.rotz.cache_clear()
        

class Camera:
    def __init__(self) -> None:
        
        # TODO -> implementa rollio camera

        # REMEMBER -> PYGAME VISUALIZZA I PUNTI DA IN ALTO A SINISTRA
        
        # O ---------->
        # |
        # |
        # V

        # sistema di riferimento:
        # right -> asse x
        # front -> asse y
        # up    -> asse z

        # default:
        # pos = asse z positivo
        # front = verso asse z negativo
        # right = verso asse x positivo
        # up = verso asse y positivo

        self.pos = np.array([0.,0.,1.,1])

        self.rig_o = np.array([1.,0.,0.,1])
        self.ups_o = np.array([0.,1.,0.,1])
        self.dir_o = np.array([0.,0.,-1.,1])

        self.rig = np.array([1.,0.,0.,1])
        self.ups = np.array([0.,1.,0.,1])
        self.dir = np.array([0.,0.,-1.,1])

        # inclinazioni (sistema di riferimento locale): 
        # rollio -> attorno ad asse y (avvitamento)
        # beccheggio -> attorno ad asse x (pendenza)
        # imbardata -> attorno ad asse z (direzione NSWE)

        # imbardata è relativa all'asse Z globale [0,0,1]   (BLENDER)
        # beccheggio è relativo all'asse X locale           (BLENDER)
        # rollio è relativo all'asse Y locale               (BLENDER)

        self.rollio = 0
        self.becche = 0
        self.imbard = 0

        # con il default la camera dovrebbe guardare dall'alto verso il basso avendo:
        # - sulla sua destra l'asse x positivo
        # - sulla sua sopra l'asse y positivo

        # ---------------------------------------------------------------------------------------

        # valori storati per caricamento impostazioni UI

        self.pos[0] = 1.5
        self.pos[1] = -1.5
        self.pos[2] = 2

        self.becche = round(45 / 57.3248, 3)
        self.rollio = 0
        self.imbard = round(45 / 57.3248, 3)

    def modello_camera(self):

        punto = self.pos
        linea = np.array([self.pos, self.pos + self.dir])

        return punto, linea
    
    def rotazione_camera(self):

        self.rig = self.rig_o @ Mate.rotx(self.becche)
        self.ups = self.ups_o @ Mate.rotx(self.becche)
        self.dir = self.dir_o @ Mate.rotx(self.becche)

        self.rig = self.rig @ Mate.roty(self.rollio)
        self.dir = self.dir @ Mate.roty(self.rollio)
        self.ups = self.ups @ Mate.roty(self.rollio)

        self.rig = self.rig @ Mate.rotz(self.imbard)
        self.ups = self.ups @ Mate.rotz(self.imbard)
        self.dir = self.dir @ Mate.rotz(self.imbard)

    def aggiorna_attributi(self, ctrl, shift, dx, dy):

        if ctrl:
            self.pos[:3] += self.dir[:3] * dy / 100 

        elif shift:
            self.pos[:3] -= self.rig[:3] * dx / 100
            self.pos[:3] -= self.ups[:3] * dy / 100

        else:
            self.becche += dy / 1000
            self.rollio += 0
            self.imbard -= dx / 1000

class Modello:
    def __init__(self, verteces, links, normali, x = 0, y = 0, z = 0, r = 0, b = 0, i = 0) -> None:
        self.verteces_ori = verteces
        self.verteces = self.verteces_ori
        self.links = links
        self.normali = normali
        
        self.x = x
        self.y = y 
        self.z = z
        self.r = r
        self.b = b  
        self.i = i
        
    def applica_rotazioni(self):

        self.verteces = self.verteces_ori @ Mate.rotx(self.b)
        self.verteces = self.verteces @ Mate.roty(self.r)
        self.verteces = self.verteces @ Mate.rotz(self.i)

    def applica_traslazioni(self):

        self.verteces = self.verteces @ Mate.trasl(np.array([self.x, self.y, self.z]))

class PointCloud:
    def __init__(self, verteces, x = 0, y = 0, z = 0, r = 0, b = 0, i = 0) -> None:
        self.verteces_ori = np.array(verteces)
        self.verteces = self.verteces_ori
        
        self.x = x
        self.y = y 
        self.z = z
        self.r = r
        self.b = b  
        self.i = i
        
    def applica_rotazioni(self, autorotation: float):

        self.verteces = self.verteces_ori @ Mate.rotx(0)    
        self.verteces = self.verteces @ Mate.roty(0)   
        self.verteces = self.verteces @ Mate.rotz(autorotation / 300)  

    def applica_traslazioni(self):

        self.verteces = self.verteces @ Mate.trasl(np.array([self.x, self.y, self.z]))


class DebugMesh:
    def __init__(self) -> None: 
        self.axis = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0]
        ])
        
        # Define the side length of the square
        side_length = 5

        # Calculate the coordinates of the vertices of the square
        vertices = np.array([
            [-side_length / 2, side_length / 2],
            [side_length / 2, side_length / 2],
            [side_length / 2, -side_length / 2],
            [-side_length / 2, -side_length / 2]
        ])

        # Determine the number of vertices to distribute along each side
        num_vertices_per_side = 40 // 4  # Divide by 4 sides

        # Generate equally distributed points along each side
        perimeter_points = []
        for i in range(4):  # Iterate over each side
            start_point = vertices[i]
            end_point = vertices[(i + 1) % 4]  # Next vertex to close the loop
            side_vector = end_point - start_point
            distances = np.linspace(0, np.linalg.norm(side_vector), num_vertices_per_side + 1)[1:]
            points_on_side = start_point + distances[:, np.newaxis] / np.linalg.norm(side_vector) * side_vector
            zeros = np.zeros((points_on_side.shape[0], 3))
            zeros[:, :2] = points_on_side
            perimeter_points.extend(zeros)

        # Convert the list of points to a NumPy array
        self.grid = np.array(perimeter_points)
        
        print(self.axis.shape, self.grid.shape)
        
    def scelta_debug(grid: bool = False, axis: bool = False):
        ...    
    
'''
# in ordine:

posizione e rotazione del modello e della telecamera prendono i valori di input dal programma
----------------------------------------------------------------

- vengono appplicate le rotazioni e le traslazioni al modello.
- vengono aggiornati gli attributi della camera, cosicchè si trovi nel posto giusto puntando nel verso giusto

- i punti del modello vengono portati nel camera space
- successivamente vengono portati nel world space

- vengono poi proiettati (frustrum & proiezione)

- vengono centrati
'''