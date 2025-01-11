import PyQt5.uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from moneyed import Money, EUR, format_money
from babel import Locale

import Middleware

locale=Locale.parse('it_IT')

def get_columnIndex_tableWidget_byName(tableWidget: PyQt5.QtWidgets.QTableWidget, column_name: str):
    column_count = tableWidget.columnCount()
    # Trova l'indice della colonna dato il nome della colonna
    for column in range(column_count):
        header_item = tableWidget.horizontalHeaderItem(column)
        if header_item and header_item.text() == column_name:
            return column

class FinestraMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("Data\\Menu_iniziale.ui",self)
        self.toolButton_Vendita.clicked.connect(self.Slot_ChiamaFinestraVendita)
        self.pushButton_Bolle.clicked.connect(self.Slot_ChiamaFinestraBolle)
        self.pushButton_RipristinoDatabase.clicked.connect(self.Slot_ChiamaFinestraRipristinoDatabase)
    #Slot
    def Slot_ChiamaFinestraVendita(self):
        finestra_vendita=FinestraVendita()
        risultato=finestra_vendita.exec()

    def Slot_ChiamaFinestraBolle(self):
        finestra_bolle=FinestraBolle()
        risultato=finestra_bolle.exec()
    
    def Slot_ChiamaFinestraRipristinoDatabase(self):
        finestra_RipristinoDatabase=Finestra_RipristinoDatabase()
        risultato=finestra_RipristinoDatabase.exec()

class FinestraBolle(QDialog):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("Data\\Bolle.ui",self)
        self.pushButton_cerca.clicked.connect(self.Slot_ChiamaFinestraCerca)
        self.pushButton_carica.clicked.connect(self.Slot_CaricaBolla)
        
    #Slot

    def Slot_CaricaBolla(self):
        pass

    def Slot_ChiamaFinestraCerca(self):
        finestra_cerca=FinestraRicerca(input_iniziale=self.lineEdit_cerca.text())
        self.lineEdit_cerca.setText("")
        risultato=finestra_cerca.exec()
        if risultato==1:#inserisci farmaco
            id_farmaco = finestra_cerca.get_risultato()
            self.__addItemToQtableWidgetItem(id_farmaco)
        
    def __addItemToQtableWidgetItem(self, id_farmaco):
        pass
        
class Finestra_RipristinoDatabase(QDialog):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("Data\\RipristinoDatabase.ui",self)
        self.pushButton_start.clicked.connect(self.run_loading_Thread)
        self.loading_t=self.loading_thread()
        self.loading_t.progress.connect(self.updateProgressBar)
        self.loading_t.finished.connect(self.finish_loading_Thread)

    class loading_thread(QThread):
        progress=pyqtSignal(int)
        finished=pyqtSignal()

        def run(self):#logica del thread che infine emette il segnale per aggiornare la grafica
            Middleware.middlwareDatabase.databaseRestore(self.progress)
            self.finished.emit()

    #Slot
    
    def run_loading_Thread(self):
        #disattiva il pulsante per evitare avii multipli
        self.pushButton_start.setEnabled(False)
        self.loading_t.start() #questo fa partire il metodo run() della classe loading_thread
        
    def updateProgressBar(self,value:int):
        self.progressBar_Caricamento.setValue(value)

    def finish_loading_Thread(self):
        self.pushButton_start.setEnabled(True)
        self.done(1)

