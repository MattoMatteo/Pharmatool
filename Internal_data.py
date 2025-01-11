from moneyed import Money, EUR
import pandas

PATH_csv="Data//inventario.csv"

def csv_read()->pandas.DataFrame:
        dtypes={
            'Codice AIC':'str',
            'Sost.isce':'str',
            'Sost.ito':'str',
        }
        csv= pandas.read_csv(PATH_csv, dtype=dtypes, na_filter=False, delimiter=";")
        csv_finale=csv.map(lambda x: x.strip() if isinstance(x, str) else x)

        csv_finale.columns=csv_finale.columns.str.strip()
        csv_finale["Codice AIC"]=csv_finale["Codice AIC"].apply(lambda x: "0"*(9-len(str(x)))+str(x))
        csv_finale["Sost.ito"]=csv_finale["Sost.ito"].apply(lambda x: "0"*(9-len(str(x)))+str(x) if x!="" and x!=None else x)
        csv_finale["Sost.isce"]=csv_finale["Sost.isce"].apply(lambda x: "0"*(9-len(str(x)))+str(x) if x!="" and x!=None else x)
        
        prezzi=['Prz. Att.','Imp.Assist','PrzRimE.']
        for p in prezzi:
            csv_finale[p]=csv[p].apply(lambda x: str(str(x).replace(',','.').strip(" ")))
            csv_finale[p]=csv_finale[p].apply(lambda x: 0.00 if isinstance(x, str) and x=="" else x)
        csv_finale.to_csv(PATH_csv, sep=";",index=False)
        return csv_finale

def calcolo_ticket_e_npezzi(tipo_vendita:str)->tuple[Money,int]:
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

class Farmaco_vendita():
    """
    Elenco di variabili che saranno inseriti nel database della vendita al banco
    """
    def __init__(self,Progressivo_riga:int=None,Codice_AIC: str=None,V:str=None,
                 Pr:int=None,ID_Ricetta:int=None,Prodotto:str=None,Prezzo:Money=None,
                 Qta:int=None,Sosp:int=None,Importo:Money=None,Pr_Rimborso:Money=None,Diff:Money=None,
                 Quota:Money=None,Tot_Assistito:Money=None,Nota:str=None,Tk:str=None,Cl:str=None,Giac:int=None):
        
        self.Progressivo_riga=Progressivo_riga
        self.Codice_AIC=Codice_AIC 
        self.V=V #Tipo Vendita (Libera, soggetta etc..)
        self.Pr=Pr #Progressivo Ricetta
        self.ID_Ricetta=ID_Ricetta
        self.Prodotto=Prodotto
        self.Prezzo=Prezzo
        self.Qta=Qta
        self.Sosp=Sosp
        self.Importo=Importo
        self.Pr_Rimborso=Pr_Rimborso
        self.Diff=Diff
        self.Quota=Quota
        self.Tot_Assistito=Tot_Assistito
        self.Nota=Nota
        self.Tk=Tk
        self.Cl=Cl
        self.Giac=Giac
    
class Ricetta_internalData():
    def __init__(self,id_ricetta:int=None,stato:str=None,numero:int=None,V:str=None,farmaco_1_AIC:str=None,farmaco_1_Descrizione:str=None,
                 farmaco_1_qta=None,farmaco_2_AIC:str=None,farmaco_2_Descrizione:str=None,farmaco_2_qta=None):
        self.id_ricetta=id_ricetta
        self.stato=stato
        self.numero=numero
        self.V=V
        self.farmaco_1_AIC=farmaco_1_AIC
        self.farmaco_1_Descrizione=farmaco_1_Descrizione
        self.farmaco_1_qta=farmaco_1_qta
        self.farmaco_2_AIC=farmaco_2_AIC
        self.farmaco_2_Descrizione=farmaco_2_Descrizione
        self.farmaco_2_qta=farmaco_2_qta

