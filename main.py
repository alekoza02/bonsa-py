import cProfile
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame.locals import *
import pygame
import configparser
    
def main(config: configparser):
    
    _debug_mesh_grid = eval(config.get('Default', 'debug_mesh_grid'))
    _debug_mesh_axis = eval(config.get('Default', 'debug_mesh_axis'))

    from _modulo_UI import UI, Logica
    from _modulo_RENDERER import Camera, PointCloud, DebugMesh, Renderer
    from _modulo_CRESCITA import Albero
    from _modulo_COMUNICAZIONE import Converter

    app = UI(config)

    scena = app.scena["main"]

    logica = Logica()
    albero = Albero()
    camera = Camera()
    convertitore = Converter()
    renderer = Renderer(scena.schermo["viewport"])

    point_cloud = PointCloud(None)
    
    # assi e griglie
    debug_mesh = DebugMesh()
    
    while app.running:

        # impostazione inizio giro
        app.start_cycle(logica) 

        # eventi
        eventi_in_corso = pygame.event.get()
        app.event_manager(eventi_in_corso, logica)

        # disegno i labels
        scena.disegnami_tabs_version(logica)

        # calcolo parametri camera
        camera, logica = renderer.camera_setup(camera, logica)
        
        # logica patre
        if scena.bottoni["simula"].toggled:
            ris_crescita = albero.crescita()
    
        if scena.bottoni["ren_mode"].toggled:
            convertitore.new_values(ris_crescita[0] / 10, ris_crescita[1].astype(int), ris_crescita[2])

            point_cloud.verteces_ori = convertitore.rotate_prisms()
            point_cloud.links = convertitore.stack_links()
        else:
            point_cloud.verteces_ori = ris_crescita[0] / 10
            point_cloud.links = ris_crescita[1].astype(int)

        # messaggi di debug
        scena.label_text["debug1"].text = albero.mess1
        scena.label_text["debug2"].text = albero.mess2
        scena.label_text["debug3"].text = albero.mess3
        scena.label_text["debug4"].text = albero.mess4
        scena.label_text["debug5"].text = albero.mess5
        
        # disegno realtà aumentata
        debug_mesh.scelta_debug(_debug_mesh_grid, _debug_mesh_axis)
        renderer.renderizza_debug_mesh(debug_mesh, camera, logica)
        
        # disegno punti
        renderer.renderizza_point_cloud(point_cloud, camera, logica, linked=True, points_draw=True)

        # controllo di uscita dal programma ed eventuale aggiornamento dello schermo
        app.mouse_icon(logica)   # lanciato due volte per evitare flickering a bassi FPS
        app.aggiornamento_e_uscita_check()
        
    renderer.lib.free_array(renderer.c_array)

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
    print(f"Finito in {time.time() - start:.0f}s")
    
    if _profiler:
        profiler.disable()
        profiler.dump_stats('PROFILATORE/_prof.prof')
