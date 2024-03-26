import numpy as np
from functools import cache
from numba import njit

class Mate:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def modulo(v: np.ndarray[float]) -> float:
        return np.linalg.norm(v)
        
    @staticmethod
    def versore(v: np.ndarray[float]) -> np.ndarray[float]:
        return v / Mate.modulo(v)
        
    @staticmethod
    def normale_tri_buffer(v: np.ndarray[np.ndarray[float]], l: np.ndarray[np.ndarray[int]]) -> np.ndarray[np.ndarray[float]]:
        triangoli = v[l]
        v0 = triangoli[:,0,:3]
        v1 = triangoli[:,1,:3]
        v2 = triangoli[:,2,:3]
        return np.cross(v1-v0, v2-v0)
    
    @staticmethod
    def centratura(dim: tuple[int]) -> np.ndarray[np.ndarray[float]]:
        return np.array(
            [
                [dim[0]//2,  0,      0,  0],
                [0,     dim[1]//2,   0,  0],
                [0,     0,      1,  0],
                [dim[0]//2,  dim[1]//2,   0,  1]
            ]
        )

    @staticmethod
    def screen_world() -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1,0,0,0],
            [0,0,1,0],
            [0,-1,0,0],
            [0,0,0,1]
        ])

    @staticmethod
    def camera_world(camera: np.ndarray) -> np.ndarray[np.ndarray[float]]:
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
    def rotx(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(ang), np.sin(ang), 0],
            [0, -np.sin(ang), np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def roty(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [np.cos(ang), 0, np.sin(ang), 0],
            [0, 1, 0, 0],
            [-np.sin(ang), 0, np.cos(ang), 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotz(ang: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [np.cos(ang), np.sin(ang), 0, 0],
            [-np.sin(ang), np.cos(ang), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @staticmethod
    def trasl(array_trasl: list | np.ndarray[float], array_scala: list | np.ndarray[float] = [1, 1, 1]) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [array_scala[0], 0, 0, 0],
            [0, array_scala[1], 0, 0],
            [0, 0, array_scala[2], 0],
            [array_trasl[0], array_trasl[1], array_trasl[2], 1]
        ])

    @staticmethod
    def frustrum(W: int, H: int, h_fov: float = np.pi / 6) -> np.ndarray[np.ndarray[float]]:
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
    def proiezione(vertici: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        ris = vertici / vertici[:, -1].reshape(-1, 1)
        ris[(ris < -2) | (ris > 2)] = 0
        return ris
    
    
    @staticmethod
    def add_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        '''
        Aggiungo la 4 coordinata alla fine dei vettori con 3 coordinate. Supporto strutture come triangoli e liste di vettori
        '''
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
    
    
    @staticmethod
    def remove_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        '''
        Rimuovo la 4 coordinata alla fine dei vettori con 4 coordinate. Supporto strutture come triangoli e liste di vettori
        '''
        shape = v.shape
        
        if len(shape) == 3:
            return v[:, :, :3]
        
        elif len(shape) == 2:
            return v[:, :3]
        
        else:
            err_msg = f"Invalid vector shape: {shape}"
            raise IndexError(err_msg)

class AcceleratedFoo:
    def __init__(self) -> None:
        pass

    @staticmethod
    @njit(fastmath=True)
    def any_fast(v: np.ndarray[float], a: float, b: float) -> bool:
        return np.any((v == a) | (v == b))

class Importer:
    def __init__(self, use_file = True, use_struttura = False) -> None:
        self.use_file = use_file
        self.use_struttura = use_struttura

    def modello(self, nome):
        if self.use_file:
            file_path = f'{nome}'

            vertici = []
            links = []

            with open(file_path, 'r') as file:
                lines = file.readlines()

            for line in lines:
                if line.startswith('v '):
                    vertex = [float(x) for x in line.split()[1:]]
                    vertici.append(vertex)
                elif line.startswith('f '):
                    link = [int(x.split('//')[0]) for x in line.split()[1:]]
                    links.append(link)

            vertici = np.array(vertici)
            links = np.array(links) - 1

            self.verteces = vertici
            self.links = links

class Camera:
    def __init__(self) -> None:
        
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
        # focus = punto di orbita per le rotazioni
        # front = verso asse z negativo
        # right = verso asse x positivo
        # up = verso asse y positivo

        self.pos: np.ndarray[float] = np.array([0.,0.,1.,1])
        self.focus: np.ndarray[float] = np.array([0.,0.,0.,1])

        self.rig_o: np.ndarray[float] = np.array([1.,0.,0.,1])
        self.ups_o: np.ndarray[float] = np.array([0.,1.,0.,1])
        self.dir_o: np.ndarray[float] = np.array([0.,0.,-1.,1])

        self.rig: np.ndarray[float] = np.array([1.,0.,0.,1])
        self.ups: np.ndarray[float] = np.array([0.,1.,0.,1])
        self.dir: np.ndarray[float] = np.array([0.,0.,-1.,1])

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
        
        # i delta angoli sono usati per calcolare lo spostamento relativo per poter orbitare attorno all'oggetto
        
        self.delta_becche = 0
        self.delta_rollio = 0
        self.delta_imbard = 0

        # con il default la camera dovrebbe guardare dall'alto verso il basso avendo:
        # - sulla sua destra l'asse x positivo
        # - sulla sua sopra l'asse y positivo

        # ---------------------------------------------------------------------------------------

        # valori default di partenza

        self.pos[0] = 9.2
        self.pos[1] = -11.1
        self.pos[2] = 5.7
        
        self.becche = 1.4
        self.rollio = 0
        self.imbard = 0.7

    
    def rotazione_camera(self) -> None:
        '''
        Applico le rotazioni in ordine Eulero XYZ ai vari vettori di orientamento della camera
        '''
        self.rig = self.rig_o @ Mate.rotx(self.becche)
        self.ups = self.ups_o @ Mate.rotx(self.becche)
        self.dir = self.dir_o @ Mate.rotx(self.becche)

        self.rig = self.rig @ Mate.roty(self.rollio)
        self.dir = self.dir @ Mate.roty(self.rollio)
        self.ups = self.ups @ Mate.roty(self.rollio)

        self.rig = self.rig @ Mate.rotz(self.imbard)
        self.ups = self.ups @ Mate.rotz(self.imbard)
        self.dir = self.dir @ Mate.rotz(self.imbard)

        self.pos -= self.focus
        self.pos = self.pos @ Mate.rotz(self.imbard - self.delta_imbard)
        # print(self.pos)
        # self.pos = self.pos @ Mate.rotx( self.delta_becche)
        self.pos = self.pos @ Mate.rotz(- self.imbard)
        self.pos += self.focus

    def aggiorna_attributi(self, ctrl: bool, shift: bool, dx: float, dy: float, zoom_in: float, zoom_out: float) -> None:
        '''
        Aggiorna gli attributi della camera come pos / rot / zoom.
        Con le traslazioni viene aggiornato anche il focus attorno al quale avverrà la rotazione
        '''
        
        # se il ctrl è schiacciato -> avverrà zoom
        if ctrl:
            self.pos[:3] += self.dir[:3] * dy / 100

        # se lo shift è schiacciato -> avverrà traslazione
        elif shift:
            # self.focus[:3] -= self.rig[:3] * dx / 100
            # self.focus[:3] -= self.ups[:3] * dy / 100
            self.pos[:3] -= self.rig[:3] * dx / 100
            self.pos[:3] -= self.ups[:3] * dy / 100

        # se non è schiacciato nulla -> avverrà rotazione
        else:
            self.becche -= dy / 1000
            self.delta_becche = dy / 1000
            
            self.rollio -= 0
            self.delta_rollio = 0
            
            self.imbard -= dx / 1000
            self.delta_imbard = dx / 1000

        # controllo dello zoom con rotella
        if zoom_in:
            self.pos[:3] += self.dir[:3]
        elif zoom_out:
            self.pos[:3] -= self.dir[:3]

class Modello:
    def __init__(self, verteces, links, normali, x = 0, y = 0, z = 0, r = 0, b = 0, i = 0, s_x = 1, s_y = 1, s_z = 1) -> None:
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
        self.s_x = s_x
        self.s_y = s_y
        self.s_z = s_z
        
    def applica_rotazioni(self, autorotation: float | None = None) -> None:
        '''
        Applicazioni rotazioni eulero XYZ
        '''
        
        if autorotation != None: self.i = autorotation / 300
        
        self.verteces = self.verteces_ori @ Mate.rotx(self.b)    
        self.verteces = self.verteces @ Mate.roty(self.r)   
        self.verteces = self.verteces @ Mate.rotz(self.i)  

    def applica_traslazioni(self) -> None:
        '''
        Applicazioni traslazioni
        '''
        self.verteces = self.verteces @ Mate.trasl(np.array([self.x, self.y, self.z]), np.array([self.s_x, self.s_y, self.s_z]))

class PointCloud:
    def __init__(self, verteces, links = None, x = 0, y = 0, z = 0, r = 0, b = 0, i = 0, s_x = 1, s_y = 1, s_z = 1) -> None:
        self.verteces_ori = np.array(verteces)
        self.verteces = self.verteces_ori
        self.links: np.ndarray = links[:, :2] if links != None else None
        
        self.x = x
        self.y = y 
        self.z = z
        self.r = r
        self.b = b  
        self.i = i
        self.s_x = s_x
        self.s_y = s_y
        self.s_z = s_z
        
    def applica_rotazioni(self, autorotation: float | None = None) -> None:
        '''
        Applicazioni rotazioni eulero XYZ
        '''
        
        if autorotation != None: self.i = autorotation / 300
        
        self.verteces = self.verteces_ori @ Mate.rotx(self.b)    
        self.verteces = self.verteces @ Mate.roty(self.r)   
        self.verteces = self.verteces @ Mate.rotz(self.i)  

    def applica_traslazioni(self) -> None:
        '''
        Applicazioni traslazioni
        '''
        self.verteces = self.verteces @ Mate.trasl(np.array([self.x, self.y, self.z]), np.array([self.s_x, self.s_y, self.s_z]))


class DebugMesh:
    def __init__(self) -> None: 
        self.axis = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0]
        ])
        
        self.link_axis = np.array([[0,3], [1,3], [2,3]])
        
        '------------------------------------------------------------------'
        
        # Define the side length of the square
        side_length = 10
        
        tmp1 = [[x - side_length // 2, side_length // 2, 0] for x in range(side_length)]
        tmp2 = [[side_length // 2, side_length // 2 - y, 0] for y in range(side_length)]
        tmp3 = [[side_length // 2 - x, - side_length // 2, 0] for x in range(side_length)]
        tmp4 = [[- side_length // 2, y - side_length // 2, 0] for y in range(side_length)]

        self.grid = (np.ravel(np.array([tmp1, tmp2, tmp3, tmp4])).reshape(-1, 3))
        
        tmp1 = [[i, 3 * side_length - i] for i in range(side_length + 1)]
        tmp2 = [[i + side_length, 4 * side_length - i] for i in range(side_length + 1)]
        
        self.link_grid = (np.ravel(np.array([tmp1, tmp2])).reshape(-1, 2))
        self.link_grid[np.where(self.link_grid == side_length * 4)] = 0

        # Calculate the 
        self.debug_grid: bool = False
        self.debug_axis: bool = False
        
    def scelta_debug(self, grid: bool = False, axis: bool = False) -> None:
        '''
        Decidi cosa visualizzare durante il debug della camera
        '''
        self.debug_grid = grid
        self.debug_axis = axis