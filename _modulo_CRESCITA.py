import numpy as np
import random

class Albero:
    def __init__(self) -> None:

        # INIZIALIZZAZIONE VARIABILI
    
        # a_nodi è un array numpy (float) 2D di coordinate [x,y,z]
        self.a_nodi = np.array([[0.,0.,0.],[0.,0.,1.]])   # primi due nodi

        # le coordinate possono essere accedute tramite le costanti C_X, C_Y, C_Z:
        self.C_X, self.C_Y, self.C_Z = 0,1,2
        self.C_ALTEZZA_DAL_SUOLO=self.C_Z # alias parlante per la coordinata z 

        # a_segmenti è un array numpy (int) 2D che contiene: 
        #   - indice nodo di origine --> C_ORIG
        #   - indice nodo di destinazione --> C_DEST
        #   - ordine del ramo: 1 (primario), 2 (secondario) , 3 ecc... --> C_ORDINE

        # a_spessori è un array numpy (float) 1D che contiene gli spessori dei segmenti

        # Gli elementi di a_segmenti possono essere acceduti tramite le coordinate:
        self.C_ORIG, self.C_DEST, self.C_ORDINE = 0,1,2

        # Segmento di partenza
        self.a_segmenti = np.array([[0, 1, 1]])
        
        # spessore iniziale segmenti nuovi
        self.C_spess_iniz = .2

        # Spessore del segmento di partenza
        self.a_spessori = np.array([self.C_spess_iniz])


        # Rami è un array numpy che contiene le sequenze di indici dei segmenti che formano rami (e sottorami)
        # self.rami = [[0,1]]


        ####  IMPOSTAZIONI DI CRESCITA  ####
        # crescita in altezza
        self.crescita_a = .2
        # crescita in larghezza
        self.crescita_l = .002
        # tendenza verso l'alto dei rami nuovi
        self.alto = .001
        # tendenza verso il basso dei rami vecchi
        self.basso = -.001
        # massima variazione di angolo iniziale rispetto al ramo padre
        # self.angolo_iniziale = np.pi/8
        # angolo minimo di spawn nuovi rami 
        self.angolo_min_spawn = np.pi/4
        # range massimo per l'angolo di spawn nuovi rami 
        self.angolo_range_spawn = np.pi/4
        
        # simmetria (gemma doppia)  # PREVEDERE SIMMETRIE MULTIPLE? x3 x4 xN ...
        self.simmetria = False

        # interazioni di crescita
        self.iterazioni = 0

        # Messaggi personalizzati nella GUI
        self.mess1 = ""
        self.mess2 = ""
        self.mess3 = ""
        self.mess4 = ""
        self.mess5 = ""


    def crescita(self, render_mode: bool = False):
    # Funzione principale di crescita
    # data_widget è l'oggetto attraverso il quale posso modificare i campi di testo personalizzati
    
        ''' TODO
        - diminuire spawn in zone affollate / aumentare morte rami affollati
        - generare foglie (estetico)
        - modificare la crescita e la direzione di spawn in base alla posizione (rami in ombra)

        - ALBERO --> BONSAI  (potatura)
        '''
        
        self.iterazioni += 1
        self.mess4 = f"iterazioni: {self.iterazioni}"
        self.mess5 = f"segmenti: {len(self.a_segmenti)}"

        # BLOCCO CRESCITA A 30000 SEGMENTI
        if len(self.a_segmenti) > 30000: 
            if render_mode:
                aggiungi_spessori(self)
                return self.a_nodi_v,self.a_segm_v
            else:
                return self.a_nodi,self.a_segmenti

        # STEP 1 - CRESCITA GENERALE DI TUTTI I SEGMENTI

        # Tutti i segmenti crescono in larghezza ad ogni ciclo
        self.a_spessori += self.crescita_l

        # Tendenza dei rami a piegarsi sotto il loro stesso peso # DISABILITATO
        # self.piega_segmento(self.a_segmenti)
        
        # STEP 2 - ALLUNGAMENTO SEGMENTI TERMINALI  
        # Se il segmento ha una lunghezza inferiore a 20 cresce ancora (se è superiore spunta un nuovo segmento)
        # Guardo quanti segmenti terminali (foglie) ci sono nella direzione di crescita.
        # Se sono pochi, cresco poco (segmento molto illuminato)
        # Se sono molti, cresco di più per cercare la luce, ma facilmente nel successivo controllo illuminazione
        # verrà probabilmente eliminato

        # costruzione array lunghezze dei segmenti (a_lung) e allungamenti (a_allu)
        self.a_lung, self.a_allu = self.ricalcolo_array_allu()
 
        # allungo segmenti con lunghezza < 20
        self.a_nodi[self.a_segmenti[self.a_lung < 20,self.C_DEST]] += self.a_allu[self.a_lung < 20]


        # STEP 3 - CREAZIONE NUOVI SEGMENTI TERMINALI
        #  Creazione nuovi segmenti che sono la prosecuzione dei segmenti terminali
        #  I requisiti per far iniziare un nuovo segmento sono: lunghezza ramo padre > 20 e numero gemme = 0 
        a_filtro, a_rand = self.calcolo_prosecuzione_segmenti()
        
        # Se le condizioni di spawn nuovi segmenti esistono almeno per un nodo, creo il nuovo segmento
        if a_filtro.size > 0:

            # 3.1) NUOVI NODI
            # L'array dei nuovi nodi è composto da tutti i nodi che devono gemmare 
            # ai quali sommo gli allungamenti del ramo precedente (prosecuzione)
            # e un fattore casuale sulle coordinate (x e y: casuali, z casuale + un fisso: "alto")

            # Estendo array degli allungamenti per applicarlo ai nodi (nodi=segmenti+1)
            a_allu_esteso = np.vstack((np.array([[0.,0.,0.]]),self.a_allu))
            # Creo i nuovi nodi
            a_nuovi_nodi = self.a_nodi[ a_filtro ] + a_allu_esteso[ a_filtro ] + a_rand[ a_filtro ]

            # 3.2) NUOVI SEGMENTI

            a_indici,a_gemme = self.ricalcolo_array_gemme()
            a_orig = np.array([a_indici[a_filtro]])
            a_dest = np.array([np.arange(len(self.a_nodi),len(self.a_nodi)+len(a_nuovi_nodi))])
            a_ordini = np.array(self.a_segmenti[a_indici[a_filtro]-1][:,self.C_ORDINE])

            # Sommo come righe, poi traspongo con T
            a_nuovi_segmenti = np.vstack([a_orig,a_dest,a_ordini]).T

            # 3.3) NUOVI SPESSORI
            a_nuovi_spessori = np.full((len(a_nuovi_nodi)),self.C_spess_iniz)


            # Aggiunta nuovi nodi a quelli esistenti
            self.a_nodi=np.vstack((self.a_nodi,a_nuovi_nodi))
            # Aggiunta nuovi segmenti a quelli esistenti
            self.a_segmenti=np.vstack((self.a_segmenti,a_nuovi_segmenti))
            # Aggiunta nuovi spessori a quelli esistenti
            self.a_spessori=np.hstack((self.a_spessori,a_nuovi_spessori))

            # 3.4) AGGIORNAMENTO RAMI
            # I nuovi segmenti vanno aggiunti ai rami esistenti (dei quali sono la prosecuzione)
            # e vanno anche aggiunti come nuovi rami (sé stesso e il segmento precedente)            
            #for segmento in nuovi_segmenti:
            #    self.rami = [ ramo+[int(segmento[self.C_DEST])] if int(segmento[self.C_ORIG]) in ramo else ramo for ramo in self.rami ]
            #for segmento in nuovi_segmenti:
            #    self.rami.append(segmento[0:2].tolist())
            
        # STEP 4 - GENERAZIONE NUOVI RAMI SECONDARI 
        # Faccio spuntare nelle zone di ramo spoglie (sequenze di almeno 20 segmenti senza biforcazioni)

        # Aggiornamento gemme
        a_indici,a_gemme = self.ricalcolo_array_gemme()

        # Compongo la lista di sequenze di indici di nodi che vanno dalle punte alle biforcazioni (parti di ramo)
        # (ll_sequenze è una lista di liste di indici di nodi)
        ll_sequenze=[]

        # parto dal nodo 1 (il nodo 0 è la radice)
        for i_nodo in a_indici[a_gemme == 1][1:]:
            
            # Promemoria
            # Il ramo n è il ramo che ha come destinazione il nodo n+1
            # Il nodo n è la destinazione del ramo n-1
            # a_gemme contiene 1 se è un nodo terminale
            # a_gemme contiene 2 se è un nodo non terminale
            # a_gemme contiene 3 se è un nodo con almeno una gemma

            l_sequenza=[i_nodo]
            while a_gemme[i_nodo] < 3 and i_nodo > 0:
                i_nodo=self.a_segmenti[i_nodo-1,self.C_ORIG]
                l_sequenza.append(i_nodo)

            if len(l_sequenza) > 20:
                ll_sequenze.append(l_sequenza)

        if ll_sequenze:

            # Inizializzazione array di indici dei nodi scelti per gemmare
            ai_nodi_scelti=np.empty(0,dtype=int)
            # Inizializzazione array di angoli dei rami secondari precedenti
            a_angoli_rsp=np.empty(0,dtype=float)

            # SCELTA DEL NODO DA GEMMARE

            for l_sequenza in ll_sequenze:
                # numero casuale con distribuzione gaussiana media=0 sigma=1
                # normalizzo da 0-2 a 0-1 (/2)
                rand=abs(random.gauss(0,1))/2
                
                # intrand = random intero da 1 alla lunghezza della sequenza 
                # corrisponde all'indice del nodo da gemmare 
                # (all'interno della sequenza, non all'interno dell'array dei nodi)  
                if rand >= 1:
                    # se troppo grande (1 - 2*sigma = 5% dei casi) metto al minimo (1)
                    intrand = 1
                else:
                    intrand = int(rand*(len(l_sequenza)))

                # No nodo terminale (0)
                if intrand == 0:
                    intrand=1

                # seleziono l'indice del nodo scelto all'interno della sequenza
                i_nodo_scelto = l_sequenza[intrand]

                # Aggiungo il nodo scelto all'array (di indici) dei nodi scelti
                ai_nodi_scelti = np.append(ai_nodi_scelti, i_nodo_scelto)
                
                # indice del nodo di biforcazione da cui inizia la sequenza (è l'ultimo della lista)
                i_inizio_sequenza = l_sequenza[-1]
                i_secondo_sequenza = l_sequenza[-2]

                # Se il nodo di inizio sequenza è la radice...
                if i_inizio_sequenza == 0:
                    angolo_rsp = 0
                else:
                    # segmento contenente il nodo precedente l'inizio della sequenza 
                    # [0] serve a trasformare da 2d a 1d
                    seg_precedente = self.a_segmenti[self.a_segmenti[:, self.C_DEST] == i_inizio_sequenza][0]
                    # Segmento di inizio sequenza
                    seg_inizio_sequenza = self.a_segmenti[self.a_segmenti[:,self.C_DEST] == i_secondo_sequenza][0]
                    
                    # ordine del ramo nel segmento precedente l'inizio della sequenza
                    ordine_precedente = seg_precedente[self.C_ORDINE]
                    # ordine del ramo nel segmento di inizio sequenza
                    ordine_inizio_sequenza = seg_inizio_sequenza[self.C_ORDINE]
                    
                    # Compongo l'array degli angoli orizzontali dei rami secondari precedenti
                    # Se questo è il primo ramo secondario del ramo corrente allora imposto 0
                    if ordine_inizio_sequenza != ordine_precedente:
                        # questo è il primo ramo secondario del ramo corrente: spawn casuale
                        angolo_rsp = 0
                    else:
                        # questo non è il primo ramo secondario del ramo corrente
                        # quindi calcolo l'angolo del ramo secondario precedente
                        # cart_to_sphere restituisce ro, theta e phi. Uso [1] per selezionare theta

                        # Le condizioni per individuare il segmento che dà origine al rsp sono:
                        # l'origine è l'inizio sequenza...
                        cond1 = self.a_segmenti[:,self.C_ORIG] == i_inizio_sequenza
                        # e la destinazione non compare nella sequenza
                        cond2 = ~np.isin(self.a_segmenti[:,self.C_DEST], l_sequenza)

                        segmento_rsp = self.a_segmenti[cond1 & cond2][0]

                        nodo_orig = segmento_rsp[self.C_ORIG]
                        nodo_dest = segmento_rsp[self.C_DEST]
                        
                        angolo_rsp = Albero.cart_to_sphere(self.a_nodi[nodo_orig], self.a_nodi[nodo_dest])[1]
                
                # aggiungo angolo
                a_angoli_rsp = np.append(a_angoli_rsp,angolo_rsp)

            a_nodi_scelti = self.a_nodi[ai_nodi_scelti]            

            # costruzione array lunghezze dei segmenti (a_lung) e array allungamenti (a_allu)
            a_lung,a_allu = self.ricalcolo_array_allu()

            # Composizione array dei nodi di origine partendo dai nodi di destinazione
            ai_nodi_prec = self.a_segmenti[ai_nodi_scelti-1][:,self.C_ORIG]
            a_nodi_prec = self.a_nodi[ai_nodi_prec]

            # Con nodi di origine e destinazione posso calcolare gli angoli del ramo
            # cart_to_sphere restituisce ro(lunghezza) theta(angolo orizzontale) e phi(angolo verticale)
            a_angoli_oriz_p,a_angoli_vert_p = Albero.cart_to_sphere(a_nodi_prec,a_nodi_scelti)[1:]


            if not self.simmetria:

                # Se lo spawn dei segmenti è asimmetrico ne gemmo solo uno in maniera casuale

                # calcolo angoli massimi di deviazione dal padre (dipende dalla verticalità del padre)
                a_est_angoli = a_angoli_vert_p*4
                
                #print("Angoli vert p: ",a_angoli_vert_p)
                #print("est angoli: ",a_est_angoli)
                # estensione massima angolo orizzontale dei figli = angolo verticale del padre * 4 (minimo: pi)
                a_est_angoli[a_est_angoli < np.pi] = np.pi
                #print("Controllo:",a_est_angoli)
                
                
                # Calcolo angolo dei nuovi rami 
                # ottimale: opposto a rsp (rsp+pi)
                # reale: limitato da variazione massima dal padre
                a_angoli_oriz = a_angoli_rsp + np.pi + np.pi/4*(np.random.random()-.5)

                # Se l'angolo del nuovo ramo è oltre il limite massimo di divergenza dal padre...
                cond1 = (a_angoli_oriz < a_angoli_oriz_p +np.pi) & (a_angoli_oriz > a_angoli_oriz_p + a_est_angoli / 2.2)
                cond2 = (a_angoli_oriz > a_angoli_oriz_p +np.pi) & (a_angoli_oriz < a_angoli_oriz_p - a_est_angoli / 2.2 + 2*np.pi)
                
                
                # ... allora limito l'angolo impostando il valore massimo di variazione
                a_angoli_oriz[cond1] = (a_angoli_oriz_p+a_est_angoli/2.2)[cond1]
                a_angoli_oriz[cond2] = (a_angoli_oriz_p-a_est_angoli/2.2)[cond2]

                # angoli verticali: da pi/4 a pi/4 + pi/8
                a_angoli_vert = np.random.random(len(a_angoli_vert_p))*self.angolo_range_spawn+self.angolo_min_spawn

                # promemoria: sommare gli array come righe, poi trasporli e sommare le coordinate ai nodi scelti
                a_nuovi_nodi = a_nodi_scelti + np.vstack((
                    np.cos(a_angoli_oriz),
                    np.sin(a_angoli_oriz),
                    np.sin(a_angoli_vert))).T
                
            # se lo spawn è simmetrico gemmo doppio
            if self.simmetria:

                # vecchio metodo per angoli dei segmenti gemelli
                # a_angoli_oriz2 = a_angoli_oriz_p - a_diff_angoli

                ################################################################################
                # NUOVO ALGORITMO PER SIMMETRICI: 
                # se debole/media verticalità del padre (DEFAULT)
                #       --> stesso angolo verticale del padre
                #       --> angolo orizzontale fisso (es.: +45 e -45 rispetto al padre)
                # se forte verticalità del padre  (CORREZIONE)                 
                #       --> angolo verticale fisso (es.: +45 e -45 dal padre)
                #       --> angolo orizzontale: il primo random (e +180), i successivi perpendicolari al precedente 
                # 
                ################################################################################
                
                a_angoli_vert = a_angoli_vert_p
                a_angoli_vert2 = a_angoli_vert_p
                a_angoli_oriz = a_angoli_oriz_p + np.pi /4
                a_angoli_oriz2 = a_angoli_oriz_p - np.pi /4
                
                a_angoli_vert[a_angoli_vert_p > np.pi/3] += np.pi/4
                a_angoli_vert2[a_angoli_vert_p > np.pi/3] -= np.pi/4
                
                #a_angoli_oriz = angoli precedenti +90  # IMPLEMENTARE
                a_angoli_oriz = a_angoli_oriz_p + np.pi /2
                a_angoli_oriz2 = a_angoli_oriz_p - np.pi /2
                
                a_nuovi_nodi = a_nodi_scelti + np.vstack((
                    np.cos(a_angoli_oriz),
                    np.sin(a_angoli_oriz),
                    np.sin(a_angoli_vert))).T


                a_nuovi_nodi2 = a_nodi_scelti + np.vstack((
                    np.cos(a_angoli_oriz2),
                    np.sin(a_angoli_oriz2),
                    np.sin(a_angoli_vert2))).T

                a_nuovi_nodi = np.vstack((a_nuovi_nodi,a_nuovi_nodi2))
            

            a_ordini=self.a_segmenti[np.where(np.isin(self.a_segmenti[:,self.C_DEST],ai_nodi_scelti))][:,self.C_ORDINE] + 1, 
                
            if self.simmetria:
                # raddoppio array dei nodi di origine
                ai_nodi_scelti = np.hstack((ai_nodi_scelti,ai_nodi_scelti))
                # raddoppio array degli ordini    
                a_ordini=np.hstack((a_ordini,a_ordini))    

            a_nuovi_segmenti = np.vstack((
                ai_nodi_scelti, 
                np.arange(len(self.a_nodi),len(self.a_nodi)+len(a_nuovi_nodi)), 
                a_ordini)).T

            a_nuovi_spessori = np.full(len(a_nuovi_nodi),self.C_spess_iniz)

            self.a_segmenti = np.vstack((self.a_segmenti,a_nuovi_segmenti))
            self.a_nodi = np.vstack((self.a_nodi,a_nuovi_nodi))
            self.a_spessori = np.hstack((self.a_spessori,a_nuovi_spessori))
                
            #for segmento in a_nuovi_segmenti:
            #    self.rami = [ ramo+[int(segmento[self.C_DEST])] if int(segmento[self.C_ORIG]) in ramo else ramo for ramo in self.rami ]
            #for segmento in a_nuovi_segmenti:
            #    self.rami.append(segmento[0:2].tolist())

        # ALGORITMO DI PIEGAMENTO PER PESO DISABILITATO PER INEFFICIENZA
        # Si possono anche commentare le parti di codice che creano/aggiornano l'array self.rami 
        # self.piega_segmento(self.a_segmenti)


        # MORTE RAMETTI PER SOVRAFFOLLAMENTO

        # TODO
        # - MODIFICARE ALGORITMO PER NON CONSIDERARE OMBREGGIATI SE C'E' UNA PARTE NON OMBREGGIATA (LATERALI)

        # Generazione elenco delle ombre
        l_ombre,ai_nodi_terminali = elenco_ombre(self)
    
        # cerco il nodo più ombreggiato
        massima_ombra = max(l_ombre)
        self.mess2 = f"Massima ombra: {massima_ombra}"
        #print(l_ombre)

        if massima_ombra > 10:
            # individuo l'indice del nodo da togliere all'interno dell'array dei nodi terminali
            # (scelgo l'ombra massima nella lista ombre, prendo il suo indice e lo uso
            # sull'array degli indici dei nodi terminali) 
            i_nodo_da_togliere = ai_nodi_terminali[l_ombre.index(max(l_ombre))]

            #print("Nodo da togliere: ",i_nodo_da_togliere)

            # ricorda: il nodo N è il nodo di destinazione del segmento N-1
            i_padre_nodo_da_togliere = self.a_segmenti[i_nodo_da_togliere-1,self.C_ORIG]

            #print("padre nodo da togliere: ",i_padre_nodo_da_togliere)


            # Tolgo nodo, segmento e spessore
            self.a_nodi = np.delete(self.a_nodi,i_nodo_da_togliere,axis=0)
            self.a_segmenti = np.delete(self.a_segmenti,i_nodo_da_togliere-1,axis=0)
            self.a_spessori = np.delete(self.a_spessori,i_nodo_da_togliere-1,axis=0)
            # Riaggiusto i puntamenti dei segmenti
            self.a_segmenti[:,:2][self.a_segmenti[:,:2] > i_nodo_da_togliere] -=1

            
            # Se il nodo padre del nodo da togliere non è padre di nessun altro nodo, lo tolgo
            if ~np.any(self.a_segmenti[:,self.C_ORIG] == i_padre_nodo_da_togliere):
                self.a_nodi = np.delete(self.a_nodi,i_padre_nodo_da_togliere,axis=0)
                self.a_segmenti = np.delete(self.a_segmenti,i_padre_nodo_da_togliere-1,axis=0)
                self.a_spessori = np.delete(self.a_spessori,i_padre_nodo_da_togliere-1,axis=0)
                self.a_segmenti[:,:2][self.a_segmenti[:,:2] > i_padre_nodo_da_togliere] -=1
            



        # PROVA DI AGGIUNTA POLIGONI

        # SPESSORE

        if render_mode:
            aggiungi_spessori(self)
            return self.a_nodi_v,self.a_segm_v
        
        else:
            return self.a_nodi,self.a_segmenti


    def cart_to_sphere(coord1: np.ndarray,coord2: np.ndarray) -> np.ndarray:
        ''' 
        Trasforma da coordinate cartesiane a coordinate sferiche.
        - Input: 2 numpy array (origine e destinazione) di coordinate x,y,z 
        - Output: 1 numpy array contenente: ro (distanza), theta (angolo orizzontale) e phi (angolo verticale)
        '''

        if coord1.ndim == 1:
            vettori = coord2.reshape(1,-1) - coord1.reshape(1,-1)
        else:
            vettori = coord2 - coord1

        ro = np.sqrt(vettori[:,0]**2+vettori[:,1]**2+vettori[:,2]**2)
        theta = np.arctan2(vettori[:,1],vettori[:,0])
        phi = np.arcsin(vettori[:,2]/ro)

        return ro,theta,phi

    def ricalcolo_array_allu(self):
        
        '''
        Questa funzione restituisce due array:
        - a_lung --> lunghezze dei segmenti, basandosi sull'array a_diff e 
        - a_allu --> allungamenti dei segmenti, basandosi sugli array a_diff e a_lung
        '''

        C_ORIG=0
        C_DEST=1
        C_ORDINE=2
        Z=2 # La coordinata Z è la colonna 2 dell'array nodi

        # array differenze di coordinate
        a_diff=self.a_nodi[self.a_segmenti[:,self.C_DEST]]-self.a_nodi[self.a_segmenti[:,self.C_ORIG]]
        
        # array lunghezze dei vettori corrispondenti alle coordinate
        a_lung=np.linalg.norm(a_diff,axis=1)


        # Calcolo dell'ombreggiatura nella direzione di allungamento
        

        # array allungamenti
        # a_diff / a_lung --> vettori normalizzati
        # allungamento inversamente proporzionale all'ordine di ramo
        # allungamento proporzionale alla crescita_a (alterazione temporale)
        # allungamento proporzionale all'altezza dal suolo (1/100)

        a_allu = a_diff / a_lung[:,None] * self.crescita_a
        a_allu *=  4/(3+self.a_segmenti[:,C_ORDINE][:,None])
        # a_allu *= (1+ self.a_nodi[self.a_segmenti[:,C_DEST],Z][:,None] /1000) 
        # a_allu[:,2] -= .0001 

        return a_lung,a_allu 

    def ricalcolo_array_gemme(self):

        '''
        Questa funzione ricalcola gli array:
        - a_indici --> array degli indici dei nodi
        - a_gemme --> array delle gemme dei nodi

        TODO: forse è il caso di fonderli in un array unico?
        '''

        C_ORIG=0
        C_DEST=1

        # Conteggio rami collegati ad ogni nodo (conto anche il ramo "padre")
        # Il numero di gemme esatto (se servisse) è n-gemme -1
        #
        # Sommo tutti i nodi che trovo sia come origine che come destinazione
        # fondendo colonne 0 e 1 (C_ORIG e C_DEST)
        # Faccio la unique+return_counts per contarli

        a_indici,a_gemme = np.unique(np.append(self.a_segmenti[:,C_ORIG], self.a_segmenti[:,C_DEST]),return_counts=True)

        return a_indici,a_gemme

    def calcolo_prosecuzione_segmenti(self):

        '''
        Questa funzione calcola gli array:
        - a_filtro --> filtro da applicare all'array nodi per ottenere quelli senza gemme appartenenti a rami lunghi
        - a_rand --> array di valori random da applicare alla crescita dei nuovi segmenti
        
        TODO: spostare il calcolo di a_rand fuori da questa funzione? Sembra poco attinente...
        '''

        C_DEST=1

        # Aggiorno il conteggio delle gemme
        a_indici,a_gemme = self.ricalcolo_array_gemme()

        # Combino le due condizioni:
        # 1) nodi con gemme=1 (array completo di booleani, es.: [ True, False, False, True, ...])
        # 2) nodi terminali di rami lunghi (array parziale di indici di nodi, es.: [ 3, 5, 17] )

        # Array "filtro"  
        a_filtro_gemme = a_gemme == 1

        # Array "filtro" contenente gli indici dei nodi terminali di segmenti lunghi
        a_filtro_lunghi = self.a_segmenti[self.a_lung > 20,C_DEST]

        # a_filtro_lunghi --> array indici dei nodi teminali di segmenti lunghi
        # a_filtro_gemme  
        a_filtro = a_filtro_lunghi[a_filtro_gemme[a_filtro_lunghi]]

        # Array di variazione casuale su x e y, mentre su z è fissa (alto)
        a_rand = np.random.uniform(-0.002, 0.002, size=(len(a_gemme), 3))
        a_rand[:, 2] += self.alto


        #return a_gemme, a_indici, a_filtro, a_rand
        return a_filtro, a_rand



    def piega_segmento(self,a_elenco_segmenti):

        # calcolo coordinate polari dei nodi dei segmenti da piegare
        a_orig=self.a_nodi[a_elenco_segmenti[:,self.C_ORIG]]
        a_dest=self.a_nodi[a_elenco_segmenti[:,self.C_DEST]]
        a_ro,a_theta,a_phi = Albero.cart_to_sphere (a_orig,a_dest)
        
        # piego verso 0° (orizzontale)
        #a_phi *= .9999
        
        a_phi = a_phi - a_phi/np.exp(a_phi*5)/100

        # riapplicazione angolo modificato
        a_nuove_x = a_orig[:,self.C_X] + a_ro * np.cos(a_theta) * np.cos(a_phi)
        a_nuove_y = a_orig[:,self.C_Y] + a_ro * np.sin(a_theta) * np.cos(a_phi)
        a_nuove_z = a_orig[:,self.C_Z] + a_ro * np.sin(a_phi)
        
        a_dest = np.vstack((a_nuove_x,a_nuove_y,a_nuove_z)).T


        # Calcolo le differenze di coordinate (serviranno per spostare tutti i segmenti collegati)
        a_differenze = self.a_nodi[a_elenco_segmenti[:,self.C_DEST]] - a_dest 

        # Sostituisco le nuove coordinate di destinazione
        self.a_nodi[a_elenco_segmenti[:,self.C_DEST]] = a_dest

        # I segmenti successivi sono quelli che hanno come origine i nodi di destinazione dei segmenti attuali
        # a_segmenti_successivi=self.a_segmenti[self.a_segmenti[:,self.C_ORIG] == a_elenco_segmenti[:,self.C_DEST]]

        # Per ogni segmento cerco i successivi, 
        # li abbasso di quanto si è abbassato il nodo di destinazione e
        # li piego a loro volta

        for i in range(a_elenco_segmenti.shape[0]):
            segmento = a_elenco_segmenti[i]
            diff = a_differenze[i]
            a_segmenti_successivi = self.a_segmenti[self.a_segmenti[:,self.C_ORIG] == segmento[self.C_DEST]]
            if a_segmenti_successivi.size > 0:
                self.abbassa_ramo(a_segmenti_successivi,diff)
                self.piega_segmento(a_segmenti_successivi)


    def abbassa_ramo(self, a_elenco_segmenti, differenze):
        self.a_nodi[a_elenco_segmenti[:,self.C_DEST]] += differenze
        a_segmenti_successivi = self.a_segmenti[np.in1d(self.a_segmenti[:,self.C_ORIG], a_elenco_segmenti[:,self.C_DEST])]
        if a_segmenti_successivi.size > 0:
            self.abbassa_ramo(a_segmenti_successivi,differenze)

            
