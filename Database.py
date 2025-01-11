from __future__ import annotations
import sqlite3
import Internal_data
from moneyed import Money, EUR
import Middleware
from enum import Enum

PATH_db="Data//Database.db"


def execute_query(query: str, commit: bool=False, values: tuple=(), dict_result=False, getROWIDbyInsert=False) -> list[any]:
    """
    Data una lista di query, verranno esseguite. Opzionale: commit->scrivere su file, values->se la query presenta dei ?,
    dict_result->se si vuole ottenere una list[{dict: (tuple)...},..] anziché una list[list[(tuple)..],...]

    """
    try:
        with sqlite3.connect(PATH_db) as conn:
            if dict_result:
                conn.row_factory = sqlite3.Row
            cursor=conn.cursor()
            cursor.execute(query,values)
            if getROWIDbyInsert:
                risposta=cursor.lastrowid
            else:   
                risposta=cursor.fetchall()
            if commit:
                conn.commit()
    except sqlite3.Error as e:
        print(e)
    return risposta

class Banca_Dati():
# Inizializzation
    def __init__(self):
        #tupla con nomi e prefissi tabelle
        self.nome_tabella_Farmaco=("Farmaco","f")
        self.nome_tabella_Azienda=("Azienda","a")
        #nomi colonne tabella Farmaco
        self.Farmaco_primarykey="Codice"
        self.codice_aic="Codice_AIC"
        self.descrizione_farmaco="Descrizione_prodotto"
        self.forma_farmaceutica="Forma_farmaceutica"
        self.principio_attivo="Principio_Attivo"
        self.atc="ATC_Descrizione"
        self.cod_gruppo="Cod_gruppo"
        self.descrizione_gruppo="Descrizione_gruppo"
        self.tipo_prodotto="Tipo_prodotto"
        self.doping="Doping"
        self.glutine="Glutine"
        self.stupefacente="Stupefacente"
        self.temperatura="Temperatura"
        self.mesi_validità="Mesi_validita"
        self.validità_dopo_apertura="Validita_dopo_apertura"
        self.iva="Iva"
        self.prezzo="Prz_Att"
        self.importo_assistito="Imp_Assist"
        self.prezzo_rimborso="Prz_RimE"
        self.obbligatorietà="Obbligatorieta"
        self.particolarità="Particolarita"
        self.cl="Cl"
        self.prescrivibilità="Prescrivibilita"
        self.tipo_ricetta="Tipo_ricetta"
        self.regime_SSN="Regime_SSN"
        self.note="Note_prescrizione"
        self.codice_azienda="Codice_Azienda"
        #nomi colonne tabella Azienda
        self.Azienda_primarykey="Codice"
        self.nome_azienda="Nome"
        self.importazione="Import"
    def create_tables(self):
        query=[f"""
                DROP TABLE IF EXISTS {self.nome_tabella_Farmaco[0]};""",
                    f"""
                CREATE TABLE {self.nome_tabella_Farmaco[0]} (
                {self.Farmaco_primarykey} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.codice_aic} TEXT,
                {self.descrizione_farmaco} TEXT,
                {self.forma_farmaceutica} TEXT,
                {self.principio_attivo} TEXT,
                {self.atc} TEXT,
                {self.cod_gruppo} TEXT,
                {self.descrizione_gruppo} TEXT,
                {self.tipo_prodotto} TEXT,
                {self.doping} TEXT,
                {self.glutine} TEXT,
                {self.stupefacente} TEXT,
                {self.temperatura} TEXT,
                {self.mesi_validità} TEXT,
                {self.validità_dopo_apertura} TEXT,
                {self.iva} TEXT,
                {self.prezzo} TEXT,
                {self.importo_assistito} TEXT,
                {self.prezzo_rimborso} TEXT,
                {self.obbligatorietà} TEXT,
                {self.particolarità} TEXT,
                {self.cl} TEXT,
                {self.prescrivibilità} TEXT,
                {self.tipo_ricetta} TEXT,
                {self.regime_SSN} TEXT,
                {self.note} TEXT,
                {self.codice_azienda} INTEGER,
                FOREIGN KEY ({self.codice_azienda}) REFERENCES {self.nome_tabella_Azienda[0]}({self.Azienda_primarykey})
                );""",
                f"""
                DROP TABLE IF EXISTS {self.nome_tabella_Azienda[0]};""",           
                f"""
                CREATE TABLE {self.nome_tabella_Azienda[0]} (
                {self.Azienda_primarykey} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.nome_azienda} TEXT,
                {self.importazione} TEXT
                );"""]
        for q in query:
            execute_query(query=q,commit=True)

