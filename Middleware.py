import Internal_data
import ui
import Database

from moneyed import Money, EUR
from enum import Enum
import sqlite3

class Middlware_GUI():
    #Vari Enum di classe
    class chosenGUIMiddlware(Enum):
        PYQT = "PYQT"

    #Varie GUI implementate
    class Middleware_PyQt():

        def chiamaDialgInfo_PYQT(textBox:str):
            box=ui.FinestraInfoDialog(okButtonClickedFunction=lambda:box.done(1),textBox=textBox)
            box.exec()

        def update_progress_restoreDatabase_PYQT(signal,value):
            signal.emit(value)

    #Init
    def __init__(self,chosenGUI):
        self.chosenGUI = chosenGUI

    #Varie funzioni principali da richiamare dall'esterno

    def update_progress_restoreDatabase(self,signal,value):
        if self.chosenGUI == self.chosenGUIMiddlware.PYQT:
            self.Middleware_PyQt.update_progress_restoreDatabase_PYQT(signal=signal,value=value)

    def chiamaDialgInfo(self,textBox:str):
        if self.chosenGUIMiddlware.PYQT:
            return self.Middleware_PyQt.chiamaDialgInfo_PYQT(textBox=textBox)

middlwareGui = Middlware_GUI(chosenGUI=Middlware_GUI.chosenGUIMiddlware.PYQT)