def aggiungi_spessori(self):
    nodi_visua1 = self.a_nodi.copy()
    nodi_visua2 = self.a_nodi.copy()
    nodi_visua3 = self.a_nodi.copy()
    nodi_visua4 = self.a_nodi.copy()
    nodi_visua2[0,0] += self.a_spessori[0]
    nodi_visua2[1:,0] += self.a_spessori
    nodi_visua3[0,1] += self.a_spessori[0]
    nodi_visua3[1:,1] += self.a_spessori
    nodi_visua4[0,2] += self.a_spessori[0]
    nodi_visua4[1:,2] += self.a_spessori
    
    segm_visua1 = self.a_segmenti.copy()
    segm_visua2 = self.a_segmenti.copy()
    segm_visua3 = self.a_segmenti.copy()
    segm_visua4 = self.a_segmenti.copy()
    segm_visua2[:,:2] += len(self.a_segmenti)+1  
    segm_visua3[:,:2] += 2*len(self.a_segmenti)+2  
    segm_visua4[:,:2] += 3*len(self.a_segmenti)+3  

    self.a_nodi_v = np.vstack((nodi_visua1,nodi_visua2,nodi_visua3,nodi_visua4))
    self.a_segm_v = np.vstack((segm_visua1,segm_visua2,segm_visua3,segm_visua4))


