import numpy as np
from _modulo_MATE import Mate, AcceleratedFoo
from _modulo_UI import Logica, Schermo
import pygame

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
        self.pos = self.pos @ Mate.rotz(- self.delta_imbard)
        self.pos = self.pos @ Mate.rot_ax(self.rig, self.delta_becche)
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
            self.focus[:3] -= self.rig[:3] * dx / 10
            self.focus[:3] -= self.ups[:3] * dy / 10
            self.pos[:3] -= self.rig[:3] * dx / 10
            self.pos[:3] -= self.ups[:3] * dy / 10

        # se non è schiacciato nulla -> avverrà rotazione
        else:
            self.becche += dy / 1000
            self.delta_becche = - dy / 1000
            
            self.rollio -= 0
            self.delta_rollio = 0
            
            self.imbard -= dx / 1000
            self.delta_imbard = dx / 1000

        # controllo dello zoom con rotella
        if zoom_in:
            self.pos[:3] += self.dir[:3]
        elif zoom_out:
            self.pos[:3] -= self.dir[:3]


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


class Renderer:

    def __init__(self, schermo: Schermo) -> None:
        self.w = schermo.w 
        self.h = schermo.h
        self.schermo = schermo.schermo
        self.madre = schermo.madre
        self.ancoraggio_x = schermo.ancoraggio_x
        self.ancoraggio_y = schermo.ancoraggio_y


    def camera_setup(self, camera: Camera, logica: Logica) -> tuple[Camera, Logica]:
        '''
        Vengono eseguite 2 sub funzioni in cui:
        Viene ricalcolata la posizione / rotazione / zoom della camera.
        Viene applicata la posizione / rotazione / zoom alla camera 
        Viene inoltre restituita anche la logica aggiornata (zoom)
        '''
        camera.aggiorna_attributi(logica.ctrl, logica.shift, logica.dragging_dx, logica.dragging_dy, logica.scroll_up, logica.scroll_down)
        camera.rotazione_camera()
        
        if logica.scroll_down > 0: logica.scroll_down -= 1
        if logica.scroll_up > 0: logica.scroll_up -= 1 
        
        return camera, logica


    def renderizza_point_cloud(self, points: PointCloud, camera: Camera, logica: Logica, linked: bool = False, points_draw: bool = False) -> None:
        '''
        Viene renderizzato un array di punti nella classe PointCloud
        '''
        
        # aggiunta della 4 coordinata (omogenea) per poter applicare le varie matrici
        points.verteces_ori = Mate.add_homogenous(points.verteces_ori)
        
        # applico le varie trasformazioni (SOLO locali all'oggetto) come l'autorotazione
        points.applica_rotazioni(autorotation=logica.contatore)
        points.applica_traslazioni()

        # rimuovo la coordinata oer non fare casini più avanti
        points.verteces_ori = Mate.remove_homogenous(points.verteces_ori)        
        
        # uso la camera per proiettare tutto nel suo spazio e poter avere i vertici finali
        render_vertex = self.apply_transforms(points.verteces, camera)
        
        for struct in render_vertex[points.links]:
            if not AcceleratedFoo.any_fast(struct, self.w/2, self.h/2):
                if points_draw:
                    for point in struct:
                        pygame.draw.circle(self.schermo, [100, 255, 100], point[:2], 1)
                if linked:
                    pygame.draw.line(self.schermo, [100, 100, 100], struct[0, :2], struct[1, :2], 1)
            
        self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))


    def renderizza_debug_mesh(self, debug: DebugMesh, camera: Camera) -> None:    
        '''
        Viene renderizzato (in base a scelte precedenti) se renderizzare:
        - semplice sistema di riferimento XYZ
        - Griglia centrata al centro con Z = 0
        '''
        
        self.schermo.fill([30, 30, 30])

        # aggiunta della 4 coordinata (omogenea) per poter applicare le varie matrici e direttamente trasformazione camera world
        render_vertex_axis = Mate.add_homogenous(debug.axis)
        render_vertex_axis = self.apply_transforms(render_vertex_axis, camera)
        
        # aggiunta della 4 coordinata (omogenea) per poter applicare le varie matrici e direttamente trasformazione camera world
        render_vertex_grid = Mate.add_homogenous(debug.grid)
        render_vertex_grid = self.apply_transforms(render_vertex_grid, camera)
        
        if debug.debug_axis:
            colore = [0, 0, 0]
            for indice, linea in enumerate(render_vertex_axis[debug.link_axis]):
                if not AcceleratedFoo.any_fast(linea, self.w/2, self.h/2):
                    colore[indice] = 255
                    pygame.draw.line(self.schermo, colore, linea[0, :2], linea[1, :2], 8)
                    colore[indice] = 0
                
        if debug.debug_grid:
            for linea in render_vertex_grid[debug.link_grid]:
                if not AcceleratedFoo.any_fast(linea, self.w/2, self.h/2):
                    pygame.draw.line(self.schermo, [100, 100, 100], linea[0, :2], linea[1, :2], 1)
                
        self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))
        
        
    def apply_transforms(self, vertici: np.ndarray[float], camera: Camera) -> np.ndarray[float]:
        '''
        Applicazione in serie delle varie trasformazioni:
        Camera -> World -> Frustrum -> Proiezione -> Centratura
        '''
        # sposto tutto nel camera world
        render_vertex = vertici @ Mate.camera_world(camera)
        # sposto tutto nello screen world (sistema di riferimento Blender in cui il front è Y e up Z)
        render_vertex = render_vertex @ Mate.screen_world()            
        
        # appiattisco tutto applicando definitivamente la prospettiva
        render_vertex = render_vertex @ Mate.frustrum(self.w, self.h)
        render_vertex = Mate.proiezione(render_vertex)
        
        # centro tutto e scalo per farlo stare sullo schermo
        render_vertex = render_vertex @ Mate.centratura((self.w, self.h))
        
        return render_vertex