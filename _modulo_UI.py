import numpy as np
import pygame
import ctypes
from numba import njit

from _modulo_MATE import Mate, AcceleratedFoo, Camera, PointCloud, DebugMesh, Modello

class Logica:
    def __init__(self) -> None:
        '''
        Inizializzazione di variabili che mi danno infomrazioni sull'UI / comandi da eseguire
        '''
        self.dragging = False
        self.dragging_start_pos = (0,0)
        self.dragging_end_pos = (0,0)
        self.dragging_dx = 0
        self.dragging_dy = 0
        self.mouse_pos = (0,0)
        
        self.skip_salto = False
        self.dt = 0
        self.scena = 0
        
        self.ctrl = False
        self.shift = False
        
        self.scroll_up = 0
        self.scroll_down = 0
        
        self.messaggio_debug1: str = "Empty!"
        self.messaggio_debug2: str = "Empty!"
        self.messaggio_debug3: str = "Empty!"
        self.messaggio_debug4: str = "Empty!"
        self.messaggio_debug5: str = "Empty!"
        
    @property
    def lista_messaggi(self):
        return [self.messaggio_debug1, self.messaggio_debug2, self.messaggio_debug3, self.messaggio_debug4, self.messaggio_debug5]

class UI:
    '''
    Classe responsabile per la generazione dell'interfaccia grafica.
    Conterrà i vari elementi grafici:
    - Schermo
    - Scene
    - Bottoni
    - Labels
    - Entrate
    - Radio
    - Scrolls
    '''

    def __init__(self) -> None:
        '''
        Inizializzazione applicazione
        '''

        # DPI aware
        pygame.init()
        ctypes.windll.user32.SetProcessDPIAware()
        screen_info = pygame.display.Info()
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

        # custom mouse
        pygame.mouse.set_visible(False)
        self.custom_mouse_icon = pygame.image.load("TEXTURES\mouse.png")

        # impostazione dimensione schermi e rapporti
        self.w : int = int(screen_info.current_w * scale_factor)
        self.h : int = int(screen_info.current_h * scale_factor)

        self.aspect_ratio_nativo : float = 2880 / 1800
        self.moltiplicatore_x : float = self.h * self.aspect_ratio_nativo
        self.rapporto_ori : float = self.w / 2880
        self.shift_ori : float = (self.w - self.moltiplicatore_x) / 2

        # generazione finestra
        self.MAIN = pygame.display.set_mode((self.w, self.h))
        self.BG : tuple[int] = (30, 30, 30)
        
        self.clock = pygame.time.Clock()
        self.max_fps : int = 0
        self.current_fps : int = 0
        self.running : int = 1

        # generazione font
        self.lista_font : dict[Font] = {}
        self.lista_font["piccolo"] = Font("piccolo", self.rapporto_ori)
        self.lista_font["medio"] = Font("medio", self.rapporto_ori)
        self.lista_font["grande"] = Font("grande", self.rapporto_ori)
        self.lista_font["gigante"] = Font("gigante", self.rapporto_ori)

        # generazione scene
        parametri_scena_repeat : list = [self.MAIN, self.lista_font, self.moltiplicatore_x, self.shift_ori]
        self.scena : dict[str, DefaultScene] = {}
        self.scena["main"] = DefaultScene(parametri_scena_repeat)


    def cambio_opacit(self) -> None:
        '''
        Modifica l'opacità della finestra principale
        '''
        # Get the window handle using GetActiveWindow
        hwnd = ctypes.windll.user32.GetActiveWindow()

        # Set the window style to allow transparency
        win32style = ctypes.windll.user32.GetWindowLongW(hwnd, ctypes.c_int(-20))  # -20 corresponds to GWL_EXSTYLE
        ctypes.windll.user32.SetWindowLongW(hwnd, ctypes.c_int(-20), ctypes.c_long(win32style | 0x80000))  # 0x80000 corresponds to WS_EX_LAYERED

        # Set the opacity level
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, int(255 * 0.7), 2)  # 0x000000 corresponds to color key

    def colora_bg(self) -> None:
        '''
        Colora la finestra con il colore dello sfondo (self.BG)
        Inoltre disegna uno sfondo di colore (25, 25, 25) per gli aspect ratio diversi da 2880 x 1800
        '''
        self.MAIN.fill((25, 25, 25))
        pygame.draw.rect(self.MAIN, self.BG, [self.shift_ori, 0, self.w - 2 * self.shift_ori, self.h])

    def mouse_icon(self, logica : Logica) -> None:
        '''
        Ottiene la posizione del mouse attuale e ci disegna sopra l'icona custom 
        Assicurarsi che in UI ci sia pygame.mouse.set_visible(False)
        '''
        mouse = logica.mouse_pos
        self.MAIN.blit(self.custom_mouse_icon, mouse)

    def aggiornamento_e_uscita_check(self) -> None:
        '''
        Controlla se la combinazione di uscita è stata selezionata -> Uscita
        Altrimenti aggiornamento pagina
        '''
        # uscita
        keys = pygame.key.get_pressed()
        key_combo = [pygame.K_ESCAPE, pygame.K_SPACE]
        if all(keys[key] for key in key_combo):
            self.running = 0

        # aggiornamento
        self.current_fps = self.clock.get_fps()
        pygame.display.flip()
        
    def aggiorna_messaggi_debug(self, logica: Logica) -> None:
        messaggio_inviato = 0
        for indice, label in self.scena["main"].label_text.items():
            messaggi = logica.lista_messaggi
            if indice.startswith("debug"):
                label.assegna_messaggio(messaggi[messaggio_inviato])
                messaggio_inviato += 1