#Populate table  
    def check_integrity(self)->bool:
        """
        Controlla che le tabelle contenute all'interno della sua classe siano state create nel database.
        Restituisce True se è tutto ok e false se manca qualcosa.
        """
        tables=execute_query(f"""
            SELECT name 
            FROM sqlite_master 
            WHERE type = 'table'; 
            """)
        count=0
        n_table=2 #tabella Farmaco e Azienda
        for table in tables:
            if table[0] == self.nome_tabella_Farmaco[0] or table[0]== self.nome_tabella_Azienda[0]:
                count=count+1
        if count==n_table:
            return True
        return False
    def populate_row(self, row, cursor):
        id_azienda=self.__insert_or_get_Azienda(cursor, row["Ditta produttrice"])
        id_farmaco=self.__insert_data(cursor=cursor,Codice_AIC=row["Codice AIC"],Descrizione_prodotto=row["Descrizione prodotto"],
                                            Forma_farmaceutica=row["Forma farmaceutica"],Principio_Attivo=row["Principio Attivo"],
                                            ATC_Descrizione=row["A.T.C. Descrizione"],Cod_gruppo=row["Cod. gruppo"],Descrizione_gruppo=row["Descrizione gruppo"],
                                            Tipo_prodotto=row["Tipo prodotto"],Doping=row["Doping"],Glutine=row["Glutine"],Stupefacente=row["Stupefacente"],
                                            Temperatura=row["Temperatura"],Mesi_di_validità=row["Mesi di validita'"],Validità_dopo_apertura=row["Validita' dopo apertura"],
                                            Iva=row["Iva"], Prz_Att=row["Prz. Att."],Imp_Assist=row["Imp.Assist"],PrzRimE=row["PrzRimE."],
                                            Obbligatorietà=row["Obbligatorieta'"],Particolarità=row["Particolarita'"],Cl=row["Cl"],Prescrivibilità=row["Prescrivibilita'"],
                                            Tipo_ricetta=row["Tipo ricetta"],Regime_SSN=row["Regime SSN"],Note_prescrizione=row["Note prescrizione"],
                                            codice_azienda=id_azienda)
        return id_farmaco      
    def __insert_or_get_Azienda(self, cursor: sqlite3.Cursor, nome:str):
        lista_import=self.__get_lista_import()
        importazione=False
        for ditta_import in lista_import:
            if nome==ditta_import:
                importazione=True
        try:
            cursor.execute(f"SELECT {self.Azienda_primarykey}, {self.nome_azienda} FROM {self.nome_tabella_Azienda[0]} WHERE {self.nome_azienda} = ?", (nome,))
            row=cursor.fetchone() #Se lo trova la row non è None e quindi restituisce risultato
            if row:
                return row[0]
            
            sql=f"INSERT INTO {self.nome_tabella_Azienda[0]}({self.nome_azienda}, {self.importazione}) VALUES(?,?)"
            cursor.execute(sql, (nome, importazione)) #Se None allora l'aggiunge
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)  
    def __insert_data(self, cursor: sqlite3.Cursor, Codice_AIC: str, Descrizione_prodotto:str, Forma_farmaceutica: str, Principio_Attivo:str, ATC_Descrizione:str,
                      Cod_gruppo:str, Descrizione_gruppo:str, Tipo_prodotto:str, Doping: str, Glutine:str, Stupefacente:str, Temperatura:str, 
                      Mesi_di_validità:str, Validità_dopo_apertura:str, Iva:str, Prz_Att:str, Imp_Assist:str, PrzRimE:str, Obbligatorietà:str, Particolarità:str, Cl: str,
                      Prescrivibilità:str, Tipo_ricetta:str, Regime_SSN:str, Note_prescrizione:str,codice_azienda:int):           
        try:
            cursor.execute(f"SELECT {self.Farmaco_primarykey} FROM {self.nome_tabella_Farmaco[0]} WHERE '{self.codice_aic}' = ?", (Codice_AIC,))
            row=cursor.fetchone() #Se lo trova la row non è None e quindi restituisce risultato
            if row:#AIC già presente
                return row[0]
            #Nuovo farmaco da inserire
            query=f"""
            INSERT INTO {self.nome_tabella_Farmaco[0]}({self.codice_aic},{self.descrizione_farmaco},{self.forma_farmaceutica},{self.principio_attivo},
                {self.atc},{self.cod_gruppo},{self.descrizione_gruppo},{self.tipo_prodotto},{self.doping},{self.glutine},{self.stupefacente},{self.temperatura},
                {self.mesi_validità},{self.validità_dopo_apertura},{self.iva},{self.prezzo},{self.importo_assistito},{self.prezzo_rimborso},
                {self.obbligatorietà},{self.particolarità},{self.cl},{self.prescrivibilità},{self.tipo_ricetta},{self.regime_SSN},
                {self.note},{self.codice_azienda}) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """
            cursor.execute(query,(Codice_AIC,Descrizione_prodotto,Forma_farmaceutica,Principio_Attivo,ATC_Descrizione,Cod_gruppo,
                                Descrizione_gruppo,Tipo_prodotto,Doping,Glutine,Stupefacente,Temperatura,Mesi_di_validità,
                                Validità_dopo_apertura,Iva,Prz_Att,Imp_Assist,PrzRimE,Obbligatorietà,Particolarità,Cl,
                                Prescrivibilità,Tipo_ricetta,Regime_SSN,Note_prescrizione,codice_azienda))
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(e)
    
    #Funzioni di ricerca
    def cerca_farmaco(self, tipo_di_ricerca,input,colonne_da_visualizzare):
        colonne=""
        for colonna in colonne_da_visualizzare:
            colonne=colonne+colonna+", "
        colonne=colonne.strip(", ")
        query=f"""
                SELECT {colonne}
                FROM {self.nome_tabella_Farmaco[0]} {self.nome_tabella_Farmaco[1]} 
                JOIN {self.nome_tabella_Azienda[0]} {self.nome_tabella_Azienda[1]} ON {self.nome_tabella_Farmaco[1]}.{self.codice_azienda}={self.nome_tabella_Azienda[1]}.{self.Azienda_primarykey}
                WHERE {tipo_di_ricerca} LIKE '{input}%'
                """
        return execute_query(query=query)
    
    #Funzioni private
    def __get_lista_import(self)->list[str]:
        return ["PRICETAG SpA","BB FARMA Srl","PROGRAMMI SANIT.INTEGRATI Srl",
                    "MEDIFARM Srl","FARMA 1000 Srl","GEKOFAR Srl","FARMAROC Srl","NEW PHARMASHOP Srl",
                    "FARMAVOX Srl","GENERAL PHARMA SOLUTIONS SpA","GMM FARMA Srl","FARMED Srl","DIFARMED S.L.","SM PHARMA Srl",
                    "PRICETAG SpA"]
