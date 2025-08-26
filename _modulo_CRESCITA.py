import numpy as np
import random

if 1 < 0:
    class Lunghezze:
        ...

class Albero:
    def __init__(self) -> None:

        # INIZIALIZZAZIONE VARIABILI
    
        # a_nodi è un array numpy (float) 2D di coordinate [x,y,z]
        self.a_nodi: np.ndarray['Lunghezze', float] = np.array([[0.,0.,0.],[0.,0.,1.]])   # primi due nodi

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
        self.alto = .00
        # tendenza verso il basso dei rami vecchi
        self.basso = -.01
        # massima variazione di angolo iniziale rispetto al ramo padre
        # self.angolo_iniziale = np.pi/8
        # angolo minimo di spawn nuovi rami 
        self.angolo_min_spawn = 0* np.pi/4
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
        - rallentare crescita per rami vecchi o bassi (?)
        - modificare la crescita e la direzione di spawn in base alla posizione (rami in ombra)
        - diminuire/bloccare spawn in zone affollate / aumentare morte rami affollati
        - generare foglie (estetico)
        - ALBERO --> BONSAI  (potatura)
        - Abbassamento rami vecchi
        - NON FUNZIONA BENE: crescita dei rami vecchi (troppo? non curvano? non muoiono?)
        '''
        
        self.iterazioni += 1
        #print(self.iterazioni)
        
        # La lunghezza dei segmenti vale al massimo 20 (valore arbitrario)
        # e corrisponde ad una lunghezza di 2 cm (self.dim_segm)
        # Calcolo l'altezza dell'albero cercando la coordinata Z del nodo più alto
        # la divido per 20 (il valore arbitrario) 
        # e la moltiplico per dim_segm (la dimensione reale in cm)
        # Per estetica, prendo solo la parte intera e divido per 100 per avere
        # l'altezza in metri con precisione fino al centimetro 
 
        self.dim_segm_virt = 20
        self.dim_segm_reale = 2
        self.altezza_max_nodi = np.max(self.a_nodi[:,self.C_Z]) # Serve per il calcolo ombreggiature
        self.mess1 = f"Altezza (m): {int(self.altezza_max_nodi*self.dim_segm_reale/self.dim_segm_virt)/100}"
        self.mess4 = f"iterazioni: {self.iterazioni}"
        self.mess5 = f"segmenti: {len(self.a_segmenti)}"

        # BLOCCO CRESCITA A 30000 SEGMENTI
        if len(self.a_segmenti) > 30000: 
            # if render_mode:
            #     aggiungi_spessori(self)
            #     return self.a_nodi_v,self.a_segm_v
            # else:
            return self.a_nodi,self.a_segmenti

        # STEP 1 - CRESCITA IN LARGHEZZA DI TUTTI I SEGMENTI
        self.a_spessori += self.crescita_l

        # STEP 2 - ALLUNGAMENTO SEGMENTI TERMINALI  
        #print("STEP 2")
        
        # Cerco i segmenti che contengono nodi terminali, cioè nodi di destinazione che non sono nodi di origine di nessun segmento
        ab_segmenti_terminali = ~np.isin(self.a_segmenti[:, self.C_DEST], self.a_segmenti[:, self.C_ORIG])

        # L'array di booleani dei segmenti terminali può essere applicato anche ai nodi per trovare i nodi terminali
        # aggiungendo un elemento in testa, relativo al nodo 0 che non è destinazione di nessun segmento
        ab_nodi_terminali = np.hstack(([False],ab_segmenti_terminali))

        # Seleziono solo i segmenti terminali
        a_segmenti_terminali = self.a_segmenti[ab_segmenti_terminali]

        # a_diff: array differenze di coordinate tra nodi di origine e nodi di destinazione dei segmenti terminali
        a_diff_term=self.a_nodi[a_segmenti_terminali[:,self.C_DEST]]-self.a_nodi[a_segmenti_terminali[:,self.C_ORIG]]
        
        # a_lung: array lunghezze dei segmenti, calcolate usando le differenze di coordinate
        a_lunghezze_term=np.linalg.norm(a_diff_term,axis=1)        

        # a_allu: array degli allungamenti dei segmenti terminali
        # a_diff / a_lung --> Normalizza i vettori di differenze
        # allungamento proporzionale alla crescita_a (alterazione temporale)
        # allungamento inversamente proporzionale all'ordine di ramo
        
        a_allu_term = a_diff_term / a_lunghezze_term[:,None] * self.crescita_a / self.a_segmenti[ab_segmenti_terminali,self.C_ORDINE][:,None]
        
        # Allungo i segmenti terminali
        self.a_nodi[a_segmenti_terminali[:,self.C_DEST]] += a_allu_term

        # STEP 3 - CREAZIONE NUOVI SEGMENTI TERMINALI
        #print("STEP 3")
        
        #  Creazione nuovi segmenti che sono la prosecuzione dei segmenti terminali
        #  I segmenti che gemmano sono un sottoinsieme di quelli terminali, più precisamente quelli lunghi almeno 20 unità 
        #  Quindi filtro tutti gli array precedenti selezionando solo i segmenti lunghi

        # Filtro i segmenti terminali lunghi
        ab_seg_terminali_lunghi  = np.copy(ab_segmenti_terminali)
        ab_seg_terminali_lunghi[ab_seg_terminali_lunghi] = a_lunghezze_term > 20 
        
        # Filtro gli indici dei segmenti terminali lunghi
        ai_seg_terminali_lunghi = np.where(ab_seg_terminali_lunghi)[0]

        # Se le condizioni di spawn nuovi segmenti esistono almeno per un nodo, creo il nuovo segmento
        if ai_seg_terminali_lunghi.size > 0:

            # Filtro l'array degli allungamenti per i soli segmenti terminali lunghi
            a_allu_term_lunghi = np.copy(a_allu_term)
            a_allu_term_lunghi = a_allu_term_lunghi[a_lunghezze_term > 20]

            # aggiungo piegamento verso il basso in base alla posizione nell'albero
            # primo tentativo: modifico la z (5% del rapporto tra altezza nodo e altezza albero)
            # secondo tentativo: modifico phi
            a_allu_term_lunghi[:,self.C_Z] *= (20+self.a_nodi[self.a_segmenti[ai_seg_terminali_lunghi,self.C_DEST],self.C_Z]/self.altezza_max_nodi)/19


            # VECCHIO ALGORITMO DI CRESCITA CASUALE 
            # Array di variazione casuale su x e y, mentre su z è fissa
            a_rand_term_lunghi = np.random.uniform(-2, 2, size=(len(ai_seg_terminali_lunghi), 3))
            #a_rand_term_lunghi[:, 2] += self.alto
            

            # 3.1) NUOVI NODI
            # L'array dei nuovi nodi è composto da tutti i nodi che devono gemmare 
            # ai quali sommo gli allungamenti del ramo precedente (prosecuzione)
            # e un fattore casuale sulle coordinate (x e y: casuali, z casuale + un fisso: "alto")

            # Estendo array degli allungamenti per applicarlo ai nodi (nodi=segmenti+1)
            #a_allu_esteso = np.vstack((np.array([[0.,0.,0.]]),a_allu))

            # Estendo array dei segmenti terminali lunghi per applicarlo ai nodi
            ab_nodi_terminali_lunghi = np.hstack(([False],ab_seg_terminali_lunghi))


            # Creo i nuovi nodi
            a_nuovi_nodi = self.a_nodi[ ab_nodi_terminali_lunghi ] + a_allu_term_lunghi #+ a_rand_term_lunghi

            #print("a_nuovi nodi: ",a_nuovi_nodi)

            # 3.2) NUOVI SEGMENTI

            # L'indice di un nodo di destinazione è sempre uguale all'indice del segmento che lo contiene +1
            ai_nodi_orig = ai_seg_terminali_lunghi + 1

            ai_nodi_dest = np.array([np.arange(len(self.a_nodi),len(self.a_nodi)+len(a_nuovi_nodi))])
            a_ordini = np.array(self.a_segmenti[ai_seg_terminali_lunghi][:,self.C_ORDINE])

            # Sommo come righe, poi traspongo con T
            #print (ai_nodi_orig,ai_nodi_dest,a_ordini)
            
            a_nuovi_segmenti = np.vstack([ai_nodi_orig,ai_nodi_dest,a_ordini]).T

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
            #for segmento in a_nuovi_segmenti:
            #    self.rami = [ ramo+[int(segmento[self.C_DEST])] if int(segmento[self.C_ORIG]) in ramo else ramo for ramo in self.rami ]
            #for segmento in a_nuovi_segmenti:
            #    self.rami.append(segmento[0:2].tolist())
            
        # STEP 4 - GENERAZIONE NUOVI RAMI SECONDARI 
        # Faccio spuntare nelle zone di ramo spoglie (sequenze di almeno 20 segmenti senza biforcazioni)
        #         
        
        # Compongo la lista di sequenze di indici di nodi che vanno dalle punte alle biforcazioni (parti di ramo)
        # (lli_sequenze è una lista di liste di indici di nodi)
        lli_sequenze: list[list[int]] = []

        # Generazione array delle gemme (indica quante gemme ha ogni nodo)
        # Conto quante volte ogni nodo compare nei segmenti (metto insieme tutti i nodi de origine e destinazione)
        _,a_gemme = np.unique(np.append(self.a_segmenti[:,self.C_ORIG], self.a_segmenti[:,self.C_DEST]),return_counts=True)
        
        # Promemoria:
        # 1 gemma: è un nodo terminale (eccezione: il nodo 0)
        # 2 gemme: è un nodo intermedio
        # 3 o più: è un nodo biforcazione

        for i_nodo in np.where(ab_nodi_terminali)[0]:

            li_sequenza=[i_nodo]
            
            while a_gemme[i_nodo] < 3 and i_nodo > 0:
                i_nodo=self.a_segmenti[i_nodo-1,self.C_ORIG]
                li_sequenza.append(i_nodo)

            # Aggiungo questa sequenza alla lista delle sequenze lunghe (lista di liste di nodi)
            if len(li_sequenza) > 20:
                lli_sequenze.append(li_sequenza)

        if lli_sequenze:

            # Inizializzazione array di indici dei nodi scelti per gemmare
            ai_nodi_scelti=np.empty(0,dtype=int)
            # Inizializzazione array di angoli dei rami secondari precedenti
            a_angoli_rsp=np.empty(0,dtype=float)

            # SCELTA DEL NODO DA GEMMARE

            for li_sequenza in lli_sequenze:
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
                    intrand = int(rand*(len(li_sequenza)))

                # No nodo terminale (0)
                if intrand == 0:
                    intrand=1

                # seleziono l'indice del nodo scelto all'interno della sequenza
                i_nodo_scelto = li_sequenza[intrand]

                # Calcolo l'ombra sul nodo scelto
                # Se non è troppo ombreggiato lo faccio gemmare altrimenti non lo considero
                
                ombra = elenco_ombre(self,i_nodo_scelto)
                if ombra < 20:

                    # Aggiungo il nodo scelto all'array (di indici) dei nodi scelti
                    ai_nodi_scelti = np.append(ai_nodi_scelti, i_nodo_scelto)
                    
                    # indice del nodo di biforcazione da cui inizia la sequenza (è l'ultimo della lista)
                    i_inizio_sequenza = li_sequenza[-1]
                    i_secondo_sequenza = li_sequenza[-2]

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
                            cond2 = ~np.isin(self.a_segmenti[:,self.C_DEST], li_sequenza)

                            segmento_rsp = self.a_segmenti[cond1 & cond2][0]

                            nodo_orig = segmento_rsp[self.C_ORIG]
                            nodo_dest = segmento_rsp[self.C_DEST]
                            
                            angolo_rsp = Albero.cart_to_sphere(self.a_nodi[nodo_orig], self.a_nodi[nodo_dest])[1]
                    
                    # aggiungo angolo
                    a_angoli_rsp = np.append(a_angoli_rsp,angolo_rsp)

            a_nodi_scelti = self.a_nodi[ai_nodi_scelti]            

            # costruzione array lunghezze dei segmenti (a_lung) e array allungamenti (a_allu)
            #a_allu = a_diff / a_lunghezze[:,None] * self.crescita_a / self.a_segmenti[ab_segmenti_terminali,self.C_ORDINE][:,None]
        
            # Composizione array dei nodi di origine partendo dai nodi di destinazione
            ai_nodi_prec = self.a_segmenti[ai_nodi_scelti-1][:,self.C_ORIG]
            a_nodi_prec = self.a_nodi[ai_nodi_prec]

            # Con nodi di origine e destinazione posso calcolare gli angoli del ramo
            # cart_to_sphere restituisce ro(lunghezza) theta(angolo orizzontale) e phi(angolo verticale)
            a_angoli_oriz_p,a_angoli_vert_p = Albero.cart_to_sphere(a_nodi_prec,a_nodi_scelti)[1:]


            if not self.simmetria:

                # Se lo spawn dei segmenti è asimmetrico ne gemmo solo uno in maniera casuale

                # calcolo angoli massimi di deviazione dal padre (dipende dalla verticalità del padre)
                # estensione massima angolo orizzontale dei figli = angolo verticale del padre * 4 (minimo: pi)
                a_est_angoli = a_angoli_vert_p*4
                a_est_angoli[a_est_angoli < np.pi] = np.pi
                
                
                # Calcolo angolo dei nuovi rami 
                # ottimale: alternanza diversa per specie (fibonacci?)
                # implementato : quasi opposto a rsp (rsp+pi+/-rnd*pi/4) 
                a_angoli_oriz = a_angoli_rsp + np.pi + np.pi/2*(np.random.random()-.5)

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

            # ricorda: il nodo N è il nodo di destinazione del segmento N-1
            i_padre_nodo_da_togliere = self.a_segmenti[i_nodo_da_togliere-1,self.C_ORIG]

            #print("Nodo da togliere: ",i_nodo_da_togliere,"padre nodo da togliere: ",i_padre_nodo_da_togliere)


            # Tolgo nodo, segmento e spessore
            self.a_nodi = np.delete(self.a_nodi,i_nodo_da_togliere,axis=0)
            self.a_segmenti = np.delete(self.a_segmenti,i_nodo_da_togliere-1,axis=0)
            self.a_spessori = np.delete(self.a_spessori,i_nodo_da_togliere-1,axis=0)
            # Riaggiusto i puntamenti dei segmenti
            self.a_segmenti[:,:2][self.a_segmenti[:,:2] > i_nodo_da_togliere] -=1

            
            # Se il nodo padre del nodo da togliere non è padre di nessun altro nodo, lo tolgo
            if ~np.any(self.a_segmenti[:,self.C_ORIG] == i_padre_nodo_da_togliere):
                print("Tolgo padre")
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

        # Se ricevo solo una tripletta singole di coordinate, le trasformo in array bidimensionali prima di fare la differenza 
        if coord1.ndim == 1:
            vettori = coord2.reshape(1,-1) - coord1.reshape(1,-1)
        else:
            vettori = coord2 - coord1

        ro = np.sqrt(vettori[:,0]**2+vettori[:,1]**2+vettori[:,2]**2)
        theta = np.arctan2(vettori[:,1],vettori[:,0])
        phi = np.arcsin(vettori[:,2]/ro)

        return ro,theta,phi

    def ricalcolo_array_gemme(self):

        '''
        Questa funzione ricalcola l'array a_gemme, cioè il numero di gemme in cui si divide ciascun nodo dell'albero
        '''

        C_ORIG=0
        C_DEST=1

        # Conteggio rami collegati ad ogni nodo (conto anche il ramo "padre")
        # Il numero di gemme esatto (se servisse) è n-gemme -1
        #
        # Sommo tutti i nodi che trovo sia come origine che come destinazione
        # fondendo colonne 0 e 1 (C_ORIG e C_DEST)
        # Faccio la unique+return_counts per contarli

        _,a_gemme = np.unique(np.append(self.a_segmenti[:,C_ORIG], self.a_segmenti[:,C_DEST]),return_counts=True)

        return a_gemme

    def calcolo_prosecuzione_segmenti(self):

        '''
        Questa funzione calcola gli array:
        - a_filtro --> filtro da applicare all'array nodi per ottenere quelli senza gemme appartenenti a rami lunghi
        - a_rand --> array di valori random da applicare alla crescita dei nuovi segmenti
        '''

        C_ORIG=0
        C_DEST=1

        # Creo filtro per i segmenti terminali (quelli che hanno nodi di destinazione che non sono nodi origine di nessun segmento)
        ab_terminali = ~np.isin(self.a_segmenti[:, C_DEST], self.a_segmenti[:, C_ORIG])
        print("Elenco rami terminali: ",ab_terminali)

        # array differenze di coordinate tra nodi di origine e nodi di destinazione dei segmenti terminali
        a_diff=self.a_nodi[self.a_segmenti[ab_terminali,C_DEST]]-self.a_nodi[self.a_segmenti[ab_terminali,C_ORIG]]
        print("Calcolo differenze di coordinate dei soli segmenti terminali: ",a_diff)

        # calcolo array lunghezze dei segmenti terminali
        a_lunghezze=np.linalg.norm(a_diff,axis=1)        
        print("Array lunghezze dei segmenti terminali: ",a_lunghezze)

        # Creo il filtro che individua i segmenti terminali lunghi almeno 20 unità
        ab_filtro = ab_terminali & (a_lunghezze > 20)
        print("filtro: ",ab_filtro)
        
        # Creo il filtro di indici partendo dal filtro di booleani
        ai_filtro = np.where(ab_filtro)[0]



        print("AGGIUNGERE ALTERAZIONE VERTICALE DOVUTA ALL'OMBREGGIATURA per nuovi rami terminali")
        # Generazione elenco delle ombre per decidere angolo verticale di crescita
        #l_ombre,ai_nodi_terminali = elenco_ombre(self)

        # Array di variazione casuale su x e y, mentre su z dipende dalle ombre
        a_rand = np.random.uniform(-0.002, 0.002, size=(len(ai_filtro), 3))
        a_rand[:, 2] += self.alto
        #a_rand[:, 2] = a_rand[:, 2] / l_ombre[a_filtro]

        # La variazione in altezza deve dipendere dall'ombreggiatura
        # - poco ombreggiato --> più verticale
        # - molto ombreggiato --> meno verticale

        return ai_filtro, a_rand



    def piega_segmento(self,segmento):

        # calcolo coordinate polari dei nodi dei segmenti da piegare
        coord_orig=self.a_nodi[segmento[self.C_ORIG]]
        coord_dest=self.a_nodi[segmento[self.C_DEST]]
        ro,theta,phi = Albero.cart_to_sphere (coord_orig,coord_dest)
        
        
        # piego verso 0° (orizzontale)
        phi *= .99999
        
        # riapplicazione angolo modificato
        nuova_x = coord_orig[self.C_X] + ro * np.cos(theta) * np.cos(phi)
        nuova_y = coord_orig[self.C_Y] + ro * np.sin(theta) * np.cos(phi)
        nuova_z = coord_orig[self.C_Z] + ro * np.sin(phi)
        
        # assicurarsi che venga generato un array simile a a_nodi[segmento] per poter sottrarre il primo dal secondo
        nuova_dest = np.vstack((nuova_x,nuova_y,nuova_z)).T
        
        # Calcolo le differenze di coordinate (serviranno per spostare tutti i segmenti collegati)
        a_differenze = self.a_nodi[segmento[self.C_DEST]] - nuova_dest 
        
        # Sostituisco le nuove coordinate di destinazione
        self.a_nodi[segmento[self.C_DEST]] = nuova_dest

        # I segmenti successivi sono quelli che hanno come origine i nodi di destinazione dei segmenti attuali
        # a_segmenti_successivi=self.a_segmenti[self.a_segmenti[:,self.C_ORIG] == a_elenco_segmenti[:,self.C_DEST]]

        # Per ogni segmento cerco i successivi, 
        # li abbasso di quanto si è abbassato il nodo di destinazione e
        # li piego a loro volta

        a_segmenti_successivi = self.a_segmenti[self.a_segmenti[:,self.C_ORIG] == segmento[self.C_DEST]]
        if a_segmenti_successivi.size > 0:
            self.sposta_segmento(a_segmenti_successivi,a_differenze)
            for segmento_successivo in a_segmenti_successivi:
                self.piega_segmento(segmento_successivo)


    def sposta_segmento(self, a_elenco_segmenti, differenze):
        self.a_nodi[a_elenco_segmenti[:,self.C_DEST]] += differenze
        a_segmenti_successivi = self.a_segmenti[np.in1d(self.a_segmenti[:,self.C_ORIG], a_elenco_segmenti[:,self.C_DEST])]
        if a_segmenti_successivi.size > 0:
            self.sposta_segmento(a_segmenti_successivi,differenze)

            
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


def elenco_ombre(self, nodo: int = 0):
    ''' 
    Restituisce una lista di interi corrispondenti all'ombreggiatura di ogni nodo terminale
    '''

    # Cerco i segmenti terminali (quelli che NON hanno i nodi di destinazione tra tutti i nodi di origine )
    a_segmenti_terminali = self.a_segmenti[~np.isin(self.a_segmenti[:,self.C_DEST],self.a_segmenti[:,self.C_ORIG])]

    # Compongo array degli indici dei nodi terminali prendendo i nodi di destinazione dei segmenti terminali
    ai_nodi_terminali = a_segmenti_terminali[:,self.C_DEST]

    
    # Se alla funzione è stato passato un nodo specifico calcolo l'ombra solo su quello
    # altrimenti calcolo per tutti i nodi terminali

    if nodo != 0:

        i = nodo
        ombra = 0

        for j in ai_nodi_terminali:
            if i != j:
                ro,theta,phi = Albero.cart_to_sphere(self.a_nodi[i],self.a_nodi[j])
                # se esiste un nodo terminale ("foglia") in un angolo verticale compreso tra +- pi/4... 
                if phi > np.pi/4 and phi < np.pi/4*3:
                    # ... considero la gemma come "ombreggiata"
                    ombra += 1
        return ombra

    else:

        l_ombre = []

        # per ogni gemma calcolo l'ombreggiatura
        for i in ai_nodi_terminali:
            ombra = 0
            for j in ai_nodi_terminali:
                if i != j:
                    ro,theta,phi = Albero.cart_to_sphere(self.a_nodi[i],self.a_nodi[j])
                    # se esiste un nodo terminale ("foglia") in un angolo verticale compreso tra +- pi/4... 
                    if phi > np.pi/4 and phi < np.pi/4*3:
                        # ... considero la gemma come "ombreggiata"
                        ombra += 1
            l_ombre.append(ombra)
        return l_ombre,ai_nodi_terminali