class FinestraVendita(QDialog):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("Data\\finestra_vendita.ui",self)
        self.pushButton_Cerca.clicked.connect(self.Slot_ChiamaFinestraCerca) # type: ignore
        self.pushButton_Vendi.clicked.connect(self.Slot_Vendi)
        self.pushButton_ricettaRossa.clicked.connect(self.Slot_chiudiRicetta)
        self.pushButton_PlusOne.clicked.connect(self.Slot_PlusOne)
        self.tableWidget_Vendita.itemSelectionChanged.connect(self._newSelection)
        self.pushButton_LessOne.clicked.connect(self.Slot_LessOne)
        self.pushButton_Delete.clicked.connect(self.Slot_Delete)
        self.pushButton_attivaSospeso.clicked.connect(self.Slot_AttivaSospeso)
        self.pushButton_ritiraSospeso.clicked.connect(self.Slot_RitiraSospeso)
        self.pushButton_storicoVendite.clicked.connect(self.Slot_StoricoVendite)
        self.pushButton_Ricette.clicked.connect(self.Slot_Ricette)
        #self.lineEdit_InserireCodice.setFocus()

        self.update_row()

    #class annidate
    class FinestraAttivaSospeso(QDialog):
            def __init__(self,Qta:int, Sosp:int, nMaxPezzi:int=None):
                super().__init__()
                PyQt5.uic.loadUi("Data\\attiva_sospeso.ui",self)    
                    # self.label_oraRitiraValue, self.spinBox_sospendi, self.checkBox_pagamento, self.pushButton_annulla, self.pushButton_ok
                self.Qta=Qta
                self.Sosp=Sosp
                self.nMaxPezzi=nMaxPezzi
                self.spinBox_oraRitira.setValue(self.Qta)
                self.spinBox_sospendi.setValue(self.Sosp)
                if nMaxPezzi!=None: #in caso di ricetta mettiamo dei max e blocchiamo lo spinbox ora ritira
                    self.spinBox_oraRitira.setReadOnly(True)
                    self.spinBox_sospendi.setRange(0,self.nMaxPezzi)
                    self.spinBox_sospendi.valueChanged.connect(self.Slot_spinBox_sospendiValueChanged)

                self.pushButton_annulla.clicked.connect(self.Slot_Annulla)
                self.pushButton_ok.clicked.connect(self.Slot_Ok)
                
            #Slot

            def Slot_Annulla(self):
                self.done(-1)

            def Slot_Ok(self):
                self.done(1)
            
            def Slot_spinBox_sospendiValueChanged(self,i):
                self.Sosp=i
                self.Qta=self.nMaxPezzi-self.Sosp
                self.spinBox_oraRitira.setValue(self.Qta)
    #Slot

    def Slot_Ricette(self):
        finestra_ricette= FinestraRicette()
        risultato=finestra_ricette.exec()

    def Slot_PlusOne(self):
        if self.tableWidget_Vendita.selectedItems():
            row=self.tableWidget_Vendita.selectedItems()[0].row()
            Middleware.middlwareDatabase.plus_one_FarmacoVendita(row=row)
            self.update_row(row)

    def Slot_LessOne(self):
        if self.tableWidget_Vendita.selectedItems():
            row=self.tableWidget_Vendita.selectedItems()[0].row()
            Middleware.middlwareDatabase.less_one_FarmacoVendita(row)
            self.update_row(row)

    def Slot_Delete(self):
        if self.tableWidget_Vendita.selectedItems():
            row=self.tableWidget_Vendita.selectedItems()[0].row()
            Middleware.middlwareDatabase.delete_FarmacoVendita(row)
            self.update_row(row-1)

    def Slot_Vendi(self):
        pass
    
    def Slot_chiudiRicetta(self):
        if self.tableWidget_Vendita.selectedItems():
            row=self.tableWidget_Vendita.selectedItems()[0].row()
        else:
            row=0
        Middleware.middlwareDatabase.close_and_numerate_ricetta()
        self.update_row(row_to_focus=row)

    def Slot_ChiamaFinestraCerca(self):
        finestra_ricerca = FinestraRicerca(input_iniziale=self.lineEdit_InserireCodice.text())
        self.lineEdit_InserireCodice.setText("")
        risultato=finestra_ricerca.exec()
        
        if risultato==1:#inserisci farmaco
            self._addItemToQtableWidgetItem(finestra_ricerca.get_risultato())            

    def Slot_AttivaSospeso(self):
        #info della riga selezionata
        if self.tableWidget_Vendita.selectedItems() or len(Middleware.middlwareDatabase.farmaci_ricetta_in_corso())>0: #cos'è una ricetta in corso con l'aggiunta dei sospesi? ripartire da qui
            row=self.tableWidget_Vendita.selectedItems()[0].row()
            f=Middleware.middlwareDatabase.get_all_FarmacoVendita_data()
            f=f[row]
        else:
            return -1 #non ci sono item selezionati

        #Caso 1: Farmaco in vendita libera
        nMaxPezzi=None
        #Caso 2: Farmaco in ricetta rossa già chiusa o in sospeso (quindi precedentemente chiusa e poi sospesa parzialmente)
        if f.V!="L" and (f.N_Ricetta!=None or f.Sosp!=0):
            nMaxPezzi=f.Qta+f.Sosp
        #Chiama la finestra
        finestra=FinestraVendita.FinestraAttivaSospeso(Qta=f.Qta,Sosp=f.Sosp,nMaxPezzi=nMaxPezzi)
        risposta=finestra.exec()
        #Risultati scelti
        newQta=finestra.spinBox_oraRitira.value()
        newSosp=finestra.spinBox_sospendi.value()
        #Chiama la logica per elaborare i cambiamenti
        Middleware.middlwareDatabase.attiva_sospeso(row=row,newQta=newQta,newSosp=newSosp)
        #Aggiorna la grafica
        self.update_row(row_to_focus=row)

    def Slot_RitiraSospeso(self):
        pass

    def Slot_StoricoVendite(self):
        pass    

    def _addItemToQtableWidgetItem(self,id_farmaco: int):
        tipo_ricetta=self._get_tipo_ricetta()
        row_to_focus=Middleware.middlwareDatabase.insert_farmaco(id_farmaco=id_farmaco,tipo_vendita=tipo_ricetta)
        #Update Grafica
        self.update_row(row_to_focus=row_to_focus)

    def _newSelection(self):
        items=self.tableWidget_Vendita.selectedItems()
        if len(items)>0:
            row=items[0].row()
            if items[0].text()!="L": #imposta stile di selezione da ricetta: scritte rosse
                self.tableWidget_Vendita.setStyleSheet("""
                                                        QTableWidget::item:selected {
                                                            background-color: yellow;
                                                            color: red}
                                                        nQTableWidget::item:selected:not active {
                                                            background-color: yellow;
                                                            color: red}
                                                        QHeaderView::section {background-color: lightblue;
                                                            color: black;
                                                            font-weight: bold;
                                                            border: 1px solid gray;
                                                            padding: 4px;}
                                                    """)
            else: #imposta stile di selezione da libera: scritte nere
                self.tableWidget_Vendita.setStyleSheet("""
                                                        QTableWidget::item:selected {
                                                            background-color: yellow;
                                                            color: black}
                                                        nQTableWidget::item:selected:not active {
                                                            background-color: yellow;
                                                            color: black}
                                                        QHeaderView::section {background-color: lightblue;
                                                            color: black;
                                                            font-weight: bold;
                                                            border: 1px solid gray;
                                                            padding: 4px;}
                                                    """)

    def update_row(self, row_to_focus:int=0):
        farmaciRicettaInCorso=Middleware.middlwareDatabase.farmaci_ricetta_in_corso()
        if len(farmaciRicettaInCorso)>0:
            self.pushButton_ricettaRossa.setEnabled(True)
            self.comboBox_TipoVendita.setEnabled(False)
            self.set_tipo_ricetta_by_simbol(farmaciRicettaInCorso[0].V)
        else:
            self.pushButton_ricettaRossa.setEnabled(False)
            self.comboBox_TipoVendita.setEnabled(True)

        totale=Money(0,EUR)
        rows=Middleware.middlwareDatabase.get_all_FarmacoVendita_data()
        self.tableWidget_Vendita.setRowCount(0)
        for i,row in enumerate(rows):
            self.tableWidget_Vendita.insertRow(i)
            #settiamo i colori
                #colore testo
            color=(0,0,0,255) #nero di base
            if row.V!="L":
                color=(255,0,0,150) #rosso se ricetta

            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"V"),self._newTableWidgetItem(value=str(row.V),color=color))
            if row.Pr!=None:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Pr"),self._newTableWidgetItem(value=str(row.Pr),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Pr"),self._newTableWidgetItem(value="",color=color))
            if row.ID_Ricetta!=None:
                n_ricetta=Middleware.middlwareDatabase.get_ricettaNumber(ID_ricetta=row.ID_Ricetta)
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"N.Ricetta"),self._newTableWidgetItem(value=str(n_ricetta),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"N.Ricetta"),self._newTableWidgetItem(value="",color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Prodotto"),self._newTableWidgetItem(value=str(row.Prodotto),color=color))
            if row.Prezzo!=Money(0, EUR):
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Prezzo"),self._newTableWidgetItem(value=format_money(row.Prezzo,locale=locale),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Prezzo"),self._newTableWidgetItem(value="",color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Qta"),self._newTableWidgetItem(value=str(row.Qta),color=color))
            if row.Sosp!=0:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Sosp"),self._newTableWidgetItem(value=row.Sosp,color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Sosp"),self._newTableWidgetItem(value="",color=color))
            if row.Importo!=Money(0, EUR):    
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Importo"),self._newTableWidgetItem(value=format_money(row.Importo,locale=locale),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Importo"),self._newTableWidgetItem(value="",color=color))
            if row.Pr_Rimborso!=Money(0, EUR):    
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Pr.Rimborso"),self._newTableWidgetItem(value=format_money(row.Pr_Rimborso,locale=locale),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Pr.Rimborso"),self._newTableWidgetItem(value="",color=color))
            if row.Diff!=Money(0, EUR):
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Diff"),self._newTableWidgetItem(value=format_money(row.Diff,locale=locale),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Diff"),self._newTableWidgetItem(value="",color=color))
            if row.Quota!=Money(0, EUR):    
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Quota"),self._newTableWidgetItem(value=format_money(row.Quota,locale=locale),color=color))
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Quota"),self._newTableWidgetItem(value="",color=color))
            if row.Tot_Assistito!=Money(0, EUR):    
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Tot.Assistito"),self._newTableWidgetItem(value=format_money(row.Tot_Assistito,locale=locale),color=color))
                totale+=row.Tot_Assistito
            else:
                self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Tot.Assistito"),self._newTableWidgetItem(value="",color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Nota"),self._newTableWidgetItem(value=str(row.Nota),color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Tk"),self._newTableWidgetItem(value=str(row.Tk),color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Cl"),self._newTableWidgetItem(value=str(row.Cl),color=color))
            self.tableWidget_Vendita.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Vendita,"Giac"),self._newTableWidgetItem(value=str(row.Giac),color=color))

        self.textBrowser_valore_TotaliVenditaAttuale.setText(format_money(totale,locale=locale))
        self.tableWidget_Vendita.resizeColumnsToContents()
        try:
            self.tableWidget_Vendita.selectRow(row_to_focus)
        except:
            pass

    def _get_tipo_ricetta(self)->str:
        tipo_vendita=self.comboBox_TipoVendita.currentText()
        if tipo_vendita=="Soggetta":
            return "S"
        elif tipo_vendita=="Parziale 2pz":
            return "K"
        elif tipo_vendita=="Parziale 6pz":
            return "Y"
        elif tipo_vendita=="Totale 2pz":
            return "O"
        elif tipo_vendita=="Totale 6pz":
            return "A"
        else:
            return "L"

    def set_tipo_ricetta_by_simbol(self,simbol:str):
        """
        In base al simbolo che rappresenta il tipo di vendita, imposta il tipo di vendita -> "L" -> "Libera", "S" -> "Soggetta" etc...
        """
        index=-1
        if simbol=="L":
            index=self.comboBox_TipoVendita.findText("Libera")
        elif simbol=="S":
            index=self.comboBox_TipoVendita.findText("Soggetta")
        elif simbol=="K":
            index=self.comboBox_TipoVendita.findText("Parziale 2pz")
        elif simbol=="Y":
            index=self.comboBox_TipoVendita.findText("Parziale 6pz")
        elif simbol=="O":
            index=self.comboBox_TipoVendita.findText("Totale 2pz")
        elif simbol=="A":
            index=self.comboBox_TipoVendita.findText("Totale 6pz")
        if index!=-1:
                self.comboBox_TipoVendita.setCurrentIndex(index)

    def _newTableWidgetItem(self,value:str,color:tuple=(255,255,255,255))->QTableWidgetItem:
        item=QTableWidgetItem(value)
        item.setForeground(QColor(color[0],color[1],color[2],color[3]))
        return item

