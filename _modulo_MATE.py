import numpy as np
from functools import cache
from numba import njit

class Mate:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def modulo(v: np.ndarray[float] | np.ndarray[np.ndarray[float]]) -> float:
        if type(v[0]) == np.ndarray:
            return np.linalg.norm(v, axis=1)
        else:     
            return np.linalg.norm(v)
        
    @staticmethod
    def versore(v: np.ndarray[float] | np.ndarray[np.ndarray[float]]) -> np.ndarray[float]:
        if type(v[0]) == np.ndarray:
            return np.divide(v, Mate.modulo(v)[:,None])
        else:     
            return v / Mate.modulo(v)
        
    @staticmethod
    def mediana_tri_buffer(v: np.ndarray[np.ndarray[float]], l: np.ndarray[np.ndarray[int]]) -> np.ndarray[np.ndarray[float]]:
        triangoli = v[l]
        v0 = triangoli[:,0,:3]
        v1 = triangoli[:,1,:3]
        v2 = triangoli[:,2,:3]
        return (v0 + v1 + v2) / 3
    
    @staticmethod
    def distance_from_cam_tri_buffer(v: np.ndarray[float], cam: np.ndarray[int]) -> np.ndarray[float]:
        to_origin = v - cam[:3]
        ris = Mate.modulo(to_origin)
        return ris
    
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
                [dim[0]/2,  0,      0,  0],
                [0,     dim[1]/2,   0,  0],
                [0,     0,      1,  0],
                [dim[0]/2,  dim[1]/2,   0,  1]
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
    def camera_world(camera) -> np.ndarray[np.ndarray[float]]:
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
    def rot_ax(axis: np.ndarray[float], ang: float) -> np.ndarray[np.ndarray[float]]:
        K = np.array([
            [0, -axis[2], axis[1], 0],
            [axis[2], 0, -axis[0], 0],
            [-axis[1], axis[0], 0, 0],
            [0, 0, 0, 0]
        ])

        return np.eye(4) + np.sin(ang) * K + (1 - np.cos(ang)) * np.dot(K, K)
    
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
        distanze = vertici[:, -1]
        indici_dist_neg = np.where(distanze < 0)

        ris = vertici / vertici[:, -1].reshape(-1, 1)
        ris[(ris < -12) | (ris > 12)] = 2
        ris[indici_dist_neg] = np.array([2, 2, 2, 1])

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