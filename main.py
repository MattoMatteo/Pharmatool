import sys
import PyQt5.QtWidgets
import Database
import ui

def main():

    app = PyQt5.QtWidgets.QApplication(sys.argv)
    
    if not Database.Banca_dati.check_integrity():
        finestra_ripristino = ui.Finestra_RipristinoDatabase()
        risultato = finestra_ripristino.exec()
        if risultato!=1:
            sys.exit(1)

    finestra_menu = ui.FinestraMenu()
    finestra_menu.show()
    sys.exit(app.exec_())   
    
if __name__== "__main__":
    main()


