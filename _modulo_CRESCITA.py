import numpy as np
import time
import random

class Albero:
    def __init__(self) -> None:
        self.data = np.array([1,2,3])


if __name__ == '__main__':
    albero = Albero()




def main_cresc(punti_multi, collegamenti, uscita, numero_rami,spessori_rami, debug, gaussiana_std, gaussiana_mean):

    # DEFINIZIONE VARIABILI

    # spessore iniziale rami nuovi
    spess_iniz = .2
    
    # nodi è un array numpy di tre float (coord x --> C_X, coord y --> C_Y, coord z --> C_Z)
    nodi = np.array([[0.,0.,0.],[0.,0.,1.]])
    C_X, C_Y, C_Z = 0,1,2
    C_ALTEZZA_DAL_SUOLO=C_Z # alias parlante

    
    # rami è un array di 
    #   - 1 intero (indice nodo di origine) --> C_ORIG
    #   - 1 intero (indice nodo di destinazione) --> C_DEST
    #   - 1 intero (ordine del ramo: primario, secondario, ecc...) --> C_ORDINE
    #   - 1 float (spessore) --> C_SPESS

    C_ORIG,C_DEST,C_ORDINE,C_SPESS = 0,1,2,3

    # Segmento di partenza
    rami = np.array([[0,1,1,spess_iniz]])
    
    
    ####  IMPOSTAZIONI DI CRESCITA  ####
    # crescita in altezza
    global crescita_a
    crescita_a = .05
    # crescita in larghezza
    global crescita_l
    crescita_l = .0001
    # tendenza verso l'alto dei rami nuovi
    global alto
    alto = .0002
    # massima variazione di angolo iniziale rispetto al ramo padre
    #angolo_iniziale = np.pi/8
    # simmetria (gemma doppia)
    simmetria = True

    # stringa di debug nella ui
    frase = ''

    iterazioni = 0

    while uscita.value == 0:

        ''' TODO
        - spawn rami secondari su rami vecchi (prima delle biforcazioni)
        - diminuire spawn in zone affollate 
        - scrivere routine morte ramo basso
        - generare posizione/orientamento foglie e chiedere ad Ale di visualizzarle
        - orientare le gemme alla nascita del nodo successivo
        '''

        
        
        iterazioni += 1

        # debug contiene una stringa da far visualizzare nella gui (frase viene valorizzata più avanti)
        debug.value = frase.encode("utf-8")

        if len(rami) > 2000:
            return


        # STEP 1 - CRESCITA IN LARGHEZZA

        # Tutti i segmenti crescono in larghezza ad ogni ciclo
        rami[:,C_SPESS] += crescita_l

        # STEP 2 - ALLUNGAMENTO RAMI TERMINALI  (quelli di lunghezza inferiore a 10)

        # costruzione array lunghezze dei rami (a_lung) e allungamenti (a_allu)
        a_lung,a_allu = ricalcolo_array_allu(nodi,rami)
 
        # allungo rami con lunghezza < 10
        nodi[rami[a_lung < 10,C_DEST].astype(np.int32)] += a_allu[a_lung < 10]


        # STEP 3 - CREAZIONE NUOVI RAMI TERMINALI
        #  Creazione nuovi rami che sono la prosecuzione dei rami terminali
        #  I requisiti per far iniziare un nuovo ramo sono: lunghezza ramo padre > 10 e numero gemme = 0 
        a_filtro, a_rand = calcolo_prosecuzione_rami(rami, a_lung)
        
        # Se le condizioni di spawn nuovi rami esistono almeno per un nodo, creo il nuovo ramo
        if a_filtro.any():

            # 3.1) NUOVI NODI
            # L'array dei nuovi nodi è composto da tutti i nodi che devono gemmare 
            # ai quali sommo gli allungamenti del ramo precedente (prosecuzione)
            # e un fattore casuale sulle coordinate x e y (z è fissa = "alto")

            # Estendo array degli allungamenti per applicarlo ai nodi (nodi=rami+1)
            a_allu_esteso = np.vstack((np.array([[0.,0.,0.]]),a_allu))

            # Creo i nuovi nodi
            nuovi_nodi = nodi[ a_filtro ] + a_allu_esteso[a_filtro ] + a_rand[a_filtro ]

            # 3.2) NUOVI RAMI

            a_indici,a_gemme = ricalcolo_array_gemme (rami)
            a_orig = np.array([a_indici[a_filtro]])
            a_dest = np.array([np.arange(len(nodi),len(nodi)+len(nuovi_nodi))])
            a_ordini = np.array(rami[a_indici[a_filtro].astype(int)-1][:,C_ORDINE])
            a_spess = np.full((len(nuovi_nodi)), spess_iniz)

            # Sommo come righe, poi traspongo con T
            nuovi_rami = np.vstack([a_orig,a_dest,a_ordini,a_spess]).T

            # 3.3) APPEND NODI E RAMI CREATI
            nodi=np.vstack((nodi,nuovi_nodi))
            rami=np.vstack((rami,nuovi_rami))


            
        # STEP 4 - GENERAZIONE NUOVI RAMI SECONDARI 

        # Aggiornamento gemme
        a_indici,a_gemme = ricalcolo_array_gemme (rami)

        # Compongo l'array di sequenze di segmenti (rami) che vanno dalle punte alle biforcazioni
        l_rametti=[]
        for nodo in a_indici[a_gemme == 1][1:]:
        
            i_nodo = int(nodo)
            
            # Promemoria
            # Il ramo n è il ramo che ha come destinazione il nodo n+1
            # Il nodo n è la destinazione del ramo n-1

            sequenza=[i_nodo]
            while a_gemme[i_nodo] < 3 and i_nodo > 0:
                i_nodo=int(rami[i_nodo-1,C_ORIG])
                sequenza.append(i_nodo)

            if len(sequenza) > 5:
                l_rametti.append(sequenza)


        if l_rametti:

            ai_nodi_scelti=np.empty(0,dtype=int)

            # scelta del nodo da gemmare
            for l_rametto in l_rametti:
                rand=abs(random.gauss(0,1))
                if rand >= 1:
                    # se troppo grande metto al minimo
                    rand = 0
                else:
                    rand = int(rand*(len(l_rametto)-2))
                
                
                rand=rand+1

                ai_nodi_scelti = np.append(ai_nodi_scelti,l_rametto[rand])

            a_nodi_scelti = nodi[ai_nodi_scelti]            

            # costruzione array lunghezze dei rami (a_lung) e allungamenti (a_allu)
            a_lung,a_allu = ricalcolo_array_allu(nodi,rami)

            # Composizione array dei nodi di origine partendo dai nodi di destinazione
            ai_nodi_prec = rami[ai_nodi_scelti-1][:,C_ORIG].astype(np.int32)
            a_nodi_prec = nodi[ai_nodi_prec]

            # Con nodi di origine e destinazione posso calcolare gli angoli del ramo
            # cart_to_sphere restituisce ro(lunghezza) theta(angolo orizzontale) e phi(angolo verticale)
            a_angoli_oriz_p,a_angoli_vert_p = cart_to_sphere(a_nodi_prec,a_nodi_scelti)[1:]


            # CALCOLO ARRAY ANGOLI ORIZZONTALI 
            # calcolo angoli massimi di deviazione dal padre (dipende dalla verticalità del padre)
            a_est_angoli = a_angoli_vert_p*4
            # estensione massima angolo orizzontale dei figli = angolo verticale del padre * 4 (minimo: pi)
            a_est_angoli[a_est_angoli < np.pi] = np.pi
            # calcolo deviazione random
            a_diff_angoli =  (np.random.random(len(a_angoli_oriz_p))-.5)*a_est_angoli     
            # calcolo angolo finale (angolo orizzontale del padre + deviazione random)
            a_angoli_oriz = a_angoli_oriz_p + a_diff_angoli

            # angoli verticali: da pi/4 a pi/4 + pi/8
            a_angoli_vert = np.random.random(len(a_angoli_vert_p))*np.pi/8 +np.pi/4

            
            a_nuovi_nodi = a_nodi_scelti + np.vstack((
                np.cos(a_angoli_oriz),
                np.sin(a_angoli_oriz),
                np.sin(a_angoli_vert))).T

            # se spawn simmetrico gemmo doppio
            if simmetria:


                # vecchio metodo per angoli dei rami gemelli
                a_angoli_oriz2 = a_angoli_oriz_p - a_diff_angoli

                ################################################################################
                # NUOVO ALGORITMO PER SIMMETRICI: 
                # se debole/media/medio-forte verticalità del padre 
                #       --> stesso angolo verticale del padre
                #       --> angolo orizzontale fisso (es.: +45 e -45 rispetto al padre)
                # se forte verticalità del padre                   
                #       --> angolo verticale fisso (es.: +45 e -45 dal padre)
                #       --> angolo orizzontale: il primo random (e +180), i successivi perpendicolari al precedente 
                # 
                ################################################################################

                #a_angoli_vert = a_angoli_vert_p
                #a_angoli_vert2 = a_angoli_vert_p
                #a_angoli_oriz = a_angoli_oriz_p + np.pi /4
                #a_angoli_oriz2 = a_angoli_oriz_p - np.pi /4
                
                #a_angoli_vert[np.abs(a_angoli_vert_p - np.pi) < .1] = a_angoli_vert_p+np.pi/4
                #a_angoli_vert2[np.abs(a_angoli_vert_p - np.pi) < .1] = a_angoli_vert_p-np.pi/4
                
                #a_angoli_oriz = angoli precedenti +90
                
                
                
                
                
                a_nuovi_nodi2 = a_nodi_scelti + np.vstack((
                    np.cos(a_angoli_oriz2),
                    np.sin(a_angoli_oriz2),
                    np.sin(a_angoli_vert))).T

                a_nuovi_nodi = np.vstack((a_nuovi_nodi,a_nuovi_nodi2))
            

            a_ordini=rami[np.where(np.isin(rami[:,C_DEST],ai_nodi_scelti))][:,C_ORDINE] + 1, 
                
            if simmetria:
                # raddoppio array dei nodi di origine
                ai_nodi_scelti = np.hstack((ai_nodi_scelti,ai_nodi_scelti))
                # raddoppio array degli ordini    
                a_ordini=np.hstack((a_ordini,a_ordini))    
                
            a_nuovi_rami = np.vstack((
                ai_nodi_scelti, 
                np.arange(len(nodi),len(nodi)+len(a_nuovi_nodi)), 
                a_ordini,
                np.full(len(a_nuovi_nodi),spess_iniz))).T

            rami = np.vstack((rami,a_nuovi_rami))
            nodi = np.vstack((nodi,a_nuovi_nodi))
                

        # PROSSIMI STEP -----

        # AGGIUNGERE PIEGAMENTO VERSO IL BASSO NEL TEMPO
        #nodi[1:,C_Z] -= .000001

        frase=f"iter: {iterazioni} nodi: {len(nodi)} H(cm): {int(np.max(nodi[:,2])*.2)}"
                        
        # FINE LOGICA DI CRESCITA---------------------------------------------------------------------------------------
        for i, punto_ciclo in enumerate(nodi):
            punti_multi[i * 3:(i + 1) * 3] = punto_ciclo
        transfer = list(map(int,np.ravel(rami[:,:2])))
        collegamenti[:len(transfer)] = transfer
        numero_rami.value = len(rami)
        spessori_rami[:len(rami)]=rami[:,3]
        time.sleep(.01)