Banca_dati = Banca_Dati()        

class Magazzino():
    def __init__(self, nome: str):
        #Nome tabella
        self.nome=nome
        #Colonne
        self.primaryKey="Codice"
        self.referencesToBancaDati="Codice_Farmaco"
        self.quantity="Giacenza"
        self.create_table()
    def create_table(self):
        query=f"""
                CREATE TABLE IF NOT EXISTS {self.nome} (
                {self.primaryKey} INTEGER PRIMARY KEY AUTOINCREMENT,
                {self.referencesToBancaDati} INTEGER,
                {self.quantity} INTEGER,
                FOREIGN KEY ({self.referencesToBancaDati}) REFERENCES {Banca_dati.nome_tabella_Farmaco[0]}({Banca_dati.Farmaco_primarykey})
                );"""
        execute_query(query=query,commit=True)   
    def add_Farmaco(self,codice_farmaco: int, quantità: int):
        #controllare se già presente in magazzino
        query=f"""
                SELECT {self.referencesToBancaDati}
                FROM {self.nome}
                WHERE {self.referencesToBancaDati} = '{codice_farmaco}'"""
        risposta=execute_query(query)
        if len(risposta)== 0: #non presente
            query=f"INSERT INTO {self.nome}({self.referencesToBancaDati},{self.quantity}) VALUES(?,?)"
            execute_query(query=query,values=(codice_farmaco,quantità),commit=True)
        else: #Già presente
            query=f"UPDATE {self.nome} SET {self.quantity}={self.quantity}+? WHERE {self.referencesToBancaDati}=?"
            execute_query(query=query,values=(quantità,codice_farmaco),commit=True)
    def remove_Farmaco(self,codice_farmaco:int, quantità:int):
        self.add_Farmaco(codice_farmaco=codice_farmaco,quantità=(quantità*-1))
    def move_Farmaco(self,codice_farmaco: int, quantità: int, magazzino_dest: Magazzino):
        self.remove_Farmaco(codice_farmaco=codice_farmaco,quantità=quantità)
        magazzino_dest.add_Farmaco(codice_farmaco=codice_farmaco,quantità=quantità)      
    def in_magazzino(self,codice_farmaco) -> bool:
        query=f"""SELECT {self.referencesToBancaDati}
                FROM {self.nome}
                WHERE {self.referencesToBancaDati} = ?"""
        risposta = execute_query(query=query,values=(codice_farmaco,))
        if risposta:
            return True
        return False
    def get_giacenza(self,codice_farmaco)-> int:
        #prima verifico che sia in magazzino
        if self.in_magazzino(codice_farmaco=codice_farmaco):#se in magazzino cerco la giacenza
            query=f"""
                    SELECT {self.quantity}
                    FROM {self.nome}
                    WHERE {self.referencesToBancaDati}={codice_farmaco}
                    """
            giacenza = execute_query(query)
            return giacenza[0][0]
        #altrimenti rispondo 0
        return 0   
