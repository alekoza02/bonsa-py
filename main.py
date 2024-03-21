import cProfile
from pygame.locals import *
import pygame

def main():

    from _modulo_UI import UI, Logica
    from _modulo_MATE import Camera, PointCloud, DebugMesh, Importer, Modello, Mate
    from _modulo_CRESCITA import Crescita
    
    ui = UI()
    logica = Logica()
    crescita = Crescita()
    camera = Camera()

    # import modello di prova    
    importer = Importer(True, False)
    path_modello = "MODELS/m_bonsai.obj"
    importer.modello(path_modello)
    
    # cloud mesh di prova
    modello = Modello(importer.verteces, importer.links, Mate.normale_tri_buffer(importer.verteces, importer.links))
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
                    if event.button == 1:
                        logica.dragging = True
                        logica.dragging_end_pos = logica.mouse_pos

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: 
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
        # set messaggi debug
        logica.messaggio_debug1 = f"FPS : {ui.current_fps:.2f}"
        logica.messaggio_debug2 = f"Numero di vertici : {len(modello.verteces_ori)}"
        logica.messaggio_debug3 = f"Path modello : {path_modello}"
        logica.messaggio_debug4 = f"Cam pos : {camera.pos[0]:.1f}, {camera.pos[1]:.1f}, {camera.pos[2]:.1f}"
        logica.messaggio_debug5 = f"Cam rot : {camera.becche:.1f}, {camera.rollio:.1f}, {camera.imbard:.1f}"
        
        ui.aggiorna_messaggi_debug(logica)
        
        # disegno i labels
        [label.disegnami() for indice, label in ui.scena["main"].label_text.items()]
        
        # disegno la viewport
        ui.scena["main"].schermo["viewport"].disegnami()
        
        # calcolo parametri camera
        camera = ui.scena["main"].schermo["viewport"].camera_setup(camera, logica)
        
        # logica patre
        # point_cloud.verteces_ori = crescita.ciclo_principale()
        
        # disegno realtà aumentata
        debug_mesh.scelta_debug(True, True)
        ui.scena["main"].schermo["viewport"].renderizza_debug_mesh(debug_mesh, camera)
        
        # disegno punti
        ui.scena["main"].schermo["viewport"].renderizza_modello(modello, camera, logica, wireframe=True)
        ui.scena["main"].schermo["viewport"].renderizza_point_cloud(point_cloud, camera, logica)
        # UI ----------------------------------------------------------------

        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()
        
if __name__ == "__main__":
    
    active_profile = False
    
    if active_profile:
        profiler = cProfile.Profile()
        profiler.enable()

    import time
    start = time.time()
    main()
    print(f"Finito in {time.time() - start}")
    
    if active_profile:
        profiler.disable()
        profiler.dump_stats('PROFILATORE/_prof.prof')