def cart_to_sphere(C1,C2):
    Vettori=C2-C1
    ro = np.sqrt(Vettori[:,0]**2+Vettori[:,1]**2+Vettori[:,2]**2)
    theta = np.arctan2(Vettori[:,1],Vettori[:,0])
    phi = np.arcsin(Vettori[:,2]/ro)
    return ro,theta,phi

def ricalcolo_array_allu(nodi,rami):

    # Questa funzione ricalcola gli array:
    # - a_diff --> differenze di coordinate nodi di inizio e di fine dei rami 
    # - a_lung --> lunghezze dei rami, basandosi sull'array a_diff
    # - a_allu --> allungamenti dei rami, basandosi sugli array a_diff e a_lung

    C_ORIG=0
    C_DEST=1
    C_ORDINE=2
    Z=2 # La coordinata Z è la colonna 2 dell'array nodi

    # array differenze di coordinate
    a_diff=nodi[rami[:,C_DEST].astype(int)]-nodi[rami[:,C_ORIG].astype(int)]
    
    # array lunghezze dei vettori corrispondenti alle coordinate
    a_lung=np.linalg.norm(a_diff,axis=1)

    # array allungamenti
    # a_diff / a_lung --> vettori normalizzati
    # allungamento inversamente proporzionale all'ordine di ramo
    # allungamento proporzionale alla crescita_a (alterazione temporale)
    # allungamento proporzionale all'altezza dal suolo (1/100)

    a_allu = a_diff / a_lung[:,None] / rami[:,C_ORDINE][:,None] * crescita_a
    a_allu *= (1+ nodi[rami[:,C_DEST].astype(int),Z][:,None] /1000) 
    #a_allu[:,2] -= .0001 

    return a_lung,a_allu 