def elenco_ombre(self):
    ''' 
    Restituisce una lista di interi corrispondenti all'ombreggiatura di ogni nodo terminale
    '''

    # Cerco i segmenti terminali (quelli che NON hanno i nodi di destinazione tra tutti i nodi di origine )
    a_segmenti_terminali = self.a_segmenti[~np.isin(self.a_segmenti[:,self.C_DEST],self.a_segmenti[:,self.C_ORIG])]

    # Compongo array degli indici dei nodi terminali prendendo i nodi di destinazione dei segmenti terminali
    ai_nodi_terminali = a_segmenti_terminali[:,self.C_DEST]

    # Per ogni gemma calcolo quante gemme si trovano in un cono rovesciato al di sopra di essa
        
    l_ombre = []

    # per ogni gemma calcolo l'ombreggiatura
    for i in ai_nodi_terminali:
        ombra = 0
        for j in ai_nodi_terminali:
            ro,theta,phi = Albero.cart_to_sphere(self.a_nodi[i],self.a_nodi[j])
            # se esiste un nodo terminale ("foglia") in un angolo verticale compreso tra +- pi/4... 
            if phi > np.pi/4 and phi < np.pi/4*3:
                # ... considero la gemma come "ombreggiata"
                ombra += 1
        l_ombre.append(ombra)
    return l_ombre,ai_nodi_terminali
