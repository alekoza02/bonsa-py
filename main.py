if __name__ == "__main__":
    import pygame
    from pygame.locals import *

    from _modulo_UI import UI, Logica
    from _modulo_MATE import Camera, PointCloud, DebugMesh
    
    ui = UI()
    logica = Logica()

    # DEBUGGING SESSION
    camera = Camera()
    
    # cubo di prova
    point_cloud = PointCloud([
        [-1, -1, -1],
        [-1, -1, 1],
        [-1, 1, -1],
        [-1, 1, 1],
        [1, -1, -1],
        [1, -1, 1],
        [1, 1, -1],
        [1, 1, 1],
    ])
    
    debug_mesh = DebugMesh()
    # DEBUGGING SESSION
    
    
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
                logica.ctrl = True if keys[pygame.K_LCTRL] else False
                logica.shift = True if keys[pygame.K_LSHIFT] else False
                

        # UI ----------------------------------------------------------------
        ui.scena["main"].label_text["title"].disegnami()
        ui.scena["main"].schermo["viewport"].disegnami()
        
        camera = ui.scena["main"].schermo["viewport"].camera_setup(camera, logica)
        
        ui.scena["main"].schermo["viewport"].renderizza_point_cloud(point_cloud, camera, logica)
        ui.scena["main"].schermo["viewport"].scelta_debug(True, True)
        ui.scena["main"].schermo["viewport"].renderizza_debug_mesh(debug_mesh, camera)
        # UI ----------------------------------------------------------------

        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        ui.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        ui.aggiornamento_e_uscita_check()