def ricalcolo_array_gemme(rami):

    # Questa funzione ricalcola gli array:
    # - a_indici, a_gemme --> indici dei nodi e gemme dei nodi
    # TODO: forse è il caso di fonderli in un array unico?
 
    C_ORIG=0
    C_DEST=1

    # Conteggio rami collegati ad ogni nodo (conto anche il ramo "padre")
    # Il numero di gemme esatto (se servisse) è n-gemme -1
    #
    # Sommo tutti i nodi che trovo sia come origine che come destinazione
    # fondendo colonne 0 e 1 (C_ORIG e C_DEST)
    # Faccio la unique+return_counts per contarli
    a_indici,a_gemme = np.unique(np.append(rami[:,C_ORIG], rami[:,C_DEST]),return_counts=True)

    return a_indici,a_gemme

def calcolo_prosecuzione_rami(rami, a_lung):

    # Questa funzione calcola gli array:
    # - a_filtro --> filtro da applicare all'array nodi per ottenere quelli senza gemme appartenenti a rami lunghi
    # - a_rand --> array di valori random da applicare alla crescita dei nuovi rami
    # TODO: spostare il calcolo di a_rand fuori da questa funzione? Sembra poco attinente...
 
    C_DEST=1
    global alto

    # Aggiorno il conteggio delle gemme
    a_indici,a_gemme = ricalcolo_array_gemme (rami)

    # Combino le due condizioni:
    # 1) nodi con gemme=1 (array completo di booleani, es.: [ True, False, False, True, ...])
    # 2) nodi terminali di rami lunghi (array parziale di indici di nodi, es.: [ 3, 5, 17] )

    # Array "filtro"  
    a_filtro_gemme = a_gemme == 1

    # Array "filtro" contenente gli indici dei nodi terminali di rami lunghi
    a_filtro_lunghi = rami[a_lung > 10,C_DEST].astype(np.int32)

    # a_filtro_lunghi --> array indici dei nodi teminali di rami lunghi
    # a_filtro_gemme  
    a_filtro = a_filtro_lunghi[a_filtro_gemme[a_filtro_lunghi]]

    # Array di variazione casuale su x e y, mentre su z è fissa (alto)
    a_rand = np.random.uniform(-0.001, 0.001, size=(len(a_gemme), 3))
    a_rand[:, 2] = alto


    #return a_gemme, a_indici, a_filtro, a_rand
    return a_filtro, a_rand


