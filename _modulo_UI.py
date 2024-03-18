import numpy as np
import pygame
import ctypes
import time

from _modulo_MATE import Mate

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
        pygame.display.flip()

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
        self.schermo = {}

        self.parametri_repeat_elementi : list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]

        self.label_text["title"] = LabelText(self.parametri_repeat_elementi, self.fonts["grande"], w=25, h=4, x=69.25, y=2, text="Benvenuto in Bonsa-py!")
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

    def disegnami(self):
        # self.buffer = np.random.random(self.buffer.shape) * 255
        # self.surface = pygame.surfarray.make_surface(self.buffer) 
        self.schermo.fill((148 / 7, 177 / 7, 255 / 7))
            
    def renderizza_tri_buffer(self, triangles: np.ndarray, logica: Logica) -> None:
        
        # nel dubbio ritrasformo tutto in array
        triangles = np.array(triangles)
        # aggiungo l'1 finale per avere coordinate omogenee
        triangles = Mate.add_homogenous(triangles)
        
        # trasformazioni base (in futuro -> rotazione con mouse)
        triangles = triangles @ Mate.rotx(logica.dt / 300)
        triangles = triangles @ Mate.rotz(logica.dt / 600)
        # triangles = triangles @ Mate.perspective(self.w, self.h)
        # triangles /= triangles[:, :, -1].reshape(triangles.shape[0], triangles.shape[1], 1)
        triangles = triangles @ Mate.scale(self.w / 3, self.w / 3, self.w / 3)
        triangles = triangles @ Mate.traslation(self.w // 2, self.h // 2)
        
        # disegno tutti i triangoli
        for tri in triangles:
            pygame.draw.polygon(self.schermo, [100, 100, 100], tri[:, :2], 1 if logica.dragging else 0)
            
        self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))