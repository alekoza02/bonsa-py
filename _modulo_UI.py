import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import numpy as np
import pygame
import ctypes
import psutil
import configparser
import os
from time import strftime
from tkinter import filedialog


class Font:
    def __init__(self, dimensione: str = "medio", rapporto: float = 1.0) -> None:    
        
        path = os.path.join('TEXTURES', 'f_full_font.ttf')

        match dimensione:
            case "piccolo":
                self.dim_font = int(18 * rapporto) 
                self.font_tipo = pygame.font.Font(path, self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "medio":
                self.dim_font = int(24 * rapporto) 
                self.font_tipo = pygame.font.Font(path, self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "grande":
                self.dim_font = int(32 * rapporto) 
                self.font_tipo = pygame.font.Font(path, self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")
            case "gigante":
                self.dim_font = int(128 * rapporto) 
                self.font_tipo = pygame.font.Font(path, self.dim_font)
                self.font_pixel_dim = self.font_tipo.size("a")


class Logica:
    def __init__(self) -> None:
        '''
        Inizializzazione di variabili che mi danno infomrazioni sull'UI / comandi da eseguire
        '''
        self.dragging = False
        self.original_start_pos = (0,0)
        self.dragging_start_pos = (0,0)
        self.dragging_end_pos = (0,0)
        self.dragging_dx = 0
        self.dragging_dy = 0
        self.mouse_pos = (0,0)

        self.click_sinistro = False
        self.click_destro = False
        
        self.skip_salto = False
        self.dt = 0
        self.contatore = 0
        self.scena = 0
        
        self.ctrl = False
        self.shift = False
        self.backspace = False
        self.left = False
        self.right = False
        self.tab = False

        self.acc_backspace = 0
        self.acc_left = 0
        self.acc_right = 0
        
        self.scroll_up = 0
        self.scroll_down = 0

        self.aggiorna_plot: bool = True
        
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

    def __init__(self, config: configparser.ConfigParser) -> None:
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
        path = os.path.join('TEXTURES', 'mouse.png') 
        self.custom_mouse_icon = pygame.image.load(path)

        # impostazione dimensione schermi e rapporti
        self.w: int = int(screen_info.current_w * scale_factor)
        self.h: int = int(screen_info.current_h * scale_factor)

        self.aspect_ratio_nativo: float = 2880 / 1800
        self.moltiplicatore_x: float = self.h * self.aspect_ratio_nativo
        self.rapporto_ori: float = self.w / 2880
        self.shift_ori: float = (self.w - self.moltiplicatore_x) / 2

        # generazione finestra
        self.MAIN = pygame.display.set_mode((self.w, self.h))
        self.BG: tuple[int] = eval(config.get(config.get("Default", "tema"), 'ui_bg'))
        
        self.clock = pygame.time.Clock()
        self.max_fps: int = 0
        self.current_fps: int = 0
        self.running: int = 1
        self.debugging: bool = eval(config.get("Default", "debugging"))

        self.cpu_sample: list[int] = [0 for i in range(100)]

        # generazione font
        self.lista_font: dict[Font] = {}
        self.lista_font["piccolo"] = Font("piccolo", self.rapporto_ori)
        self.lista_font["medio"] = Font("medio", self.rapporto_ori)
        self.lista_font["grande"] = Font("grande", self.rapporto_ori)
        self.lista_font["gigante"] = Font("gigante", self.rapporto_ori)

        # generazione scene
        self.config = config
        self.parametri_scena_repeat: list = [self.MAIN, self.lista_font, self.moltiplicatore_x, self.shift_ori, self.config]
        self.scena: dict[str, Scena] = {}
        self.scena["main"] = Scena(self.parametri_scena_repeat); self.scena["main"].build_main()
        
        self.entrata_attiva: Entrata = None


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


    def mouse_icon(self, logica: Logica) -> None:
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

        # aggiornamento
        self.current_fps = self.clock.get_fps()

        # PC status
        self.scena["main"].label_text["memory"].text = f"Memory usage: {psutil.Process().memory_info().rss / 1024**2:.2f} MB"
        
        self.cpu_sample.pop(0)
        self.cpu_sample.append(psutil.cpu_percent(interval=0))
        self.scena["main"].label_text["cpu"].text = f"CPU usage: {sum(self.cpu_sample) / len(self.cpu_sample):.0f}%"

        self.scena["main"].label_text["fps"].text = f"FPS: {self.current_fps:.2f}"

        self.scena["main"].label_text["clock"].text = strftime("%X, %x")
        
        battery = psutil.sensors_battery()
        if battery:
            if battery.power_plugged: charging = "chr"
            else: charging = "NO chr"
            self.scena["main"].label_text["battery"].text = f"Battery: {battery.percent:.1f}% {charging}"
        

        # uscita
        keys = pygame.key.get_pressed()
        key_combo = [pygame.K_ESCAPE, pygame.K_SPACE]
        if all(keys[key] for key in key_combo):
            self.running = 0

            try:
                # ferma multi-processi
                self.gestore_multiprocess.stahp = True
                self.gestore_multiprocess.try_fast_kill()
            except AttributeError:
                ...

        pygame.display.flip()
        

    @staticmethod
    def salva_screenshot(path, schermo):
        try:
            pygame.image.save(schermo, path)
        except FileNotFoundError:
            pass


    def start_cycle(self, logica: Logica):
        # impostazione inizio giro
        logica.dt = self.clock.tick(self.max_fps)
        logica.contatore += 1
        self.colora_bg()
        self.mouse_icon(logica)

        logica.dragging_dx = 0
        logica.dragging_dy = 0
        logica.mouse_pos = pygame.mouse.get_pos()


    def event_manager(self, eventi: pygame.event, logica: Logica):

        # Stato di tutti i tasti
        keys = pygame.key.get_pressed()

        # CONTROLLO CARATTERI SPECIALI
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
        logica.backspace = keys[pygame.K_BACKSPACE]
        logica.left = keys[pygame.K_LEFT]
        logica.right = keys[pygame.K_RIGHT]
        logica.tab = keys[pygame.K_TAB]


        # reset variabili
        logica.click_sinistro = False
        logica.click_destro = False

        # scena main UI
        for event in eventi:
            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    logica.click_sinistro = True

                    [elemento.selezionato_bot(event) for indice, elemento in self.scena["main"].bottoni.items()]

                if event.button == 3:
                    logica.click_destro = True
                    logica.dragging = True
                    logica.original_start_pos = logica.mouse_pos
                    logica.dragging_end_pos = logica.mouse_pos
                
                if event.button == 4:
                    logica.scroll_up += 10
                if event.button == 5:
                    logica.scroll_down += 10

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3: 
                    logica.dragging = False
                    logica.dragging_end_pos = logica.mouse_pos

            if event.type == pygame.MOUSEMOTION:
                if logica.dragging:
                    logica.dragging_start_pos = logica.dragging_end_pos
                    logica.dragging_end_pos = logica.mouse_pos
                    logica.dragging_dx = logica.dragging_end_pos[0] - logica.dragging_start_pos[0]
                    logica.dragging_dy = - logica.dragging_end_pos[1] + logica.dragging_start_pos[1] # sistema di riferimento invertito

            
            # input -> tastiera con caratteri e backspace
            if self.entrata_attiva != None:

                if " " in self.entrata_attiva.text: ricercatore = " " 
                elif "\\" in self.entrata_attiva.text: ricercatore = "\\"
                elif "/" in self.entrata_attiva.text: ricercatore = "/"
                else: ricercatore = None

                if event.type == pygame.TEXTINPUT:           
                    self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore] + event.text + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
                    self.entrata_attiva.puntatore += len(event.text)
                    self.entrata_attiva.dt_animazione = 0

                if event.type == pygame.KEYDOWN:
                    
                    tx = self.entrata_attiva.text
                            
                    if event.key == pygame.K_BACKSPACE:
                        if logica.ctrl:
                            if ricercatore is None:
                                self.entrata_attiva.puntatore = 0
                                self.entrata_attiva.text = "" 
                            else:
                                nuovo_puntatore = tx[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                                text2eli = tx[nuovo_puntatore : self.entrata_attiva.puntatore]
                                self.entrata_attiva.puntatore = nuovo_puntatore
                                self.entrata_attiva.text = tx.replace(text2eli, "") 

                        else:
                            if self.entrata_attiva.puntatore != 0:
                                self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore-1] + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
                            if self.entrata_attiva.puntatore > 0:
                                self.entrata_attiva.puntatore -= 1

                    if event.key == pygame.K_LEFT:
                        if self.entrata_attiva.puntatore > 0:
                            if logica.ctrl:
                                if ricercatore is None:
                                    self.entrata_attiva.puntatore = 0
                                else:
                                    self.entrata_attiva.puntatore = tx[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                            else: 
                                self.entrata_attiva.puntatore -= 1

                    if event.key == pygame.K_RIGHT:
                        if self.entrata_attiva.puntatore < len(self.entrata_attiva.text):
                            if logica.ctrl:

                                if ricercatore is None:
                                    self.entrata_attiva.puntatore = len(self.entrata_attiva.text)
                                else:

                                    # trovo l'indice di dove inizia la frase
                                    start = tx.find(tx[self.entrata_attiva.puntatore:].lstrip(), self.entrata_attiva.puntatore, len(tx))
                                    # se non la trovo mi blocco dove sono partito
                                    if start == -1: start = self.entrata_attiva.puntatore

                                    # se la trovo, cerco la parola successiva
                                    found = tx.find(ricercatore, start, len(tx))
                                    # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                                    if found == -1: found = len(tx.rstrip())

                                    self.entrata_attiva.puntatore = found
                                    
                            else:
                                self.entrata_attiva.puntatore += 1

                    self.entrata_attiva.dt_animazione = 0 

        if logica.backspace:
            logica.acc_backspace += 1
            if logica.acc_backspace > 20:
                if self.entrata_attiva.puntatore != 0:
                    self.entrata_attiva.text = self.entrata_attiva.text[:self.entrata_attiva.puntatore-1] + self.entrata_attiva.text[self.entrata_attiva.puntatore:]
                if self.entrata_attiva.puntatore > 0:
                    self.entrata_attiva.puntatore -= 1
        else: 
            logica.acc_backspace = 0

        if logica.left:
            logica.acc_left += 1
            if logica.acc_left > 20:
                if logica.ctrl:
                    self.entrata_attiva.puntatore = self.entrata_attiva.text[:self.entrata_attiva.puntatore].rstrip().rfind(ricercatore)+1
                elif self.entrata_attiva.puntatore > 0: self.entrata_attiva.puntatore -= 1
                self.entrata_attiva.dt_animazione = 0 
        else: 
            logica.acc_left = 0
        
        if logica.right:
            logica.acc_right += 1
            if logica.acc_right > 20:
                if logica.ctrl:
                    tx = self.entrata_attiva.text
                    # trovo l'indice di dove inizia la frase
                    start = tx.find(tx[self.entrata_attiva.puntatore:].lstrip(), self.entrata_attiva.puntatore, len(tx))
                    # se non la trovo mi blocco dove sono partito
                    if start == -1: start = self.entrata_attiva.puntatore

                    # se la trovo, cerco la parola successiva
                    found = tx.find(ricercatore, start, len(tx))
                    # se non la trovo guardo mi posizione nell'ultimo carattere diverso da uno spazio
                    if found == -1: found = len(tx.rstrip())

                    self.entrata_attiva.puntatore = found
                        
                elif self.entrata_attiva.puntatore < len(self.entrata_attiva.text): self.entrata_attiva.puntatore += 1
                self.entrata_attiva.dt_animazione = 0 
        else: 
            logica.acc_right = 0



class Scena:
    def __init__(self, parametri_repeat: list) -> None:
        # 0.625
        self.madre: pygame.Surface = parametri_repeat[0]
        self.fonts: dict[str, Font] = parametri_repeat[1]

        self.moltiplicatore_x: float = parametri_repeat[2]
        self.shift: int = parametri_repeat[3]

        self.config: configparser.ConfigParser = parametri_repeat[4]

        self.ori_y: int = self.madre.get_height()

        self.entrata_attiva = None

        self.label_text: dict[str, LabelText] = {}
        self.label_texture = {}
        self.bottoni: dict[str, Button] = {}
        self.entrate: dict[str, Entrata] = {}
        self.paths: dict[str, Path] = {}
        self.multi_box: dict[str, MultiBox] = {}
        self.scrolls: dict[str, ScrollConsole] = {}
        self.schermo: dict[str, Schermo] = {}
        self.ui_signs: dict[str, UI_signs] = {}
        self.tabs: dict[str, TabUI] = {}

        self.parametri_repeat_elementi: list = [self.madre, self.shift, self.moltiplicatore_x, self.ori_y]
        
        self.tema = self.config.get('Default', 'tema')


    def disegnami_standard_version(self, logica: Logica) -> None:
        
        # ui elements
        [label.disegnami() for indice, label in self.label_text.items()]
        [bottone.disegnami() for indice, bottone in self.bottoni.items()]
        [entrata.disegnami(logica) for indice, entrata in self.entrate.items()]
        [scrolla.disegnami(logica) for indice, scrolla in self.scrolls.items()]
        [segno.disegnami() for indice, segno in self.ui_signs.items()]


    def disegnami_tabs_version(self, logica: Logica):
        [tab.disegna_tab(logica) for index, tab in self.tabs.items()]

    
    def build_main(self):
        # LABEL
        # --------------------------------------------------------------------------------
        # statici
        self.label_text["memory"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=81, y=98, text="Memory usage: X MB", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["battery"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=72, y=98, text="Battery: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["fps"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=66, y=98, text="FPS: X", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["cpu"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=59, y=98, text="CPU usage: X%", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["clock"] = LabelText(self.parametri_repeat_elementi, self.fonts, "piccolo", w=10, h=1.8, x=92, y=98, text="00:00, 1/1/2000", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        
        self.label_text["title"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=2, text="Benvenuto in Bonsa-py!", renderizza_bg=False, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["debug1"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=30, text="Empty!", renderizza_bg=True, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["debug2"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=40, text="Empty!", renderizza_bg=True, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["debug3"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=50, text="Empty!", renderizza_bg=True, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["debug4"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=60, text="Empty!", renderizza_bg=True, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        self.label_text["debug5"] = LabelText(self.parametri_repeat_elementi, self.fonts, "grande", w=25, h=4, x=69.25, y=70, text="Empty!", renderizza_bg=True, bg=eval(self.config.get(self.tema, 'label_bg')), color_text=eval(self.config.get(self.tema, 'label_text')))
        
        self.schermo["viewport"] = Schermo(self.parametri_repeat_elementi)
    
        self.bottoni["ren_mode"] = Button(self.parametri_repeat_elementi, self.fonts, "grande", text="Render Mode", w=12, h=4, x=82.25, y=80, bg = eval(self.config.get(self.tema, 'bottone_bg')), color_text = eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato = eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled = eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno = eval(self.config.get(self.tema, 'bottone_contorno')), bg2 = eval(self.config.get(self.tema, 'bottone_bg2')))
        self.bottoni["ren_mode"].tooltip = "Abilita la visualizzazione\n3D del modello."
        self.bottoni["foglie"] = Button(self.parametri_repeat_elementi, self.fonts, "grande", text="Foglie", w=12, h=4, x=69.25, y=80, bg = eval(self.config.get(self.tema, 'bottone_bg')), color_text = eval(self.config.get(self.tema, 'bottone_color_text')), colore_bg_schiacciato = eval(self.config.get(self.tema, 'bottone_colore_bg_schiacciato')), contorno_toggled = eval(self.config.get(self.tema, 'bottone_contorno_toggled')), contorno = eval(self.config.get(self.tema, 'bottone_contorno')), bg2 = eval(self.config.get(self.tema, 'bottone_bg2')))
        self.bottoni["foglie"].tooltip = "Abilita la visualizzazione\ndelle foglie."

        # TABS LINK
        self.tabs["sys_info"] = TabUI(name="sys_info", 
            labels=[self.label_text["memory"], self.label_text["battery"], self.label_text["fps"], self.label_text["cpu"], self.label_text["clock"]]
        )

        self.tabs["scene_info"] = TabUI(name="scene_info",
            labels=[self.label_text["title"], self.label_text["debug1"], self.label_text["debug2"], self.label_text["debug3"], self.label_text["debug4"], self.label_text["debug5"]],
            bottoni=[self.bottoni["ren_mode"], self.bottoni["foglie"]],
        )




class LabelText:
    def __init__(self, parametri_locali_elementi: list, font_locale: dict[str, Font], size: str = "medio", w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, color_text: tuple[int] = (200, 200, 200), text: str = "Prova", autodistruggi: bool = False) -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.timer: int = 0
        self.autodistruggi: bool = autodistruggi

        self.bg: tuple[int] = bg
        self.renderizza_bg: bool = renderizza_bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]

        self.font_locale_d: Font = font_locale[size]
        self.font_locale_s: Font = font_locale["piccolo"]
        self.text: str = text
        self.color_text: tuple[int] = color_text


    def disegnami(self) -> None:

        if self.autodistruggi: self.timer -= 1

        if self.autodistruggi and self.timer < 0:
            return

        if self.renderizza_bg:
            pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
        
        if type(self.text) == str and self.text.count("£") == 2:
            
            start_index = self.text.find("£") + 1
            end_index = self.text.find("£", start_index)
        
            contatore_righe = 0

            for riga in self.text[:start_index - 1].split("\n"):
                self.screen.blit(self.font_locale_d.font_tipo.render(f"{riga}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_d.font_pixel_dim[1]))
                contatore_righe += 1

            for riga in self.text[start_index - 1:end_index].split("\n"):
                self.screen.blit(self.font_locale_s.font_tipo.render(f"{riga[1:-1]}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_s.font_pixel_dim[1]))
                contatore_righe += 1

            for riga in self.text[end_index + 1:].split("\n"):
                self.screen.blit(self.font_locale_d.font_tipo.render(f"{riga}", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + contatore_righe * 1.5 * self.font_locale_d.font_pixel_dim[1]))
                contatore_righe += 1

        else:
            if type(self.text) == list:
            
                numero_linee = 15

                if len(self.text) > numero_linee:
                    for i, riga in enumerate(self.text[:np.ceil(numero_linee / 2).astype(int)]):
                        text = f"{riga}" if len(riga) < 93 else f"{riga[:90]}..." 
                        self.screen.blit(self.font_locale_d.font_tipo.render(text, True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + i * 1.5 * self.font_locale_d.font_pixel_dim[1]))
                    
                    self.screen.blit(self.font_locale_d.font_tipo.render(f"-- {len(self.text) - numero_linee} righe non visualizzate --", True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + (i + 1.5) * 1.5 * self.font_locale_d.font_pixel_dim[1]))

                    for i, riga in enumerate(self.text[-10:]):
                        text = f"{riga}" if len(riga) < 93 else f"{riga[:90]}..." 
                        self.screen.blit(self.font_locale_d.font_tipo.render(text, True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + + (i + np.floor(numero_linee / 2) + 3) * 1.5 * self.font_locale_d.font_pixel_dim[1]))

                else:

                    for i, riga in enumerate(self.text):
                        text = f"{riga}" if len(riga) < 93 else f"{riga[:90]}..." 
                        self.screen.blit(self.font_locale_d.font_tipo.render(text, True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + i * 1.5 * self.font_locale_d.font_pixel_dim[1]))

            elif type(self.text) == str:
                
                for i, riga in enumerate(self.text.split("\n")):
                    text = f"{riga}" if len(riga) < 93 else f"{riga[:90]}..." 
                    self.screen.blit(self.font_locale_d.font_tipo.render(text, True, self.color_text), (self.x + 2 * self.font_locale_d.font_pixel_dim[0], self.y + self.h // 2 - self.font_locale_d.font_pixel_dim[1] // 2 + i * 1.5 * self.font_locale_d.font_pixel_dim[1]))


    def assegna_messaggio(self, str: str = "Empty!") -> None:
        self.text = str



class UI_signs:
    def __init__(self, parametri_locali_elementi: list, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, bg: tuple[int] = (40, 40, 40), spessore: int = 1) -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.x1: float = self.moltiplicatore_x * x1 / 100 + self.offset
        self.y1: float = self.ori_y * y1 / 100
        self.x2: float = self.moltiplicatore_x * x2 / 100 + self.offset
        self.y2: float = self.ori_y * y2 / 100

        self.spessore: int = spessore

        self.bg: tuple[int] = bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]


    def disegnami(self) -> None:
        pygame.draw.line(self.screen, self.bg, [self.x1, self.y1], [self.x2, self.y2], self.spessore)
        


class Button:
    def __init__(self, parametri_locali_elementi: list, font_locale: dict[str, Font], size: str = "piccolo", w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", tipologia: str = "toggle", toggled: bool = False, texture: None = None, multi_box: bool = False, visibile: bool = True, color_text: tuple[int] = (200, 200, 200), colore_bg_schiacciato = [210, 210, 210], contorno_toggled = [84,160,134], contorno = [160,84,134], bg2: tuple[int] = (42, 80, 67)) -> None:
        '''
        parametri_locali_elementi dovrà contenere:
        - schermo madre
        - shift_x
        - x a disposizione sullo schermo
        - y a disposizione sullo schermo
        '''
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.bg: tuple[int] = bg
        self.renderizza_bg: bool = renderizza_bg

        self.screen: pygame.Surface = parametri_locali_elementi[0]

        self.font_locale: Font = font_locale[size]
        self.text: str = text
        self.tooltip = "Tooltip."
        self.color_text: tuple[int] = color_text

        self.font_tooltip: Font = font_locale["piccolo"]

        self.multi_box = multi_box
        self.tipologia = tipologia
        self.toggled = toggled
        self.colore_bg_schiacciato = [i+10 if i < 245 else 255 for i in self.bg]

        self.contorno_toggled = contorno_toggled
        self.contorno = contorno

        self.animation: bool = False
        self.durata: int = 30
        self.tracker: int = 0
        self.bg2: tuple[int] = bg2

        self.visibile: bool = visibile

        self.hover = False
        self.dt_hover = 0

        self.tooltip = "Lorem ipsum dolor sit amet, consectetur adipisci elit, sed do eiusmod tempor incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrum exercitationem ullamco laboriosam, nisi ut aliquid ex ea commodi consequatur. Duis aute irure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

        if texture is None:
            self.texture = None
        else:
            path = os.path.join(f"TEXTURES", f'{texture}.png')
            self.texture = pygame.image.load(path)
            self.texture = pygame.transform.scale(self.texture, (self.w, self.h))


    def disegnami(self):
        if self.visibile:
            colore_scelto = np.array(self.colore_bg_schiacciato) if self.toggled else np.array(self.bg)
            
            if self.animation:
                self.tracker += 1

                colore_scelto = np.array([int(p * (self.durata - self.tracker) / self.durata + d * (self.tracker) / self.durata) for p, d in zip(self.bg2, colore_scelto)])
                

                if self.tracker > self.durata:
                    self.tracker = 0
                    self.animation = False
            
            
            if self.hover:
                colore_scelto += np.array([50, 50, 50])

            colore_secondario = self.contorno_toggled if self.toggled else self.contorno
            pygame.draw.rect(self.screen, colore_secondario, [self.x-1, self.y-1, self.w+2, self.h+2], border_top_left_radius=10, border_bottom_right_radius=10)
            pygame.draw.rect(self.screen, colore_scelto, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)
            
            if self.texture is None:
                self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, self.color_text), (self.x + self.w // 2 - len(self.text) * self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))
            else:
                self.screen.blit(self.texture, (self.x, self.y))


    def selezionato_bot(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.bounding_box.collidepoint(event.pos) and not self.multi_box and self.visibile:
                if self.toggled:
                    self.toggled = False
                else:
                    self.toggled = True
                    self.animation = True
                    self.tracker = 0
                return True
        return False


    def hover_update(self, logica: Logica) -> None:
        if self.bounding_box.collidepoint(logica.mouse_pos) and self.visibile:
            self.hover = True
            self.dt_hover += logica.dt
        else:
            self.hover = False
            self.dt_hover = 0

        if self.dt_hover > 1000:

            elenco = self.tooltip.split("\n")
            linee = len(elenco)
            max_larghezza = max([len(linea) for linea in elenco])
            
            altezza_tooltip = (linee + 1) * self.font_tooltip.font_pixel_dim[1]

            pygame.draw.rect(self.screen, self.bg, [logica.mouse_pos[0] - 150, logica.mouse_pos[1] - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2), altezza_tooltip])
            pygame.draw.rect(self.screen, [100, 100, 100], [logica.mouse_pos[0] - 150 - 1, logica.mouse_pos[1] - 1 - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2) + 1, altezza_tooltip + 1], 1)
            
            for linea in range(linee):             
                self.screen.blit(self.font_tooltip.font_tipo.render(f"{elenco[linea]}", True, self.color_text), (logica.mouse_pos[0] - 150 + self.font_tooltip.font_pixel_dim[0], logica.mouse_pos[1] + self.font_tooltip.font_pixel_dim[1] * (linea + 0.5) - altezza_tooltip))


    def push(self) -> bool:
        if self.toggled and self.tipologia == "push":
            self.toggled = False
            return True
        return False



class Entrata:
    def __init__(self, key, parametri_locali_elementi: list, font_locale: dict[str, Font], w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, text: str = "Prova", titolo = "", visibile: bool = True, color_text: tuple[int] = (200, 200, 200), bg_toggled: tuple[int] = [10, 15, 15], contorno: tuple[int] = [100, 100, 100], contorno_toggled: tuple[int] = [100, 255, 255], color_puntatore: tuple[int] = [255, 255, 255], text_toggled: tuple[int] = (84,160,134)) -> None:
        
        self.key = key 

        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.text_prec: str = text
        self.text: str = text
        self.titolo: str = titolo
        self.tooltip = "Tooltip."
        
        self.bg: tuple[int] = bg
        self.bg_toggled: tuple[int] = bg_toggled
        self.color_text: tuple[int] = color_text
        self.color_text_toggled: tuple[int] = text_toggled
        self.contorno: tuple[int] = contorno
        self.contorno_toggled: tuple[int] = contorno_toggled
        self.color_puntatore: tuple[int] = color_puntatore

        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.toggle = False

        self.hover = False
        self.dt_hover = 0


        self.puntatore: int = len(self.text)
        self.dt_animazione: int = 0 

        self.visibile = visibile

        self.font_locale: Font = font_locale["piccolo"]
        self.font_tooltip: Font = font_locale["piccolo"]


    @property
    def text_invio(self):
        if not self.toggle:
            if self.text_prec != self.text:
                self.text_prec = self.text
        return self.text_prec


    def disegnami(self, logica: Logica):    

        if self.visibile:

            colore_sfondo = np.array(self.bg_toggled) if self.toggle else np.array(self.bg) 
            colore_testo = self.color_text_toggled if self.toggle else self.color_text 

            if self.hover:
                colore_sfondo += np.array([50, 50, 50])

            # calcolo forma
            colore_secondario = self.contorno_toggled if self.toggle else self.contorno
            pygame.draw.rect(self.screen, colore_secondario, [self.x-1, self.y-1, self.w+2, self.h+2])
            pygame.draw.rect(self.screen, colore_sfondo, [self.x, self.y, self.w, self.h])

            # calcolo scritta
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.text}", True, colore_testo), (self.x + self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

            # calcolo nome
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, colore_testo), (self.x - len(self.titolo + " ") * self.font_locale.font_pixel_dim[0], self.y + self.h//2 - self.font_locale.font_pixel_dim[1] // 2))

            if self.toggle and self.dt_animazione % 2 == 0:
                pygame.draw.rect(self.screen, self.color_puntatore, [self.x + self.font_locale.font_pixel_dim[0] * (self.puntatore + .5) + 2, self.y, 2, self.h])


    def hover_update(self, logica: Logica) -> None:
        if self.bounding_box.collidepoint(logica.mouse_pos) and self.visibile:
            self.hover = True
            self.dt_hover += logica.dt
        else:
            self.hover = False
            self.dt_hover = 0

        if self.dt_hover > 1000:

            elenco = self.tooltip.split("\n")
            linee = len(elenco)
            max_larghezza = max([len(linea) for linea in elenco])
            
            altezza_tooltip = (linee + 1) * self.font_tooltip.font_pixel_dim[1]

            pygame.draw.rect(self.screen, self.bg, [logica.mouse_pos[0] - 150, logica.mouse_pos[1] - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2), altezza_tooltip])
            pygame.draw.rect(self.screen, [100, 100, 100], [logica.mouse_pos[0] - 150 - 1, logica.mouse_pos[1] - 1 - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2) + 1, altezza_tooltip + 1], 1)
            
            for linea in range(linee):             
                self.screen.blit(self.font_tooltip.font_tipo.render(f"{elenco[linea]}", True, self.color_text), (logica.mouse_pos[0] - 150 + self.font_tooltip.font_pixel_dim[0], logica.mouse_pos[1] + self.font_tooltip.font_pixel_dim[1] * (linea + 0.5) - altezza_tooltip))


    def selezionato_ent(self, event, key=""):
            
            if key == self.key:
                if self.visibile:
                    self.toggle = True
                    self.puntatore = len(self.text)

            elif key != "":
                if self.toggle:
                    self.toggle = False

            elif key == "":
                if self.bounding_box.collidepoint(event.pos) and self.visibile:
                    if self.toggle:
                        self.toggle = False
                    else:
                        self.toggle = True
                        self.puntatore = len(self.text)
                else:
                    self.toggle = False

    # def completamento_testo(path, entrata):
    #     if type(path) == str:
    #         possibili_file = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)) and file.startswith(entrata.txt)]
    #     elif type(path) == dict:
    #         possibili_file = [i for i in path if i.startswith(entrata.txt)]

    #     if event.type == pygame.TEXTINPUT and entrata.collisione:
    #         try:
    #             entrata.subtext = possibili_file[0]
    #         except IndexError:
    #             pass

    #     if keys[pygame.K_TAB] and entrata.collisione:
    #         ultimo_file = entrata.subtext
    #         if ultimo_file in possibili_file:
    #             indice = possibili_file.index(ultimo_file) + 1
    #             if indice == len(possibili_file):
    #                 indice = 0
    #         else:
    #             indice = 0
    #         try:
    #             entrata.subtext = possibili_file[indice]
    #         except IndexError:
    #             pass

    #     if keys[pygame.K_RETURN] and entrata.collisione:
    #         entrata.txt = entrata.subtext

    def __str__(self) -> str:
        return f"{self.text}"
    


class Path:
    def __init__(self, key, parametri_locali_elementi: list, font_locale: dict[str, Font], w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), tipologia="folder", renderizza_bg: bool = True, text: str = "Prova", titolo = "", visibile: bool = True, color_text: tuple[int] = (200, 200, 200), contorno: tuple[int] = [100, 100, 100]) -> None:
        
        self.key = key 

        self.offset: int = parametri_locali_elementi[1]

        self.tipologia = tipologia

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.text: str = text
        self.visualizza_text: str = text
        self.titolo: str = titolo
        self.tooltip = "Tooltip."
        
        self.execute_action = False
        
        self.bg: tuple[int] = bg
        self.color_text: tuple[int] = color_text
        self.contorno: tuple[int] = contorno
        
        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.hover = False
        self.dt_hover = 0

        self.visibile = visibile

        self.font_locale: Font = font_locale["piccolo"]
        self.font_tooltip: Font = font_locale["piccolo"]


    def search(self, event):
        match self.tipologia:
            case "folder":
                self.search_folder(event)
            case "file":
                self.search_file(event)


    def search_folder(self, event):
        if self.bounding_box.collidepoint(event.pos) and self.visibile:
            self.text = filedialog.askdirectory(initialdir=".", title="Selezione cartella di lavoro")
            lunghezza = len(self.text)

            numero_caratteri = int(self.w / self.font_locale.font_pixel_dim[0])

            if lunghezza > numero_caratteri:
                self.visualizza_text = "..." + self.text[- (numero_caratteri - 4):]
            else: 
                self.visualizza_text = self.text

            self.execute_action = True
    
    
    def search_file(self, event):
        if self.bounding_box.collidepoint(event.pos) and self.visibile:
            self.text = filedialog.askopenfilename(initialdir=".", title="Selezione file")
            lunghezza = len(self.text)

            numero_caratteri = int(self.w / self.font_locale.font_pixel_dim[0])

            if lunghezza > numero_caratteri:
                self.visualizza_text = "..." + self.text[- (numero_caratteri - 4):]
            else: 
                self.visualizza_text = self.text

            self.execute_action = True

    
    @staticmethod
    def save(start_path: str, extension: str = ".png"):
        path = filedialog.asksaveasfilename(initialdir=start_path, title="Salva file", defaultextension=extension)
        return path


    def disegnami(self, logica: Logica):    

        if self.visibile:

            colore_sfondo = np.array(self.bg) 

            if self.hover:
                colore_sfondo += np.array([50, 50, 50])

            # calcolo forma
            colore_secondario = self.contorno
            pygame.draw.rect(self.screen, colore_secondario, [self.x-1, self.y-1, self.w+2, self.h+2])
            pygame.draw.rect(self.screen, colore_sfondo, [self.x, self.y, self.w, self.h])

            # calcolo scritta
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.visualizza_text}", True, self.color_text), (self.x + self.font_locale.font_pixel_dim[0] // 2, self.y + self.h // 2 - self.font_locale.font_pixel_dim[1] // 2))

            # calcolo nome
            self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, self.color_text), (self.x - len(self.titolo + " ") * self.font_locale.font_pixel_dim[0], self.y + self.h//2 - self.font_locale.font_pixel_dim[1] // 2))


    def hover_update(self, logica: Logica) -> None:
        if self.bounding_box.collidepoint(logica.mouse_pos) and self.visibile:
            self.hover = True
            self.dt_hover += logica.dt
        else:
            self.hover = False
            self.dt_hover = 0

        if self.dt_hover > 1000:

            elenco = self.tooltip.split("\n")
            linee = len(elenco)
            max_larghezza = max([len(linea) for linea in elenco])
            
            altezza_tooltip = (linee + 1) * self.font_tooltip.font_pixel_dim[1]

            pygame.draw.rect(self.screen, self.bg, [logica.mouse_pos[0] - 150, logica.mouse_pos[1] - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2), altezza_tooltip])
            pygame.draw.rect(self.screen, [100, 100, 100], [logica.mouse_pos[0] - 150 - 1, logica.mouse_pos[1] - 1 - altezza_tooltip, self.font_tooltip.font_pixel_dim[0] * (max_larghezza + 2) + 1, altezza_tooltip + 1], 1)
            
            for linea in range(linee):             
                self.screen.blit(self.font_tooltip.font_tipo.render(f"{elenco[linea]}", True, self.color_text), (logica.mouse_pos[0] - 150 + self.font_tooltip.font_pixel_dim[0], logica.mouse_pos[1] + self.font_tooltip.font_pixel_dim[1] * (linea + 0.5) - altezza_tooltip))


    def __str__(self) -> str:
        return f"{self.text}"



class ScrollConsole:
    def __init__(self, parametri_locali_elementi: list, font_locale: dict[str, Font], w: float = 50, h: float = 50, x: float = 0, y: float = 0, bg: tuple[int] = (40, 40, 40), renderizza_bg: bool = True, titolo: str = "Default scroll", color_text: tuple[int] = (200, 200, 200), colore_selezionato: tuple[int] = [42, 80, 67], titolo_colore: tuple[int] = (150, 150, 150), cambio_ordine: bool = True, all_on: bool = False) -> None:
        self.offset: int = parametri_locali_elementi[1]

        self.moltiplicatore_x: int = parametri_locali_elementi[2]
        self.ori_y: int = parametri_locali_elementi[3]
        
        self.w: float = self.moltiplicatore_x * w / 100
        self.h: float = self.ori_y * h / 100
        self.x: float = self.moltiplicatore_x * x / 100 + self.offset
        self.y: float = self.ori_y * y / 100

        self.bg: tuple[int] = bg
        self.color_text: tuple[int] = color_text
        self.colore_selezionato: tuple[int] = colore_selezionato
        self.titolo_colore: tuple[int] = titolo_colore

        self.bg_alteranto1 = np.array(self.bg) + 10
        self.bg_alteranto1[self.bg_alteranto1 > 255] = 255
        self.bg_alteranto2 = np.array(self.bg) + 15
        self.bg_alteranto2[self.bg_alteranto2 > 255] = 255
        
        self.screen: pygame.Surface = parametri_locali_elementi[0]
        self.bounding_box = pygame.Rect(self.x, self.y, self.w, self.h)

        self.bottoni_foo: dict[str, Button] = {}

        self.font_locale: Font = font_locale["piccolo"]

        self.titolo: str = titolo
        
        self.elementi: list[str] = [f"-                                          " for _ in range(5)]
        self.indici: list[int] = [i for i in range(5)]
        self.elementi_attivi: list[bool] = [False for i in range(5)]
        
        self.first_item: int = 0
        self.scroll_item_selected: int = 0

        self.cambio_ordine = cambio_ordine
        self.all_on = all_on

        for i in range(5):
            self.bottoni_foo[f"attiva_{i}"] = Button(
                parametri_locali_elementi, 
                font_locale, 
                x=x + w * 0.9,
                y=y + h * 0.28 + 2.125 * i,
                w=1,
                h=1.8,
                text=f"a",
                toggled=self.all_on
            )

        self.bottoni_foo["su"] = Button(
                parametri_locali_elementi, 
                font_locale, 
                x=x + w * 1.05,
                # y=y + 3 + (- self.ori_y * (self.cambio_ordine - 1)),
                y=y + 3,
                w=1.5,
                h=6,
                text=f"su",
                tipologia="push"
            )
    
        self.bottoni_foo["giu"] = Button(
                parametri_locali_elementi, 
                font_locale, 
                x=x + w * 1.05,
                # y=y + 9.45 + (- self.ori_y * (self.cambio_ordine - 1)),
                y=y + 9.45,
                w=1.5,
                h=6,
                text=f"giù",
                tipologia="push"
            )

        # batched data
        self.pos_elementi_bb: list[pygame.Rect] = [pygame.Rect([
            self.x + 3 * self.font_locale.font_pixel_dim[0] // 2, 
            self.y + self.font_locale.font_pixel_dim[1] * 3.25 + index * (self.h - self.font_locale.font_pixel_dim[1] * 4) / 5, 
            len(elemento) * self.font_locale.font_pixel_dim[0], 
            self.font_locale.font_pixel_dim[1] * 1.5]) 
            for index, elemento in enumerate(self.elementi[self.first_item : self.first_item + 5])]

        self.pos_elementi: list[tuple[float]] = [(
            self.x + 4 * self.font_locale.font_pixel_dim[0] // 2, 
            self.y + self.font_locale.font_pixel_dim[1] * 3.5 + index * (self.h - self.font_locale.font_pixel_dim[1] * 4) / 5) 
            for index in range(len(self.elementi[self.first_item : self.first_item + 5]))]


    def disegnami(self, logica: Logica):

        # calcolo forma
        pygame.draw.rect(self.screen, self.bg, [self.x, self.y, self.w, self.h], border_top_left_radius=10, border_bottom_right_radius=10)

        # calcolo box titolo
        pygame.draw.rect(self.screen, np.array(self.bg) + 10, [self.x, self.y, self.font_locale.font_pixel_dim[0] * (len(self.titolo) + 4), self.font_locale.font_pixel_dim[1] * 2], border_top_left_radius=10, border_bottom_right_radius=10)
        self.screen.blit(self.font_locale.font_tipo.render(f"{self.titolo}", True, self.titolo_colore), (self.x + 3 * self.font_locale.font_pixel_dim[0] // 2, self.y + self.font_locale.font_pixel_dim[1] - self.font_locale.font_pixel_dim[1] // 2))

        # calcolo scritta elementi
        for index, elemento in enumerate(self.elementi[self.first_item : self.first_item + 5]):
            colore_alternato = self.bg_alteranto1 if index % 2 == 0 else self.bg_alteranto2
            if index == self.scroll_item_selected: colore_alternato = self.colore_selezionato
            
            pygame.draw.rect(self.screen, colore_alternato, self.pos_elementi_bb[index])
            self.screen.blit(self.font_locale.font_tipo.render(f"{elemento}", True, self.color_text), self.pos_elementi[index])

        for index, elemento in self.bottoni_foo.items():
            elemento.disegnami()


    def selezionato_scr(self, event, logica: Logica):
        
        # gestito movimento con le freccie e lo spostamento presso i limiti (0 e 5)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.aggiorna_externo("up", logica)
            if event.key == pygame.K_DOWN:
                self.aggiorna_externo("down", logica)

            # aggiorna valore tasti di accensione (non importa dove faccio il test, tanto su e giù saranno sempre gli ultimi)
            for bottone_elemento, stato in zip(self.bottoni_foo.items(), self.elementi_attivi[self.first_item : self.first_item+5]):
                if bottone_elemento[0].startswith("attiva_"):
                    bottone = bottone_elemento[1]
                    bottone.toggled = stato


        # gestito selezione con il mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, test_pos in enumerate(self.pos_elementi_bb):
                    if test_pos.collidepoint(logica.mouse_pos) and index < len(self.elementi):
                        self.scroll_item_selected = index
                        logica.aggiorna_plot = True
        

        # gestito selezione con il mouse di "Accensione" e update della variabile stato "elementi_attivi". Inoltre seleziona la barra corrispondente
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                indice_cliccato = [(index, element[0]) for index, element in zip(range(len(self.bottoni_foo)), self.bottoni_foo.items()) if element[1].selezionato_bot(event) and element[0].startswith("attiva_")]
                if len(indice_cliccato) > 0:
                    self.elementi_attivi[indice_cliccato[0][0] + self.first_item] = self.bottoni_foo[indice_cliccato[0][1]].toggled
                    self.scroll_item_selected = indice_cliccato[0][0]
                    logica.aggiorna_plot = True

        
        if self.bottoni_foo["su"].push():
            if self.scroll_item_selected + self.first_item > 0:
                self.elementi[self.scroll_item_selected + self.first_item - 1], self.elementi[self.scroll_item_selected + self.first_item] = self.elementi[self.scroll_item_selected + self.first_item], self.elementi[self.scroll_item_selected + self.first_item - 1] 
                self.indici[self.scroll_item_selected + self.first_item - 1], self.indici[self.scroll_item_selected + self.first_item] = self.indici[self.scroll_item_selected + self.first_item], self.indici[self.scroll_item_selected + self.first_item - 1] 
                self.elementi_attivi[self.scroll_item_selected + self.first_item - 1], self.elementi_attivi[self.scroll_item_selected + self.first_item] = self.elementi_attivi[self.scroll_item_selected + self.first_item], self.elementi_attivi[self.scroll_item_selected + self.first_item - 1] 
                self.aggiorna_externo(index="up", logica=logica)
                # aggiorna valore tasti di accensione (non importa dove faccio il test, tanto su e giù saranno sempre gli ultimi)
                for bottone_elemento, stato in zip(self.bottoni_foo.items(), self.elementi_attivi[self.first_item : self.first_item+5]):
                    if bottone_elemento[0].startswith("attiva_"):
                        bottone = bottone_elemento[1]
                        bottone.toggled = stato

        
        if self.bottoni_foo["giu"].push():
            if self.scroll_item_selected + self.first_item < len(self.elementi) - 1:
                self.elementi[self.scroll_item_selected + self.first_item + 1], self.elementi[self.scroll_item_selected + self.first_item] = self.elementi[self.scroll_item_selected + self.first_item], self.elementi[self.scroll_item_selected + self.first_item + 1]
                self.indici[self.scroll_item_selected + self.first_item + 1], self.indici[self.scroll_item_selected + self.first_item] = self.indici[self.scroll_item_selected + self.first_item], self.indici[self.scroll_item_selected + self.first_item + 1]
                self.elementi_attivi[self.scroll_item_selected + self.first_item + 1], self.elementi_attivi[self.scroll_item_selected + self.first_item] = self.elementi_attivi[self.scroll_item_selected + self.first_item], self.elementi_attivi[self.scroll_item_selected + self.first_item + 1] 
                self.aggiorna_externo(index="down", logica=logica)
                # aggiorna valore tasti di accensione (non importa dove faccio il test, tanto su e giù saranno sempre gli ultimi)
                for bottone_elemento, stato in zip(self.bottoni_foo.items(), self.elementi_attivi[self.first_item : self.first_item+5]):
                    if bottone_elemento[0].startswith("attiva_"):
                        bottone = bottone_elemento[1]
                        bottone.toggled = stato


    def aggiorna_externo(self, index: str, logica: Logica = None):

        match index:
            case "up":
                if self.scroll_item_selected > 0: 
                    self.scroll_item_selected -= 1 
                elif self.first_item > 0:
                    self.first_item -= 1

            case "down":
                if self.scroll_item_selected < 4: 
                    self.scroll_item_selected += 1 
                elif self.first_item < len(self.elementi) - 5:
                    self.first_item += 1

            case "reload":
                self.scroll_item_selected = 0
                self.first_item = 0
                self.indici = [i for i in range(len(self.elementi))]
                self.elementi_attivi = [self.all_on for i in range(len(self.elementi))]
                for index, bottone in self.bottoni_foo.items():
                    if index.startswith("attiva_"):
                        bottone.toggled = self.all_on

            case _:
                pass

        if not logica is None: 
            logica.aggiorna_plot = True


    def update_elements(self):
        
        n_elementi = len(self.elementi)
        
        if self.cambio_ordine:
            if n_elementi > 5:
                self.bottoni_foo["su"].visibile = False
                self.bottoni_foo["giu"].visibile = False
            else:
                self.bottoni_foo["su"].visibile = True
                self.bottoni_foo["giu"].visibile = True

        for i, bottone in enumerate(self.bottoni_foo.items()):
            if i < len(self.elementi):
                bottone[1].visibile = True
            else:
                bottone[1].visibile = False



class MultiBox:
    def __init__(self, bottoni: list[Button]) -> None:
        self.elementi = bottoni

    def calcola_bb(self):

        min_x = np.inf
        min_y = np.inf
        max_x = - np.inf
        max_y = - np.inf

        for elemento in self.elementi:
            min_x = min(min_x, elemento.bounding_box[0])
            min_y = min(min_y, elemento.bounding_box[1])

            max_x = max(max_x, elemento.bounding_box[0] + elemento.bounding_box[2])
            max_y = max(max_y, elemento.bounding_box[1] + elemento.bounding_box[3])
                    
        max_x -= min_x
        max_y -= min_y

        self.BBB = pygame.rect.Rect(min_x, min_y, max_x, max_y)
    

    def selezionato_mul(self, event):
        
        self.calcola_bb()

        if self.BBB.collidepoint(event.pos):
            for elemento in self.elementi:
                if elemento.bounding_box.collidepoint(event.pos):
                    if elemento.toggled:
                        elemento.toggled = False
                    else:
                        elemento.toggled = True
                        elemento.animation = True
                        elemento.tracker = 0
                else:
                    elemento.toggled = False



class TabUI:
    def __init__(self, name: str = "Test TabUI", renderizza: bool = True, abilita: bool = True, bottoni: list[Button] = None, entrate: list[Entrata] = None, scroll_consoles: list[ScrollConsole] = None, ui_signs: list[UI_signs] = None, multi_boxes: list[MultiBox] = None, labels: list[LabelText] = None, paths: list[Path] = None) -> None:
        
        self.name = name

        self.bottoni = bottoni
        self.entrate = entrate
        self.scroll_consoles = scroll_consoles
        self.ui_signs = ui_signs
        self.multi_boxes = multi_boxes
        self.labels = labels
        self.paths = paths

        self.renderizza = renderizza
        self.abilita = abilita

    
    def aggiorna_tab(self, event, logica):
        if self.abilita:
            if not self.bottoni is None: [elemento.selezionato_bot(event) for elemento in self.bottoni]
            if not self.entrate is None: [elemento.selezionato_ent(event) for elemento in self.entrate]
            if not self.multi_boxes is None: [mult_box.selezionato_mul(event) for mult_box in self.multi_boxes]
            if not self.scroll_consoles is None: [scrolla.selezionato_scr(event, logica) for scrolla in self.scroll_consoles]

            if not self.paths is None: [elemento.search(event) for elemento in self.paths]


    def hover_update(self, logica): 
        if self.abilita:
            if not self.bottoni is None: [elemento.hover_update(logica) for elemento in self.bottoni]
            if not self.entrate is None: [elemento.hover_update(logica) for elemento in self.entrate]
            if not self.paths is None: [elemento.hover_update(logica) for elemento in self.paths]


    def disegna_tab(self, logica):

        if self.renderizza:
            if not self.ui_signs is None: [segno.disegnami() for segno in self.ui_signs]
            if not self.labels is None: [label.disegnami() for label in self.labels]
            if not self.bottoni is None: [bottone.disegnami() for bottone in self.bottoni]
            if not self.entrate is None: [entrata.disegnami(logica) for entrata in self.entrate]
            if not self.paths is None: [path.disegnami(logica) for path in self.paths]
            if not self.scroll_consoles is None: [scrolla.disegnami(logica) for scrolla in self.scroll_consoles]

        self.hover_update(logica)


    def __str__(self) -> str:
        return self.name



class Schermo:
    def __init__(self, parametri_locali_elementi: list, w: float = None, h: float = None, x: float = None, y: float = None, default: bool = True, toggled: bool = True) -> None:

        if default:
            self.w: int = int(parametri_locali_elementi[3] * 0.9)
            self.h: int = int(parametri_locali_elementi[3] * 0.9)
            self.ancoraggio_x: int = parametri_locali_elementi[3] * 0.05 + parametri_locali_elementi[1]
            self.ancoraggio_y: int = parametri_locali_elementi[3] * 0.05

        else:
            self.w: int = int(w * parametri_locali_elementi[2] / 100)
            self.h: int = int(h * parametri_locali_elementi[3] / 100)
            self.ancoraggio_x: int = int(x * parametri_locali_elementi[2] / 100 + parametri_locali_elementi[1])
            self.ancoraggio_y: int = int(y * parametri_locali_elementi[3] / 100)


        self.shift_x = parametri_locali_elementi[1]

        self.madre: pygame.Surface = parametri_locali_elementi[0]

        self.buffer: np.ndarray = np.zeros((self.w, self.h, 3))
        self.bg: tuple[int] = (40, 40, 40)

        self.toggled = toggled

        self.schermo: pygame.Surface = pygame.Surface((self.w, self.h))

    
    def aggiorna_schermo(self) -> None:
        """
        Incolla lo schermo allo schermo madre (originale)
        """
        if self.toggled:
            self.madre.blit(self.schermo, (self.ancoraggio_x, self.ancoraggio_y))