class Middlware_Database():
    #Vari Enum di classe
    class chosenDatabaseMiddleware(Enum):
        SQLITE = "SQLITE"
    class tipoRicercaBancadati(Enum):
        Denominazione_e_Confezione  =   "Denominazione e Confezione"
        Descrizione_Gruppo          =   "Descrizione Gruppo"
        Principio_Attivo            =   "Principio Attivo"
        Titolare_AIC                =   "Titolare AIC"
        Codice_AIC                  =   "Codice AIC"
        Cod_Gruppo_Equivalenza      =   "Cod. Gruppo Equivalenza"
        ID_Farmaco                  =   "ID Farmaco"
        Forma_farmaceutica          =   "Forma farmaceutica"
        Prezzo_attuale              =   "Prezzo attuale"
    
    #Vari Database implementati
    class Middleware_SQLITE():
        #FUNZIONI DI CONVERSIONE
        def convert_tipoRicercaBancadati_SQLITE(type:Enum)->str:
            """
            Converte gli Enum generici nelle stringhe specifiche utilizzate da SQLITE
            """
            #Da vedere se serve altro
            if type==Middlware_Database.tipoRicercaBancadati.Cod_Gruppo_Equivalenza:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.cod_gruppo
            elif type==Middlware_Database.tipoRicercaBancadati.Codice_AIC:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.codice_aic
            elif type==Middlware_Database.tipoRicercaBancadati.Denominazione_e_Confezione:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.descrizione_farmaco
            elif type==Middlware_Database.tipoRicercaBancadati.Descrizione_Gruppo:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.descrizione_gruppo
            elif type==Middlware_Database.tipoRicercaBancadati.ID_Farmaco:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.Farmaco_primarykey
            elif type==Middlware_Database.tipoRicercaBancadati.Principio_Attivo:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.principio_attivo
            elif type==Middlware_Database.tipoRicercaBancadati.Forma_farmaceutica:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.forma_farmaceutica
            elif type==Middlware_Database.tipoRicercaBancadati.Prezzo_attuale:
                return Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.prezzo
            elif type==Middlware_Database.tipoRicercaBancadati.Titolare_AIC:
                return Database.Banca_dati.nome_tabella_Azienda[1]+"."+Database.Banca_dati.nome_azienda
        def get_all_FarmacoVendita_data_SQLITE() -> list[Internal_data.Farmaco_vendita]:
            farmaci = Database.execute_query(f""" SELECT b.{Database.Banca_dati.codice_aic},
                            b.{Database.Banca_dati.descrizione_farmaco},
                            b.{Database.Banca_dati.prezzo},
                            b.{Database.Banca_dati.importo_assistito},
                            b.{Database.Banca_dati.prezzo_rimborso},
                            b.{Database.Banca_dati.note},
                            b.{Database.Banca_dati.tipo_ricetta},
                            b.{Database.Banca_dati.cl},
                            v.{Database.vendita.referencesToBancaDati},
                            v.{Database.vendita.tipo_vendita},
                            v.{Database.vendita.numero_progressivo_ricetta},
                            v.{Database.vendita.referencesToRicette},
                            v.{Database.vendita.quantità},
                            v.{Database.vendita.sospesi}
                    FROM {Database.vendita.nome} v
                    LEFT JOIN {Database.Banca_dati.nome_tabella_Farmaco[0]} b ON v.{Database.vendita.referencesToBancaDati} = b.{Database.Banca_dati.Farmaco_primarykey}
                """)
            lista_farmaci=[]
            for i,farmaco in enumerate(farmaci):
                progressivo_riga=i+1 #credo
                new_farmaco=Internal_data.Farmaco_vendita()
                #AIC: [0], Descrizione Farmaco: [1], Prezzo: [2], Importo Assistito: [3], Prezzo Rimborso: [4], None: [5], Tipo Ricetta: [6], Cl: [7],
                #ID Farmaco: [8], V: [9], Pr: [10], ID Ricetta: [11], Qta: [12], Sosp: [13] 
                new_farmaco.Progressivo_riga    =   progressivo_riga
                new_farmaco.Codice_AIC          =   farmaco[0]
                new_farmaco.V                   =   farmaco[9]
                new_farmaco.Pr                  =   farmaco[10]
                new_farmaco.ID_Ricetta          =   farmaco[11]
                new_farmaco.Prodotto            =   farmaco[1]
                new_farmaco.Prezzo              =   Money(farmaco[2],EUR)
                new_farmaco.Importo             =   Money(farmaco[2],EUR) #per ora uguale al prezzo, non so che cambia
                new_farmaco.Qta                 =   farmaco[12]
                new_farmaco.Sosp                =   farmaco[13]
                new_farmaco.Pr_Rimborso         =   Money(farmaco[4],EUR)
                new_farmaco.Diff                =   Money(farmaco[3],EUR)
                if new_farmaco.V=="S":
                    new_farmaco.Quota           =   Money(2,EUR)
                elif new_farmaco.V=="K" or new_farmaco.V=="Y":
                    new_farmaco.Quota           =   Money(1,EUR)
                elif new_farmaco.V=="0" or new_farmaco.V=="A":
                    new_farmaco.Quota           =   Money(0,EUR)
                else:
                    new_farmaco.Quota           =   None
                if new_farmaco.Quota            !=  None:#importo calcolato su ricetta
                    new_farmaco.Tot_Assistito   =   (new_farmaco.Quota+new_farmaco.Diff)*new_farmaco.Qta
                else:#importo è uguale al prezzo al publico fuori ricetta
                    new_farmaco.Tot_Assistito   =   new_farmaco.Prezzo*new_farmaco.Qta
                    new_farmaco.Quota           =   Money(0, EUR)
                new_farmaco.Nota                =   farmaco[5]
                new_farmaco.Tk                  =   farmaco[6]
                new_farmaco.Cl                  =   farmaco[7]
                new_farmaco.Giac                =   Database.Magazzino_Principale.get_giacenza(codice_farmaco=farmaco[8])

                lista_farmaci.append(new_farmaco)

            return lista_farmaci
        def get_all_Ricetta_data_SQLITE()->list[Internal_data.Ricetta_internalData]:
            ricette = Database.execute_query(f"""
                    SELECT r.{Database.ricette.stato},
                            r.{Database.ricette.numero},
                            f1.{Database.Banca_dati.codice_aic},
                            f1.{Database.Banca_dati.descrizione_farmaco},
                            r.{Database.ricette.farmaco_1_qta},
                            f2.{Database.Banca_dati.codice_aic},
                            f2.{Database.Banca_dati.descrizione_farmaco},
                            r.{Database.ricette.farmaco_2_qta},
                            r.{Database.ricette.V},
                            r.{Database.ricette.primaryKey}
                    FROM {Database.ricette.nome} r
                    LEFT JOIN {Database.Banca_dati.nome_tabella_Farmaco[0]} f1 ON r.{Database.ricette.farmaco_1} = f1.{Database.Banca_dati.Farmaco_primarykey}
                    LEFT JOIN {Database.Banca_dati.nome_tabella_Farmaco[0]} f2 ON r.{Database.ricette.farmaco_2} = f2.{Database.Banca_dati.Farmaco_primarykey}
                    """)
            lista_ricette=[]
            for ricetta in ricette:
                #Stato: [0], Numero [1], F1_AIC [2], F1_Desc [3], F1_qta [4], F2_AIC [5], F2_Desc [6], F2_qta [7], V [8], ID_ricetta [9]
                new_ricetta=Internal_data.Ricetta_internalData()
                new_ricetta.stato=ricetta[0]
                new_ricetta.numero=ricetta[1]
                new_ricetta.farmaco_1_qta=ricetta[4]
                new_ricetta.farmaco_2_qta=ricetta[7]
                new_ricetta.V=ricetta[8]
                new_ricetta.farmaco_1_AIC=ricetta[2]
                new_ricetta.farmaco_1_Descrizione=ricetta[3]
                new_ricetta.farmaco_2_AIC=ricetta[5]
                new_ricetta.farmaco_2_Descrizione=ricetta[6]
                new_ricetta.id_ricetta=ricetta[9]
                lista_ricette.append(new_ricetta)
            return lista_ricette          
        def get_FarmacoData_for_insert_SQLITE(id_farmaco:int)->list:
            return Database.Banca_dati.cerca_farmaco(tipo_di_ricerca=Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.Farmaco_primarykey,
                                              input=id_farmaco,
                                              colonne_da_visualizzare=[Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.codice_aic,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.descrizione_farmaco,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.prezzo,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.importo_assistito,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.prezzo_rimborso,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.note,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.tipo_ricetta,
                                                                       Database.Banca_dati.nome_tabella_Farmaco[1]+"."+Database.Banca_dati.cl])[0]

        #FUNZIONI RESTORE DATA
        def DatabaseRestore_SQLITE(signal):
            inventario=Internal_data.csv_read()
            Database.Banca_dati.create_tables()
            with sqlite3.connect(Database.PATH_db) as conn:
                cursor=conn.cursor()
                for _, row in inventario.iterrows():
                    id_farmaco=Database.Banca_dati.populate_row(row=row,cursor=cursor)
                    progress_value=int(id_farmaco*100/len(inventario))
                    middlwareGui.update_progress_restoreDatabase(signal=signal,value=progress_value)
                cursor.connection.commit()

        #FUNZIONI VENDITA
        def plus_one_SQLITE(row:int):
            Database.vendita.plus_one(row=row)
        def less_one_SQLITE(row:int):
            Database.vendita.less_one(row=row)
        def delete_SQLITE(row:int):
            Database.vendita.delete(row=row)
        def close_and_numerate_ricetta_SQLITE():
            Database.vendita.close_and_numerate_ricetta()
        def farmaci_ricetta_in_corso_SQLITE()->list[Internal_data.Farmaco_vendita]:
            return Database.vendita.farmaci_ricetta_in_corso()
        def attiva_sospeso_SQLITE(row,newQta,newSosp):
            Database.vendita.attiva_sospeso(row=row,newQta=newQta,newSosp=newSosp)
        def insert_farmaco_SQLITE(id_farmaco:int,tipo_vendita:str) -> int:
            return Database.vendita.insert_farmaco(id_farmaco=id_farmaco,tipo_vendita=tipo_vendita)
        def search_farmaco_SQLITE(id:int)->int:
            """
            Dato un ID restituisce la row della vendita
            """
            return Database.vendita.search_farmaco(id=id)

        #FUNZIONI RICETTA
        def get_ricettaNumber_SQLITE(ID_ricetta:int)->int:
            return Database.ricette.get_columnValue(id=ID_ricetta,column=Database.ricette.numero)

        #FUNZIONI BANCA DATI
        def cerca_farmaco_SQLITE(input:str,tipo_di_ricerca:Enum,colonne_da_visualizzare:list[Enum])->int:
            tipo_di_ricerca=Middlware_Database.Middleware_SQLITE.convert_tipoRicercaBancadati_SQLITE(type=tipo_di_ricerca)
            colonne_da_visualizzare_convertito=[]
            for colonna in colonne_da_visualizzare:
                colonne_da_visualizzare_convertito.append(Middlware_Database.Middleware_SQLITE.convert_tipoRicercaBancadati_SQLITE(type=colonna))
            return Database.Banca_dati.cerca_farmaco(tipo_di_ricerca=tipo_di_ricerca,input=input,colonne_da_visualizzare=colonne_da_visualizzare_convertito)
    
    #Init
    def __init__(self,activeDatabase:chosenDatabaseMiddleware):
        self.chosenDatabase=activeDatabase

    #Varie funzioni principali da richiamare dall'esterno
    def get_all_FarmacoVendita_data(self)->list[Internal_data.Farmaco_vendita]:
        """
        Chiede al database utilizzato di convertire i dati presenti nella tabella di vendita di farmaci in una struttura lista di Farmaco Vendita.
        """
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            return self.Middleware_SQLITE.get_all_FarmacoVendita_data_SQLITE()  
    def get_all_Ricetta_data(self)->list[Internal_data.Ricetta_internalData]:
        """
        Chiede al database utilizzato di convertire i dati presenti nella tabella delle ricette in una struttura lista di Ricetta_internalData.
        """
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            return self.Middleware_SQLITE.get_all_Ricetta_data_SQLITE()

    #FUNZIONI RESTORE DATA
    def databaseRestore(self,update_progress):
        """
        Recupera i dati dal csv e li converte in un database.
        """
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.DatabaseRestore_SQLITE(signal=update_progress)
    
    #FUNZIONI VENDITA
    def plus_one_FarmacoVendita(self,row:int):
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.plus_one_SQLITE(row=row)
    def less_one_FarmacoVendita(self,row:int):
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.less_one_SQLITE(row=row)
    def delete_FarmacoVendita(self,row:int):
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.delete_SQLITE(row=row)
    def close_and_numerate_ricetta(self):
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.close_and_numerate_ricetta_SQLITE()
    def farmaci_ricetta_in_corso(self) -> list[Internal_data.Farmaco_vendita]:
         if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
             risposta = self.Middleware_SQLITE.farmaci_ricetta_in_corso_SQLITE()
             return risposta
    def attiva_sospeso(self,row:int,newQta:int,newSosp:int):
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            self.Middleware_SQLITE.attiva_sospeso_SQLITE(row=row,newQta=newQta,newSosp=newSosp)
    def insert_farmaco(self,id_farmaco:int,tipo_vendita:str) -> int:
        """
        Inserisce un farmaco nel database. Restituisce la riga del farmaco inserito.
        """
        #1. RECUPERO DATI CHE SERVONO SICURO tramite alcune funzioni che estragono da logica, banca dati e magazzino
            #Da Logica:
        ticket_pezzi=Internal_data.calcolo_ticket_e_npezzi(tipo_vendita=tipo_vendita)

            #Da Banca dati:
                #Recupero dati farmaco dalla banca dati e li metto in una lista così composta:
                #AIC:[0], descrizione_farmaco:[1], Prezzo:[2], Importo Assistito:[3], Prezzo_rimborso:[4], Note:[5], Tipo_ricetta[6], Cl:[7]
        bancaDati_farmaco = []
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            bancaDati_farmaco = self.Middleware_SQLITE.get_FarmacoData_for_insert_SQLITE(id_farmaco=id_farmaco)

            #Da Magazzino:
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                    Giac=Database.Magazzino_Principale.get_giacenza(codice_farmaco=id_farmaco)

            #Inseriamo nella struttura dati Farmaco:
        Farmaco=Internal_data.Farmaco_vendita(Codice_AIC=bancaDati_farmaco[0],
                                        Prodotto=bancaDati_farmaco[1],
                                        Prezzo=Money(bancaDati_farmaco[2],EUR),
                                        Importo=Money(bancaDati_farmaco[3],EUR),
                                        Pr_Rimborso=Money(bancaDati_farmaco[4],EUR),
                                        Nota=bancaDati_farmaco[5],
                                        Tk=bancaDati_farmaco[6],
                                        Cl=bancaDati_farmaco[7],
                                        Quota=ticket_pezzi[0],
                                        Giac=Giac)
        
            # Problema con Pr_Rimborso nel database:
        if Farmaco.Pr_Rimborso!=Money(0.0,EUR): #sembra che nel database i farmaci senza equivalenti abbiano un prz rimb = 0
            Farmaco.Diff=Farmaco.Prezzo-Farmaco.Pr_Rimborso
        else:
            Farmaco.Diff=Farmaco.Pr_Rimborso #quindi in questi casi il prezzo rimborso deve essere = Diff per non far pagare nulla
            #------------------------------------------

        Farmaco.Qta=1 #per il momento
        Farmaco.Sosp=0 #per il momento
        
        #controllo se conviene tariffare
        if tipo_vendita!="L" and Farmaco.Cl=="A" and not Farmaco.Prezzo>Farmaco.Quota+Farmaco.Diff:
                #non conviene tariffare quindi metto in libera con allert
                tipo_vendita="L"
                middlwareGui.chiamaDialgInfo(textBox="Non conviene tariffare.\nIl farmaco viene inserito in vendita libera.")

        #2. RECUPERO I DATI CHE SERVONO IN BASE AL TIPO DI VENDITA

            #VENDITA SU RICETTA
        if tipo_vendita!="L" and Farmaco.Cl=="A":

                        #nuova ricetta
            if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                f_ricetta = Database.vendita.rows_farmaci_ricettaInCorso()
                Farmaco.Pr = Database.vendita.get_progressivo_ricetta()

            n_riga=None #Se n_riga=None aggiungerà una riga alla tabella

            if len(f_ricetta)==0:
                Farmaco.Pr=Farmaco.Pr+1
                if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                    Farmaco.ID_Ricetta=Database.ricette.open_new_ricetta(V=tipo_vendita,id_farmaco=id_farmaco)

            else:    #ricetta in corso
                f_ricetta=self.farmaci_ricetta_in_corso()
                Farmaco.ID_Ricetta=f_ricetta[0].ID_Ricetta #tutti i farmaci hanno lo stesso ID ricetta.
                if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                    Database.ricette.add_farmaco_ricetta(id_ricetta=Farmaco.ID_Ricetta,id_farmaco=id_farmaco)
                
                qta_pezzi_ricetta=0 #contatore della quantità totale di farmaci in ricetta
                #controllo max 2 differenti farmaci e contemporaneamente la qt totale di farmaci in ricetta.
                for f in f_ricetta:
                    if Farmaco.Codice_AIC==f.Codice_AIC: #se ricetta in corso e trovi una riga con lui allora si può aggiungere
                        n_riga=f.Progressivo_riga
                        Farmaco.Qta=f.Qta+1 #se lo trova allora inserisce già la quantità finale
                    qta_pezzi_ricetta+=f.Qta
                if n_riga==None:
                    if len(f_ricetta)==2: # 2 farmaci già in ricetta e nessuno è quello da inserire: NON SI PUO'
                        middlwareGui.chiamaDialgInfo(textBox="Massimo 2 specialità inseribili in una ricetta.")
                        return -1 #Chiudo l'inserimento con codice -1 -> Riferirà "troppi farmaci in ricetta"    
                
                #controllo se chiudere e numerare la ricetta
                if qta_pezzi_ricetta+1>=ticket_pezzi[1]: #se inserendo questo farmaco si arriva al limite di pezzi in ricetta per il tipo di vendita allora chiudi la ricetta
                    if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                        Database.ricette.close_ricetta()
                                 
        else: #VENDITA LIBERA                
            tipo_vendita="L"
            #Cercare se c'è una riga in libera con lo stesso farmaco così non aggiungo una riga ma aggiorno quella
            if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                f_vendita = self.Middleware_SQLITE.get_all_FarmacoVendita_data_SQLITE()
            n_riga=None
            for f in f_vendita:
                if f.Codice_AIC == Farmaco.Codice_AIC and f.V == "L":
                    n_riga = f.Progressivo_riga
                    Farmaco.Qta+=f.Qta

        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            Database.vendita.add_or_update_Farmaco(codice_farmaco=id_farmaco,tipo_vendita=tipo_vendita,progressivo_ricetta=Farmaco.Pr,id_ricetta=Farmaco.ID_Ricetta,
                                            quantità=Farmaco.Qta,sospesi=Farmaco.Sosp,n_riga=n_riga)
        if n_riga==None:
            if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
                n_riga=self.Middleware_SQLITE.search_farmaco_SQLITE(id=id_farmaco)
        return n_riga-1

    #FUNZIONI RICETTA
    def get_ricettaNumber(self,ID_ricetta:int)->int:
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            return self.Middleware_SQLITE.get_ricettaNumber_SQLITE(ID_ricetta=ID_ricetta)

    #FUNZIONI BANCA DATI
    def cerca_farmaco(self,input:str,tipo_di_ricerca:Enum,colonne_da_visualizzare:list[Enum])->int:
        if self.chosenDatabase==self.chosenDatabaseMiddleware.SQLITE:
            return self.Middleware_SQLITE.cerca_farmaco_SQLITE(input=input,tipo_di_ricerca=tipo_di_ricerca,colonne_da_visualizzare=colonne_da_visualizzare)
            
middlwareDatabase = Middlware_Database(activeDatabase=Middlware_Database.chosenDatabaseMiddleware.SQLITE)