class Font:
    def __init__(self, dimensione : str = "medio", rapporto : float = 1.0) -> None:    
        
        match dimensione:
            case "piccolo":
                self.dim_font = int(16 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "medio":
                self.dim_font = int(24 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "grande":
                self.dim_font = int(32 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "gigante":
                self.dim_font = int(128 * rapporto) 
                self.font_tipo = pygame.font.Font("TEXTURES/f_full_font.ttf", self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")

class DefaultScene:
    def __init__(self, parametri_repeat : list) -> None:

        self.madre : pygame.Surface = parametri_repeat[0]
        self.fonts : dict[str, Font] = parametri_repeat[1]

        self.moltiplicatore_x : float = parametri_repeat[2]
        self.shift : int = parametri_repeat[3]

        self.ori_y : int = self.madre.get_height()

        self.label_text : dict[str, LabelText] = {}
        self.label_texture = {}
        self.bottoni = {}
        self.entrate = {}
        self.radio = {}
        self.scrolls = {}
        self.schermo: dict[str, Schermo] = {}

        self.parametri_repeat_elementi : list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]

        self.label_text["title"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=2, text="Benvenuto in Bonsa-py!")
        self.label_text["debug1"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=40, text="Empty!")
        self.label_text["debug2"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=50, text="Empty!")
        self.label_text["debug3"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=60, text="Empty!")
        self.label_text["debug4"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=70, text="Empty!")
        self.label_text["debug5"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=80, text="Empty!")
        self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)
        
class LabelText:
    def __init__(self, parametri_locali_elementi : list, font_locale : Font, w : float = 50, h : float = 50, x : float = 0, y : float = 0, bg : tuple[int] = (40, 40, 40), renderizza_bg : bool = True, text : str = "Prova") -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset : int = parametri_locali_elementi[1]

        self.moltiplicatore_x : int = parametri_locali_elementi[2]
        self.ori_y : int = parametri_locali_elementi[3]
        
        self.w : float = self.moltiplicatore_x * w / 100
        self.h : float = self.ori_y * h / 100
        self.x : float = self.moltiplicatore_x * x / 100 + self.offset
        self.y : float = self.ori_y * y / 100

        self.bg : tuple[int] = bg
        self.renderizza_bg : bool = renderizza_bg

        self.screen : pygame.Surface = parametri_locali_elementi[0]

        self.font_locale : Font = font_locale
        self.text : str = text
        self.color_text : tuple[int] = (100, 100, 100)

    def disegnami(self) -> None:
        if self.renderizza_bg:
            pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, self.color_text), (self.x + self.w // 2 - len(self.text) * self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

    def assegna_messaggio(self, str: str = "Empty!") -> None:
        self.text = str

class Schermo:
    def __init__(self, parametri_locali_elementi : list) -> None:

        self.w : int = int(parametri_locali_elementi[3] * 0.9)
        self.h : int = int(parametri_locali_elementi[3] * 0.9)
        self.ancoraggio_x : int = parametri_locali_elementi[3] * 0.05 + parametri_locali_elementi[1]
        self.ancoraggio_y : int = parametri_locali_elementi[3] * 0.05

        self.madre : pygame.Surface = parametri_locali_elementi[0]

        self.buffer : np.ndarray = np.zeros((self.w, self.h, 3))
        self.bg : tuple[int] = (30, 30, 30)

        self.schermo : pygame.Surface = pygame.Surface((self.w, self.h))

    def disegnami(self) -> None:
        '''
        Imposta solo lo sfondo
        ''' 
        self.schermo.fill((148 / 7, 177 / 7, 255 / 7))
        
    
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
        points.applica_rotazioni(autorotation=logica.dt)
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
    
    
    def renderizza_modello_pixel_based(self, modello: Modello, camera: Camera, logica: Logica) -> None:
        
        # aggiunta della 4 coordinata (omogenea) per poter applicare le varie matrici
        modello.verteces_ori = Mate.add_homogenous(modello.verteces_ori)
        
        # applico le varie trasformazioni (SOLO locali all'oggetto) come l'autorotazione
        modello.applica_rotazioni(autorotation=logica.dt)
        modello.applica_traslazioni()
        
        # calcolo normali per shading
        normali = Mate.normale_tri_buffer(modello.verteces, modello.links)
        normali = Mate.versore(normali[:,:3])
        
        # rimuovo la coordinata oer non fare casini più avanti
        modello.verteces_ori = Mate.remove_homogenous(modello.verteces_ori)        
        
        # uso la camera per proiettare tutto nel suo spazio e poter avere i vertici finali
        modello.verteces = self.apply_transforms(modello.verteces, camera)
        
        triangoli = modello.verteces[modello.links]
        uv_triangolo = modello.uv[modello.uv_links]
        
        # schermatura out of cam view
        maschera = np.any((triangoli == self.w/2) | (triangoli == self.h/2), axis=(1, 2))
        triangoli = triangoli[~maschera]
        uv_triangolo = uv_triangolo[~maschera]
        normali = normali[~maschera]
        
        self.buffer = Schermo.rasterization(self.w, self.h, triangoli, normali, uv_triangolo, modello.texture, camera.dir, render_mode=0)
        
        self.surface = pygame.surfarray.make_surface(self.buffer)
        self.madre.blit(self.surface, (self.ancoraggio_x, self.ancoraggio_y))
    
    
    @staticmethod
    @njit()
    def rasterization(w: int, h: int, triangles: np.ndarray[np.ndarray[np.ndarray[float]]], normali: np.ndarray[np.ndarray[float]], uv: np.ndarray[np.ndarray[np.ndarray[float]]], texture: np.ndarray[np.ndarray[float]], cam_dir: np.ndarray[float], render_mode: int = 0) -> np.ndarray[np.ndarray[float]]:
        
        v1 = triangles[:, 0, :]
        v2 = triangles[:, 1, :]
        v3 = triangles[:, 2, :]
        
        triangles = np.ones(triangles.shape)
        triangles[:, 0, :] = v1
        triangles[:, 1, :] = v3
        triangles[:, 2, :] = v2
        
        def cross_edge(vertex1, vertex2, p):
            edge12 = vertex1 - vertex2
            edge1p = vertex1 - p
            return edge12[0] * edge1p[1] - edge12[1] * edge1p[0]
        
        cam_dir_norm = cam_dir / np.linalg.norm(cam_dir)
        
        min_z = np.min(triangles[:,:,2])
        
        colori = np.dot(normali, - cam_dir_norm[:3])
        
        buffer = np.zeros((w, h, 3))
        zbuffer = np.ones((w, h)) * 500

        for triangle, colore, uv_sin in zip(triangles, colori, uv):
            
            if colore >= 0:

                min_x = round(np.min(triangle[:,0]))
                max_x = round(np.max(triangle[:,0]))
                min_y = round(np.min(triangle[:,1]))
                max_y = round(np.max(triangle[:,1]))
                
                if max_x < 0: continue
                if max_y < 0: continue
                if min_x > w: continue
                if min_y > h: continue
                                
                if max_x > w: max_x = w
                if max_y > h: max_y = h
                if min_x < 0: min_x = 0
                if min_y < 0: min_y = 0
                            
                v_1 = triangle[0, :2]
                v_2 = triangle[1, :2]
                v_3 = triangle[2, :2]
                
                z_1 = triangle[0, 2]
                z_2 = triangle[1, 2]
                z_3 = triangle[2, 2]
                
                uv_1 = uv_sin[0]
                uv_2 = uv_sin[1]
                uv_3 = uv_sin[2]
        
                area = cross_edge(v_1, v_2, v_3)
                if area == 0: continue
                
                delta_w0_col = v_2[1] - v_3[1]
                delta_w1_col = v_3[1] - v_1[1]
                delta_w2_col = v_1[1] - v_2[1]
                
                delta_w0_row = v_3[0] - v_2[0]
                delta_w1_row = v_1[0] - v_3[0]
                delta_w2_row = v_2[0] - v_1[0]
                
                p0 = np.array([min_x, min_y]) + np.array([0.5, 0.51])

                w0_row = cross_edge(v_2, v_3, p0)
                w1_row = cross_edge(v_3, v_1, p0)
                w2_row = cross_edge(v_1, v_2, p0)
                
                for y in range(min_y, max_y):
                    w0 = w0_row
                    w1 = w1_row
                    w2 = w2_row
                    for x in range(min_x, max_x):
                        
                        alpha = w0 / area
                        beta = w1 / area
                        gamma = w2 / area
                        
                        if w0 >= 0 and w1 >= 0 and w2 >= 0:
                            
                            z = z_1 * alpha + z_2 * beta + z_3 * gamma 

                            u = uv_1[0] * alpha + uv_3[0] * beta + uv_2[0] * gamma
                            v = uv_1[1] * alpha + uv_3[1] * beta + uv_2[1] * gamma

                            distance = z - min_z
                            
                            if distance < zbuffer[x, y]:
                                
                                zbuffer[x, y] = distance
                            
                                if render_mode == 0: buffer[x, y, :] = [colore * 200 + 50, colore * 200 + 50, colore * 200 + 40]
                                if render_mode == 1: buffer[x, y, :] = texture[int(u * texture.shape[0]), int(v * texture.shape[1])]
                                # buffer[x, y, 0] = alpha * 255
                                # buffer[x, y, 1] = beta * 255
                                # buffer[x, y, 2] = gamma * 255 
                        
                        w0 += delta_w0_col 
                        w1 += delta_w1_col
                        w2 += delta_w2_col
                    
                    w0_row += delta_w0_row 
                    w1_row += delta_w1_row
                    w2_row += delta_w2_row
                    
        return buffer
        
        
    def renderizza_modello(self, modello: Modello, camera: Camera, logica: Logica, wireframe: bool = True) -> None:
        '''
        Viene renderizzato un array di punti nella classe Modello
        '''
        
        # aggiunta della 4 coordinata (omogenea) per poter applicare le varie matrici
        modello.verteces_ori = Mate.add_homogenous(modello.verteces_ori)
        
        # applico le varie trasformazioni (SOLO locali all'oggetto) come l'autorotazione
        modello.applica_rotazioni(autorotation=logica.dt)
        modello.applica_traslazioni()
        
        # calcolo delle backface e colore shading normale
        normali_iterazione = Mate.normale_tri_buffer(modello.verteces, modello.links)
        normali_iterazione = Mate.versore(normali_iterazione)
        colori_normali = np.dot(normali_iterazione, Mate.versore(camera.pos[:3]))
        
        # rimuovo la coordinata oer non fare casini più avanti
        modello.verteces_ori = Mate.remove_homogenous(modello.verteces_ori)        
        
        # calcolo mediana per quick sort
        mediane = Mate.mediana_tri_buffer(modello.verteces, modello.links)
        distanze = Mate.distance_from_cam_tri_buffer(mediane, camera.pos)
        indici_sort = np.argsort(- distanze)
        
        # uso la camera per proiettare tutto nel suo spazio e poter avere i vertici finali
        modello.verteces = self.apply_transforms(modello.verteces, camera)
        
        triangoli = modello.verteces[modello.links]
        
        # sort triangoli e colori
        triangoli = triangoli[indici_sort]
        colori_normali = colori_normali[indici_sort]
        
        # schermatura out of cam view
        maschera_camview = np.any((triangoli == self.w/2) | (triangoli == self.h/2), axis=(1, 2))
        triangoli = triangoli[~maschera_camview]
        colori_normali = colori_normali[~maschera_camview]
        
        # schermatura backculling
        maschera_backface = colori_normali >= 0
        triangoli = triangoli[maschera_backface]
        colori_normali = colori_normali[maschera_backface]
        
        # pre trasformazione in interi
        triangoli = triangoli.astype(np.int32)
        
        colori_normali *= 200
        colori_normali = colori_normali.astype(np.int32)
        
        for triangolo, colore in zip(triangoli, colori_normali):
            pygame.draw.polygon(self.schermo, [colore + 50, colore + 50, colore + 40], triangolo[:, :2], 0)
                    
        self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))
    
    def renderizza_debug_mesh(self, debug: DebugMesh, camera: Camera) -> None:    
        '''
        Viene renderizzato (in base a scelte precedenti) se renderizzare:
        - semplice sistema di riferimento XYZ
        - Griglia centrata al centro con Z = 0
        '''
        
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