Magazzino_Principale = Magazzino("Principale")

class Ricette():   
    def __init__(self):
        #Dati Tabella
            #nome tabella
        self.nome="Ricette"
            #colonne
        self.primaryKey="ID"
        self.stato="Stato" # da definire i vari stati
        self.numero="Numero"
        self.V="Esenzione"
        self.farmaco_1 = "Farmaco_1"
        self.farmaco_1_qta = "Farmaco_1_Qta"
        self.farmaco_2 = "Farmaco_2"
        self.farmaco_2_qta = "Farmaco_2_Qta"

        #Crea Tabella
        query=f"""
            CREATE TABLE IF NOT EXISTS {self.nome} (
            {self.primaryKey} INTEGER PRIMARY KEY AUTOINCREMENT,
            {self.stato} TEXT,
            {self.numero} INTEGER,
            {self.V} TEXT,
            {self.farmaco_1} INTEGER,
            {self.farmaco_1_qta} INTEGER,
            {self.farmaco_2} INTEGER,
            {self.farmaco_2_qta} INTEGER,
            FOREIGN KEY ({self.farmaco_1}) REFERENCES {Banca_dati.nome_tabella_Farmaco[0]}({Banca_dati.Farmaco_primarykey}),
            FOREIGN KEY ({self.farmaco_2}) REFERENCES {Banca_dati.nome_tabella_Farmaco[0]}({Banca_dati.Farmaco_primarykey}));"""
        execute_query(query=query,commit=True)       
    class StatoRicetta(Enum):
        APERTO = "Aperto"
        CHIUSO = "Chiuso"
        SOSPESO = "Sospeso"
    def open_new_ricetta(self,V:str,id_farmaco:int)->int:
        """
        Crea una nuova row nella tabella delle ricette. Si inserisce lo stato di APERTO, il primo farmaco inserito con qta 1.
        La funzione restituisce il valore della primaryKey generata.
        """
        query=f"INSERT INTO {self.nome}({self.stato},{self.numero},{self.V},{self.farmaco_1},{self.farmaco_1_qta},{self.farmaco_2},{self.farmaco_2_qta}) VALUES(?,?,?,?,?,?,?)"
        risposta=execute_query(query=query,values=(ricette.StatoRicetta.APERTO.value,None,V,id_farmaco,1,None,0),commit=True,getROWIDbyInsert=True)
        return risposta  
    def add_farmaco_ricetta(self,id_ricetta:int,id_farmaco,qta:int=1):
        query=f"SELECT {self.farmaco_1},{self.farmaco_1_qta},{self.farmaco_2},{self.farmaco_2_qta},{self.V} FROM {self.nome} WHERE {self.primaryKey}=?"
        f1_f2=execute_query(query=query,values=(id_ricetta,))[0]
        #[0] f1 [1]f1 qta [2]f2 [3]f2 qta [4] V
        if f1_f2[0]==id_farmaco:
            self.update_ricetta(ID_Ricetta=id_ricetta,Farmaco_1_qta=f1_f2[1]+qta)
        else:
            self.update_ricetta(ID_Ricetta=id_ricetta,Farmaco_2=id_farmaco,Farmaco_2_qta=f1_f2[3]+qta)
    def close_ricetta(self):
        """
        Cambia lo stato della ricetta in Chiuso, Assegna numerazione e restituisce il numero assegnato
        """
        id=execute_query(f"SELECT {self.primaryKey} FROM {self.nome} WHERE {self.stato}=?",values=(self.StatoRicetta.APERTO.value,))
        if len(id)>0:
            id=id[0][0]
        else:
            return None #Nessuna ricetta in corso. Non dovrebbe mai succedere
        numero=1 #per ora sempre 1
        self.update_ricetta(ID_Ricetta=id,stato=self.StatoRicetta.CHIUSO.value,Numero=numero)
        return numero
    def get_columnValue(self,id:int,column:str)->str:
        """
        Restituisce lo stato della ricetta richiesta tramite ID (PrimaryKey). Se la ricetta non è presente restituisce None
        """
        if id==None:
            return None
        return execute_query(f"SELECT {column} FROM {self.nome} WHERE {self.primaryKey}={id}")[0][0]
    def get_V_ricettaAperta(self)->str:
        """
        Tenendo conto che al momento solo 1 ricetta è aperta alla volta. Restituisco l'esenzione impostata di quella in corso (Aperta)
        """
        risposta = execute_query(f"SELECT {self.V} FROM {self.nome} WHERE {self.stato}='{self.StatoRicetta.APERTO.value}'")
        if risposta: #trovata almeno 1 aperta
            return risposta[0][0] #1 sola ricetta aperta possibile e 1 solo risultato della select quindi [0][0]
        else:
            return None
    def update_ricetta(self,ID_Ricetta,stato=None,Numero=None,V=None,Farmaco_1=None,Farmaco_1_qta=None,Farmaco_2=None,Farmaco_2_qta=None):
        """
        Inserire ID Ricetta da modificare. Inserire valore/i da modificare. Quelli non specificati verranno lasciati così come sono
        """
        #valori di input messi in una lista nello stesso ordine in cui vengono richiamati quelli esistenti dalla query
        lista_colonne=(stato,Numero,V,Farmaco_1,Farmaco_1_qta,Farmaco_2,Farmaco_2_qta)
        risposta=execute_query(f"""   SELECT {self.stato},{self.numero},{self.V},{self.farmaco_1},{self.farmaco_1_qta},
                                            {self.farmaco_2},{self.farmaco_2_qta}
                                    FROM {self.nome}
                                    WHERE {self.primaryKey}=?
                            """,values=(ID_Ricetta,))[0]
        values = [x for x in risposta]
        values.append(ID_Ricetta)
        for v in range(len(lista_colonne)):
            if lista_colonne[v]!=None:
                values[v]=lista_colonne[v]
        if values[4]==0: #Farmaco_1_qta
            if values[6]!=0:
                #Sposto farmaco 2 in farmaco 1 ed elimino il 2
                values[3]=values[5] #F1     =   F2
                values[4]=values[6] #F1_qta =   F2_qta
                values[5]=None      #F2     =   None
                values[6]=0         #F2_qta =   0
            else:
                values[3]=None      #F1     =   None
        if values[6]==0: #Farmaco_2_qta
            values[5]=None #Niente più farmaco 2
        if values[3]==None and values[5]==None: #Se niente farmaco 1 e 2 = Niente ricetta
            #niente ricetta
            query=f"DELETE FROM {self.nome} WHERE {self.primaryKey}={ID_Ricetta}"
            execute_query(query=query,commit=True)
        else: #altrimenti aggiorna e basta
            query=f"UPDATE {self.nome} SET {self.stato}=?,{self.numero}=?,{self.V}=?,{self.farmaco_1}=?,{self.farmaco_1_qta}=?,{self.farmaco_2}=?,{self.farmaco_2_qta}=? WHERE {self.primaryKey}=?"
            execute_query(query=query,values=values,commit=True)