class FinestraRicerca(QDialog):
    
    def __init__(self, input_iniziale:str=""):
        super().__init__()
        PyQt5.uic.loadUi("Data\\finestra_cerca.ui",self)
        self.input_ricerca.setFocus()
        self.input_ricerca.setText(input_iniziale)

        self.pulsante_cerca.clicked.connect(self.__pulsante_cerca_clicked)
        self.input_ricerca.returnPressed.connect(self.__pulsante_cerca_clicked)
        self.tableWidget_risultati.itemActivated.connect(self.__pulsante_inserisci_clicked)
        self.pushButton_inserisci.clicked.connect(self.__pulsante_inserisci_clicked)
        #Checkbox
        self.boxList=[self.checkBox_Denominazione_e_Confezione,self.checkBox_Principio_Attivo,self.checkBox_Prezzo,
                 self.checkBox_Titolare_AIC,self.checkBox_Codice_AIC,self.checkBox_Cod_Gruppo_Equivalenza]
        for box in self.boxList:
            box.stateChanged.connect(self.__checkStateFilterChanged)
        self.__checkStateFilterChanged()
        #---------

    def get_risultato(self):
        column=get_columnIndex_tableWidget_byName(tableWidget=self.tableWidget_risultati, column_name="Codice AIC")
        codice_aic = self.tableWidget_risultati.item(self.tableWidget_risultati.currentRow(),column).text()
        id_farmaco = Middleware.middlwareDatabase.cerca_farmaco(input=codice_aic,
                                                                tipo_di_ricerca=Middleware.middlwareDatabase.tipoRicercaBancadati.Codice_AIC,
                                                                colonne_da_visualizzare=[Middleware.middlwareDatabase.tipoRicercaBancadati.ID_Farmaco])
        return id_farmaco[0][0]
    
    #Slot
    def __pulsante_cerca_clicked(self):
        self.tableWidget_risultati.setRowCount(0)
        righe = Middleware.middlwareDatabase.cerca_farmaco(input=self.input_ricerca.text(),
                                                           tipo_di_ricerca=self.__converti_ComboBoxText_in_Enum(),
                                                           colonne_da_visualizzare=self.__restituisci_risultati_checkBox_attivi())
                                                                        
        self.tableWidget_risultati.setRowCount(len(righe))
        for i,riga in enumerate(righe):
            for j,colonna in enumerate(riga):
                self.tableWidget_risultati.setItem(i,j,QTableWidgetItem(str(colonna)))
        self.tableWidget_risultati.resizeColumnsToContents()

    def __checkStateFilterChanged(self):
        self.tableWidget_risultati.setColumnCount(0)
        for box in self.boxList:
            if box.checkState():
                n_colonne=self.tableWidget_risultati.columnCount()
                self.tableWidget_risultati.setColumnCount(n_colonne + 1)
                column_name=box.text()
                self.tableWidget_risultati.setHorizontalHeaderItem(n_colonne, QTableWidgetItem(column_name))
        self.__pulsante_cerca_clicked()

    def __pulsante_inserisci_clicked(self):
        """chiude con codice 1 quindi volendo inserire un risultato"""
        self.done(1)

    #metodi interni
    def __converti_ComboBoxText_in_Enum(self):
        if self.comboBox.currentText()=="Denominazione e Confezione":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Denominazione_e_Confezione
        elif self.comboBox.currentText()=="Principio Attivo":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Principio_Attivo
        elif self.comboBox.currentText()=="Titolare AIC":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Titolare_AIC
        elif self.comboBox.currentText()=="Codice AIC":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Codice_AIC
        elif self.comboBox.currentText()=="Cod. Gruppo Equivalenza":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Cod_Gruppo_Equivalenza
        elif self.comboBox.currentText()=="Descrizione Gruppo":
            return Middleware.Middlware_Database.tipoRicercaBancadati.Descrizione_Gruppo

    def __restituisci_risultati_checkBox_attivi(self) -> list[str]:
        risultato=[]
        if self.checkBox_Denominazione_e_Confezione.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Denominazione_e_Confezione)
        if self.checkBox_Principio_Attivo.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Principio_Attivo)
        if self.checkBox_Prezzo.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Prezzo_attuale)
        if self.checkBox_Titolare_AIC.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Titolare_AIC)
        if self.checkBox_Codice_AIC.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Codice_AIC)
        if self.checkBox_Cod_Gruppo_Equivalenza.isChecked():
            risultato.append(Middleware.Middlware_Database.tipoRicercaBancadati.Cod_Gruppo_Equivalenza)
        return risultato
    
    #metodi base redefiniti
    def keyPressEvent(self, event):
        QDialog.keyPressEvent(self, event)
        if event.key()==Qt.Key.Key_Down and self.input_ricerca.hasFocus():
            self.tableWidget_risultati.setFocus()
        elif event.key()==Qt.Key.Key_Up and self.tableWidget_risultati.hasFocus():
            self.input_ricerca.setFocus()

