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
    
    @cache
    @staticmethod
    def rotx(a: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [np.cos(a), np.sin(a), 0, 0],
            [-np.sin(a), np.cos(a), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    
    @cache
    @staticmethod
    def rotz(a: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1, 0, 0, 0],
            [0, np.cos(a), np.sin(a), 0],
            [0, -np.sin(a), np.cos(a), 0],
            [0, 0, 0, 1]
        ])
        
    def rotate_using_camera():
        # alpha = a.value
        # beta = b.value

        # cam_p_tmp = np.array([zoom.value * np.cos(alpha) * np.cos(beta), zoom.value * np.sin(alpha) * np.cos(beta), zoom.value * np.sin(beta), 1])

        # cam_dir = -cam_p_tmp[:3]
        # cam_dir /= np.linalg.norm(cam_dir)
        # cam_rig = np.array([cam_dir[1], - cam_dir[0], 0])
        # cam_rig /= np.linalg.norm(cam_rig)
        # cam_up = np.cross(cam_rig, cam_dir)

        # cam_p = cam_p_tmp + np.array([0, 0, offset.value, 0])
            
        def camera_world(cam_p: np.ndarray[float], cam_rig: np.ndarray[float], cam_up: np.ndarray[float], cam_dir: np.ndarray[float]) -> np.ndarray[np.ndarray[float]]:
            return np.array(
                [[1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [-cam_p[0], -cam_p[1], -cam_p[2], 1]]
            ) @ np.array(
                [[cam_rig[0], cam_up[0], cam_dir[0], 0],
                [cam_rig[1], cam_up[1], cam_dir[1], 0],
                [cam_rig[2], cam_up[2], cam_dir[2], 0],
                [0, 0, 0, 1]]
            )
    
    @cache
    @staticmethod
    def traslation(x: float, y: float, z: float = 0.0) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [x, y, z, 1]
        ])
    
    @cache
    @staticmethod
    def scale(x: float, y: float, z: float) -> np.ndarray[np.ndarray[float]]:
        return np.array([
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ])
    
    @cache
    @staticmethod
    def perspective(w, h, fov: float = np.pi / 3) -> np.ndarray[np.ndarray[float]]:
        h_fov = fov
        v_fov = h_fov * h / w
        left = np.tan(h_fov / 2)
        right = -left
        top = np.tan(v_fov / 2)
        bottom = -top
        far = 100
        near = 0.01
        return np.array([
            [2 / (right - left), 0, 0, 0],
            [0, 2 / (top - bottom), 0, 0],
            [0, 0, (far + near) / (far - near), 1],
            [0, 0, -2 * near * far / (far - near), 0]
        ])
    
    def add_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        ones = np.ones((v.shape[0], v.shape[1], 4))
        ones[:, :, :3] = v
        return ones
    
    def remove_homogenous(v: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
        return v[:, :, :3]
    
    @staticmethod
    def clear_cache_rotazioni() -> None:
        Mate.rotx.cache_clear()
        Mate.rotz.cache_clear()