ricette=Ricette()  

class Vendita():
    def __init__(self):  
        #Nome tabella
        self.nome="Vendita"
        #Colonne
            #dati essenziali per ripristinare la vendita
        self.referencesToBancaDati="Codice_Farmaco"
        self.tipo_vendita="V"
        self.numero_progressivo_ricetta="Pr"
        self.referencesToRicette="ID_Ricetta"
        self.quantità="Qt"
        self.sospesi="Sosp"
        self.create_table()
    def create_table(self):
        query=f"""
            CREATE TABLE IF NOT EXISTS {self.nome} (
            {self.referencesToBancaDati} INTEGER,
            {self.tipo_vendita} TEXT,
            {self.numero_progressivo_ricetta} INTEGER,
            {self.referencesToRicette} INTEGER,
            {self.quantità} INTEGER,
            {self.sospesi} INTEGER,
            FOREIGN KEY ({self.referencesToBancaDati}) REFERENCES {Banca_dati.nome_tabella_Farmaco[0]}({Banca_dati.Farmaco_primarykey}),
            FOREIGN KEY ({self.referencesToRicette}) REFERENCES {ricette.nome}({ricette.primaryKey})
            );"""
        execute_query(query=query,commit=True)
    def rows_farmaci_ricettaInCorso(self)->list[int]:
        risposta=execute_query( f"""SELECT {self.nome}.ROWID
                                    FROM {self.nome}
                                    JOIN {ricette.nome} ON {self.nome}.{self.referencesToRicette} = {ricette.nome}.{ricette.primaryKey}
                                    WHERE {ricette.nome}.{ricette.stato}='{ricette.StatoRicetta.APERTO.value}'""")
        if len(risposta)>0:
            risposta = [x[0] for x in risposta]
        return risposta
    def calcolo_ticket_e_npezzi(self,tipo_vendita:str)->tuple[Money,int]:
        """
        A codice carattere associo una lista: [ticket,npezzi]
        """
        if tipo_vendita=="S":#soggetta
            return (Money(2,EUR),2)
        elif tipo_vendita=="K":
            return (Money(1,EUR),2)
        elif tipo_vendita=="Y": #K->2pz Y->6pz
            return (Money(1,EUR),6)
        elif tipo_vendita=="O":
            return (Money(0,EUR),2)
        elif tipo_vendita=="A": #O->2pz A->6pz
            return (Money(0,EUR),6)
        else:
            return (Money(-1,EUR),-1) #Libera
    def add_or_update_Farmaco(self,codice_farmaco: int,tipo_vendita: str,progressivo_ricetta: int,id_ricetta: int,quantità: int,sospesi: int,n_riga:int=None):
        """
        Inserisce una nuova riga alla tabella di un farmaco oppure, se specificata, aggiorna una riga esistente
        """
        if n_riga==None:
            delta=quantità
            query=f"INSERT INTO {self.nome}({self.referencesToBancaDati},{self.tipo_vendita},{self.numero_progressivo_ricetta},{self.referencesToRicette},{self.quantità},{self.sospesi}) VALUES(?,?,?,?,?,?)"
            execute_query(query=query,values=(codice_farmaco,tipo_vendita,progressivo_ricetta,id_ricetta,quantità,sospesi),commit=True)
        elif n_riga>=0:
            query=f"SELECT {self.quantità} FROM {self.nome} WHERE ROWID = ?"
            quantità_attuale=execute_query(query=query,values=(n_riga,))[0][0]
            delta=quantità-quantità_attuale
            query=f"UPDATE {self.nome} SET {self.referencesToBancaDati}=?,{self.tipo_vendita}=?,{self.numero_progressivo_ricetta}=?,{self.referencesToRicette}=?,{self.quantità}=?,{self.sospesi}=? WHERE ROWID=?"
            execute_query(query=query,values=(codice_farmaco,tipo_vendita,progressivo_ricetta,id_ricetta,quantità,sospesi,n_riga),commit=True)
        
        #Aggiorno giacenza magazzino principale
        Magazzino_Principale.remove_Farmaco(codice_farmaco=codice_farmaco,quantità=delta)
    def delete_rows(self,rows:list[int]):
        # Sistemiamo i progressivi ricetta: Pr
            #anche se cancella più righe, cancella sempre una sola Pr. Dalla prima riga da cancellare in poi diminuiamo di 1 il Pr delle prossime
        if rows:
            listaFarmaciVendita=execute_query(query=f"SELECT * FROM {self.nome}")            
            for i in range(rows[0]+1, len(listaFarmaciVendita)):               
                #[0]: ID, [1]:V, [2]:Pr, [3]: N.Ricetta, [4]:Qt [5]:Sospesi
                if listaFarmaciVendita[i][2]!=None: #Devono essere ricette chiuse
                    self.add_or_update_Farmaco(codice_farmaco=listaFarmaciVendita[i][0],tipo_vendita=listaFarmaciVendita[i][1],
                                            progressivo_ricetta=listaFarmaciVendita[i][2]-1, id_ricetta=listaFarmaciVendita[i][3],
                                            quantità=listaFarmaciVendita[i][4],sospesi=listaFarmaciVendita[i][5],n_riga=i+1)
        listaFarmaciVendita=execute_query(query=f"SELECT * FROM {self.nome}")
        # Eliminiamo effettivamente le righe
        for row in rows:
            row=row+1
            quantità_codice=execute_query(f"SELECT {self.quantità},{self.referencesToBancaDati} FROM {self.nome} WHERE ROWID=?",values=(row,))[0]
            Magazzino_Principale.add_Farmaco(codice_farmaco=quantità_codice[1],quantità=quantità_codice[0])
            query=f"DELETE FROM {self.nome} WHERE ROWID = ?"
            execute_query(query=query,values=str(row),commit=True)
        listaFarmaciVendita=execute_query(query=f"SELECT * FROM {self.nome}")
        # Aggiorno le ROWID
        self.update_rowid()        
    def exit_restore(self,magazzino: Magazzino):
        """
        Ripristina in magazzino dato in input(principale sicuramente) tutte le giacenze ed elimina le ricette erogate.
        """
        query=f"""
                SELECT {self.referencesToBancaDati},{self.quantità}
                FROM {self.nome} v
                JOIN {Banca_dati.nome_tabella_Farmaco} f ON v.{self.referencesToBancaDati}=f.{Banca_dati.Farmaco_primarykey}
               """
        elenco_farmaci=execute_query(query=query) # [(codiceFarmaco,quantità),(...)...]
        for farmaco in elenco_farmaci:
            magazzino.add_Farmaco(codice_farmaco=farmaco[0],quantità=farmaco[1]) #aggiungo tutti i farmaci messi in vendita al magazzino
        execute_query(f"DELETE FROM {self.nome}",commit=True) #clear della tabella vendita
        #da implementare l'eliminazione delle ricette, quando avrò implementato le ricette
    def get_progressivo_ricetta(self):
        risposta=execute_query(f"SELECT MAX({self.numero_progressivo_ricetta}) FROM {self.nome}")
        risposta=risposta[0] #risposta della query è solo una
        if risposta[0]==None:
            r=0
        else:
            r=risposta[0]
        return r
    def farmaci_ricetta_in_corso(self)->list[Internal_data.Farmaco_vendita]:
        """
        Restituiscie i farmaci nella ricetta in corso, completi di tutte le info della riga
        """
        risposta = self.rows_farmaci_ricettaInCorso() #dà la row non l'indice della row
        f_vendita = Middleware.middlwareDatabase.get_all_FarmacoVendita_data()
        returning = [f_vendita[x-1] for x in risposta]
        return returning       
    def close_and_numerate_ricetta(self)->int:
        """
        Restituisce il numero di ricetta
        """
        #da implementare. Trovo il prossimo numero di ricetta da assegnare
        N_Ricetta=ricette.close_ricetta()
        f_ricetta=self.farmaci_ricetta_in_corso()
        for f in f_ricetta: #assegna numerazione a tutti i farmaci nella ricetta. Per ora assegno solo il numero 1
            r=execute_query(f"SELECT {Banca_dati.Farmaco_primarykey} FROM {Banca_dati.nome_tabella_Farmaco[0]} WHERE {Banca_dati.codice_aic}='{f.Codice_AIC}'")
            r=r[0]
            self.add_or_update_Farmaco(codice_farmaco=r[0],tipo_vendita=f.V,progressivo_ricetta=f.Pr,id_ricetta=N_Ricetta,
                            quantità=f.Qta,sospesi=f.Sosp,n_riga=f.Progressivo_riga)    
        #da implementare ricette
        return N_Ricetta
    def update_rowid(self):
        risultato=execute_query(f"SELECT *, ROWID FROM {self.nome}")
        for i, row in enumerate(risultato,start=1):
             #[0]: ID, [1]:V, [2]:Pr, [3]: N.Ricetta, [4]:Qt [5]:Sosp [6]:ROWID
            execute_query(query=f"UPDATE {self.nome} SET ROWID=? WHERE ROWID = ?",values=(i,row[6]),commit=True)
        #TEST
        risultato=execute_query(f"SELECT *, ROWID FROM {self.nome}")
        risultato
    def check_ConvieneTariffare(self,prezzo_farmaco:int, ticket:int):
        if prezzo_farmaco>ticket:
            return True
        return False
    def get_nRicetta(self,row:int)->int:
        risposta=execute_query(f"""
                                SELECT {ricette.nome}.{ricette.numero}
                                FROM {ricette.nome}
                                JOIN {self.nome} ON {ricette.nome}.{ricette.primaryKey} = {self.referencesToRicette}
                                WHERE {self.nome}.ROWID = {row} 
                               """)
        return risposta[0][0]
    def search_farmaco(self,id:int)->int:
        risposta = execute_query(f"""
                                    SELECT ROWID
                                    FROM {self.nome}
                                    WHERE {self.referencesToBancaDati} = {id}
                                 """)
        if len(risposta)>0:
            risposta=risposta[0][0]
        else:
            risposta = -1
        return risposta

