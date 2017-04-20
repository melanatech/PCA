from PyQt5 import QtGui, QtCore, QtWidgets
from pymodule_imports import *
import numpy as np

class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.table = QtWidgets.QTableWidget(self)
        #retrieve the initial table
        squery1 = 'select project_name,cast(ID_network as varchar(10)) ID_network,cast(ID_sqldb as varchar(10)) ID_sqldb,\
                cast(ID_restrictedsqldb as varchar(10)) ID_restrictedsqldb,reviewer1,reviewer2 from PCA.projects_master;'
        rdprj = pd.read_sql_query(squery1, engine)
        rdprj = rdprj.replace([None], [''], regex=True)
        #set up table structure
        columns=6
        self.table.setColumnCount(columns)
        colnames = {0:'project_name',1:'ID_network',2:'ID_sqldb',3:'ID_restrictedsqldb',4:'reviewer1',5:'reviewer2'}
        rows = len(rdprj.index)
        self.table.setRowCount(rows)
        self.table.setHorizontalHeaderLabels(['project_name','ID_network','ID_sqldb','ID_restrictedsqldb','reviewer1','reviewer2'])
        
        for column in range(columns):
            rdcol = colnames[column]
            for row in range(rows):
                rdrow = str(rdprj.ix[row,rdcol])
                item = QtWidgets.QTableWidgetItem(rdrow)
                self.table.setItem(row, column, item)

        self.buttonSave = QtWidgets.QPushButton('Save', self)
        self.buttonAdd = QtWidgets.QPushButton('Add Row', self)
        self.buttonSave.clicked.connect(self.handleSave)
        self.buttonAdd.clicked.connect(self.handleAdd)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addWidget(self.buttonSave)
        layout.addWidget(self.buttonAdd)

    def handleSave(self):
        confirmmsg = QtWidgets.QMessageBox()
        """
        tabledata=[]
        for row in range(self.table.rowCount()):
            rowdata = {}
            for column in range(self.table.columnCount()):
                newcol=colnames[column]
                item = self.table.item(row, column)
                if item is not None:
                    rowdata[newcol]=item.text()
                else:
                    rowdata[newcol]=''
            tabledata.append(rowdata)
        tabledf=pd.DataFrame(tabledata)"""
        confirmmsg.setIcon(QtWidgets.QMessageBox.Warning)
        confirmmsg.setText("Are you sure you want to save changes to this table?")
        confirmmsg.setWindowTitle("Confirm changes")
        confirmmsg.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel)
        confirmmsg.setDefaultButton(QtWidgets.QMessageBox.Save)
        msgval = confirmmsg.exec_()
        if msgval == QtWidgets.QMessageBox.Save:
            tabledf=self.rdprj
            self.submitData(tabledf)
            #self.exitApp()

    def exitApp(self):
        engine.dispose()
        QtCore.QCoreApplication.instance().quit()

    def submitData(self, newdf):
        #newdf.to_sql('temp', engine, if_exists='replace', schema='PCA', index=False)
        #sql.execute('EXEC [dbo].[update_masterprojects];', engine)
        finalmsg = QtWidgets.QMessageBox()
        finalmsg.setIcon(QtWidgets.QMessageBox.Information)
        finalmsg.setText("Table was successfully updated.")
        finalmsg.setWindowTitle("Update Confirmation")
        finalmsg.setStandardButtons(QtWidgets.QMessageBox.Close)
        cmsgval = finalmsg.exec_()
        if cmsgval == QtWidgets.QMessageBox.Close:
            self.exitApp()
        
        
        
    def handleAdd(self):
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(640, 480)
    window.show()
    app.exec_()

def initsql():
    global engine
    eparams = urllib.parse.quote("DRIVER={SQL Server Native Client 11.0};SERVER=servernm;DATABASE=dbname;Trusted_Connection=yes")
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % eparams)

if __name__ == '__main__':
    initsql()
    main()