class FinestraInfoDialog(QDialog):
    def __init__(self,okButtonClickedFunction,textBox:str):
        super().__init__()
        PyQt5.uic.loadUi("Data\\Info_Dialog.ui",self)
        self.okButtonClickedFunction=okButtonClickedFunction
        self.texBox=textBox
        self.pushButton_OK.clicked.connect(self.okButtonClickedFunction)
        self.label_TESTO.setText(textBox)

class FinestraRicette(QDialog):
    def __init__(self):
        super().__init__()
        PyQt5.uic.loadUi("Data\\Ricette.ui",self)
        self.updateRow()

    def _newTableWidgetItem(self,value:str,color:tuple=(255,255,255,255))->QTableWidgetItem:
        item=QTableWidgetItem(value)
        item.setForeground(QColor(color[0],color[1],color[2],color[3]))
        return item

    def updateRow(self):
        lista_ricette=Middleware.middlwareDatabase.get_all_Ricetta_data()
        self.tableWidget_Ricette.setRowCount(0)
        for i, ricetta in enumerate(lista_ricette):
            self.tableWidget_Ricette.insertRow(i)
            color=(0,0,0,255)
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Stato"),self._newTableWidgetItem(value=ricetta.stato,color=color))
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Numero"),self._newTableWidgetItem(value=str(ricetta.numero),color=color))
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Esenzione"),self._newTableWidgetItem(value=ricetta.V,color=color))
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 1 AIC"),self._newTableWidgetItem(value=ricetta.farmaco_1_AIC,color=color))
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 1 Descrizione"),self._newTableWidgetItem(value=ricetta.farmaco_1_Descrizione,color=color))
            if ricetta.farmaco_1_qta>0:
                self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 1 Qta"),self._newTableWidgetItem(value=str(ricetta.farmaco_1_qta),color=color))                
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 2 AIC"),self._newTableWidgetItem(value=ricetta.farmaco_2_AIC,color=color))
            self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 2 Descrizione"),self._newTableWidgetItem(value=ricetta.farmaco_2_Descrizione,color=color))
            if ricetta.farmaco_2_qta>0:
                self.tableWidget_Ricette.setItem(i,get_columnIndex_tableWidget_byName(self.tableWidget_Ricette,"Farmaco 2 Qta"),self._newTableWidgetItem(value=str(ricetta.farmaco_2_qta),color=color))
        self.tableWidget_Ricette.resizeColumnsToContents()