#Metodi principale
    def plus_one(self,row:int)->int:
        risultato=execute_query(f"SELECT * FROM {self.nome}")
        risultato=risultato[row] #[0]: ID, [1]:V, [2]:Pr, [3]: ID_Ricetta, [4]:Qt
        stato_ricetta = ricette.get_columnValue(risultato[3],ricette.stato)
        if risultato[1]!="L" and stato_ricetta!=ricette.StatoRicetta.APERTO.value: #ricetta rossa chiusa = nulla da aggiungere
            return -1
        else: #tutti gli altri casi prova un inserimento classico. Come tipo di vendita usare quello della riga selezionata
            Middleware.middlwareDatabase.insert_farmaco(id_farmaco=risultato[0],tipo_vendita=risultato[1])
    def less_one(self,row:int)->int:
        risultato=execute_query(f"SELECT *, ROWID FROM {self.nome}")
        risultato=risultato[row] #[0]: ID, [1]:V, [2]:Pr, [3]: ID_Ricetta, [4]:Qt [5]:Sosp [6]:ROWID
        stato_ricetta = ricette.get_columnValue(risultato[3],ricette.stato)
        if risultato[1]!="L" and stato_ricetta!=ricette.StatoRicetta.APERTO.value: #ricetta rossa chiusa = Non fare nulla
            return -1
        #in teoria in tutti gli altri casi (ricetta rossa in corso o vendita libera) può agire allo stesso modo
            #distinguiamo se aggiornare o eliminare la riga
        if risultato[4]>1: # più di 1 elemento = decrementa di 1 la qt
            self.add_or_update_Farmaco(codice_farmaco=risultato[0],tipo_vendita=risultato[1],progressivo_ricetta=risultato[2],
                                       id_ricetta=risultato[3],quantità=risultato[4]-1,sospesi=risultato[5],n_riga=risultato[6])
        else: # solo 1 elemento = elimina riga
           self.delete_rows(rows=[row])
        if risultato[3]: #se associato ad una ricetta, rimuovo il farmaco dalla ricetta.
            ricette.add_farmaco_ricetta(id_ricetta=risultato[3],id_farmaco=risultato[0],qta=-1)
    def delete(self,row:int):
        risultato=execute_query(f"SELECT {self.referencesToBancaDati},{self.tipo_vendita},{self.numero_progressivo_ricetta},{self.referencesToRicette}, ROWID FROM {self.nome}")
        risultato=risultato[row] #[0]: Codice_Farmaco, [1]: V, [2]:Pr, [3]: ID_Ricetta, [4]: ROWID
        statoRicetta = ricette.get_columnValue(id=risultato[3],column=ricette.stato)

        if risultato[1]!="L" and (statoRicetta==ricette.StatoRicetta.CHIUSO.value or statoRicetta==ricette.StatoRicetta.SOSPESO.value):
            #Ricetta rossa chiusa: Eliminare tutte le righe della ricetta
                #Da gestire l'eliminazione dei sospesi in caso presenti
            ricette.update_ricetta(risultato[3],Farmaco_1_qta=0,Farmaco_2_qta=0)
            farmaciInRicetta=execute_query(f"SELECT *, ROWID FROM {self.nome} WHERE {self.numero_progressivo_ricetta}= ?",values=(risultato[2],))
            lista_f=[]
            for f in farmaciInRicetta:
                lista_f.append(f[6]-1)
            self.delete_rows(rows=lista_f)
        else: #Vendita libera o ricetta in corso
            #Ricetta in corso: Eliminare solo la riga selezionata
            if risultato[1]!="L":
                if risultato[0]==ricette.get_columnValue(id=risultato[3],column=ricette.farmaco_1):
                    ricette.update_ricetta(risultato[3],Farmaco_1_qta=0)
                else: #il secondo
                    ricette.update_ricetta(risultato[3],Farmaco_2_qta=0)
            self.delete_rows(rows=[row])
    def attiva_sospeso(self,row:int, newQta:int, newSosp:int):
        pass
vendita = Vendita() #una sorta di magazzino provvisorio dove inserire elenco di farmaci che si stanno vendendo

class Sospesi():
    def __init__(self):
        #Nome tabella
        self.nome="Sospesi"
        #Colonne
        self.primaryKey="Numero"
        self.referenceBancadati="ID_Farmaco"
        self.quantità="Quantita"
        self.referenceRicetta="ID_Ricetta"
        #Altre variabili
        self.lastNumber=0 #Gestico l'assegnazione dei numeri della primaryKey a modo mio e non autoincrementale
        #Crea tabella
        query= f"""
                CREATE TABLE IF NOT EXISTS {self.nome} (
                {self.primaryKey} INTEGER,
                {self.referenceBancadati} INTEGER,
                {self.quantità} INTEGER,
                {self.referenceRicetta} INTEGER,
                FOREIGN KEY ({self.referenceBancadati}) REFERENCES {Banca_dati.nome_tabella_Farmaco[0]}({Banca_dati.Farmaco_primarykey}),
                FOREIGN KEY ({self.referenceRicetta}) REFERENCES {ricette.nome}({ricette.primaryKey})
                );"""
        execute_query(query=query,commit=True)
    def add(self):
        pass
sospesi=Sospesi()