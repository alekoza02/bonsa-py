import cProfile
from pygame.locals import *
import pygame
import configparser
import numpy as np
    
def main(config: configparser):
    
    _tasto_navigazione = int(config.get('Default', 'tasto_navigazione'))
    _modello_or_cloud = config.get('Default', 'modello_or_cloud')
    _modello_default = config.get('Default', 'modello_default')
    _debug_mesh_grid = eval(config.get('Default', 'debug_mesh_grid'))
    _debug_mesh_axis = eval(config.get('Default', 'debug_mesh_axis'))

    from _modulo_UI import UI, Logica
    from _modulo_MATE import Camera, PointCloud, DebugMesh, Importer, Modello, Mate
    from _modulo_CRESCITA import Albero
    
    ui = UI()
    logica = Logica()
    albero = Albero()
    camera = Camera()

    # import modello di prova    
    importer = Importer(True, False)
    path_modello = _modello_default
    importer.modello(path_modello)
    
    if _modello_or_cloud == "modello":
        modello = Modello(importer.verteces, importer.links, Mate.normale_tri_buffer(importer.verteces, importer.links), s_x=5, s_y=5, s_z=5)
    elif _modello_or_cloud == "points":
        point_cloud = PointCloud(importer.verteces)
    
    # assi e griglie
    debug_mesh = DebugMesh()
    
    while ui.running:

        # impostazione inizio giro
        ui.clock.tick(ui.max_fps)
        ui.colora_bg()
        ui.mouse_icon(logica)

        logica.dt += 1
        logica.dragging_dx = 0
        logica.dragging_dy = 0
        logica.mouse_pos = pygame.mouse.get_pos()

        # BLOCCO GESTIONE EVENTI -----------------------------------------------------------------------------
        # raccolta eventi
        eventi_in_corso = pygame.event.get()

        # Stato di tutti i tasti
        keys = pygame.key.get_pressed()

        # scena main UI
        for event in eventi_in_corso:
            # MOUSE
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == _tasto_navigazione:
                    logica.dragging = True
                    logica.dragging_end_pos = logica.mouse_pos
                if event.button == 4:
                    logica.scroll_up += 1
                if event.button == 5:
                    logica.scroll_down += 1

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == _tasto_navigazione: 
                    logica.dragging = False
                    logica.dragging_end_pos = logica.mouse_pos

            if event.type == pygame.MOUSEMOTION:
                if logica.dragging:
                    logica.dragging_start_pos = logica.dragging_end_pos
                    logica.dragging_end_pos = logica.mouse_pos
                    logica.dragging_dx = logica.dragging_end_pos[0] - logica.dragging_start_pos[0]
                    logica.dragging_dy = - logica.dragging_end_pos[1] + logica.dragging_start_pos[1] # sistema di riferimento invertito

        # CONTROLLO TELECAMERA
        logica.ctrl = keys[pygame.K_LCTRL]
        logica.shift = keys[pygame.K_LSHIFT]
                

        # UI ----------------------------------------------------------------
        
        # disegno i labels
        [label.disegnami() for indice, label in ui.scena["main"].label_text.items()]
        
        # disegno la viewport
        ui.scena["main"].schermo["viewport"].disegnami()
        
        # calcolo parametri camera
        camera, logica = ui.scena["main"].schermo["viewport"].camera_setup(camera, logica)
        
        # logica patre
        # ris_crescita = albero.crescita()
        # point_cloud.verteces_ori = ris_crescita[0] / 10
        # point_cloud.links = ris_crescita[1].astype(int)

        # set messaggi debug
        logica.messaggio_debug1 = f"FPS : {ui.current_fps:.2f}"
        # logica.messaggio_debug2 = f"Numero di segmenti : {len(point_cloud.verteces_ori)}"
        # logica.messaggio_debug3 = f"Altezza approssimativa (cm): {int(np.max(point_cloud.verteces_ori))}"
        logica.messaggio_debug4 = f"Cam pos : {camera.pos[0]:.1f}, {camera.pos[1]:.1f}, {camera.pos[2]:.1f}"
        logica.messaggio_debug5 = f"hehehehe"
        
        ui.aggiorna_messaggi_debug(logica)
        
        # disegno realtà aumentata
        debug_mesh.scelta_debug(_debug_mesh_grid, _debug_mesh_axis)
        ui.scena["main"].schermo["viewport"].renderizza_debug_mesh(debug_mesh, camera)
        
        # disegno punti
        if _modello_or_cloud == "modello":
            ui.scena["main"].schermo["viewport"].renderizza_modello(modello, camera, logica, wireframe=True)
            # ui.scena["main"].schermo["viewport"].renderizza_modello_pixel_based(modello, camera, logica)
        elif _modello_or_cloud == "points":
            ui.scena["main"].schermo["viewport"].renderizza_point_cloud(point_cloud, camera, logica, linked=True)
        # UI ----------------------------------------------------------------

        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()
        
if __name__ == "__main__":
    
    config = configparser.ConfigParser()
    config.read('./DATA/settings.ini')
    
    _profiler = eval(config.get('Default', 'profiler'))
    
    if _profiler:
        profiler = cProfile.Profile()
        profiler.enable()

    import time
    start = time.time()
    main(config)
    print(f"Finito in {time.time() - start}")
    
    if _profiler:
        profiler.disable()
        profiler.dump_stats('PROFILATORE/_prof.prof')
