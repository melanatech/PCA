# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 18:12:59 2017

@author: nicol_000
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import PCA_mod2ui
from pymodule_imports import *

class PCAmod2App(QtWidgets.QMainWindow, PCA_mod2ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PCAmod2App, self).__init__(parent)
        self.setupUi(self) #sets up UI design file layout
        #populate project list
        def createPlaceholder(text1):
            spacer = 95
            placehold = ' '
            placeholder = (placehold*(spacer-len(text1)))
            return placeholder

        def createListItem(label1, label2):
            line2txt = 'User role: '+label2
            line1 = label1+createPlaceholder(label1)
            line2 = line2txt+createPlaceholder(line2txt)
            listitem = line1+line2
            return listitem
        
        for row in readprojs.itertuples():
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(item.sizeHint().width(), 35))
            item.setFont(QtGui.QFont('Arial', 12))
            #item.setFont(QtGui.QFont('Tahoma', 14,QtGui.QFont.Bold))
            project = getattr(row,'Index')
            item.setText(project)
            #role = getattr(row,'role')
            #datalist = createListItem(project, role)
            #self.projectListWidget.addItem(datalist)
            self.projectListWidget.addItem(item)
        
        
        #set up signals for application actions
        self.userLabel.setText(user1)
        self.exitButton.clicked.connect(self.exit_app)
        self.SubmitButton.clicked.connect(self.submit_inputs)
        self.clearButton.clicked.connect(self.clear_inputs)
        self.projectListWidget.itemSelectionChanged.connect(self.project_info)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint) # disable (but not hide) close button
        
        #set up button groups
        self.actionbg = QtWidgets.QButtonGroup()
        self.updatebg = QtWidgets.QButtonGroup()        
        self.actionbg.addButton(self.saveOption,1)
        self.actionbg.addButton(self.NAoption,2)
        self.actionbg.addButton(self.deleteOption,3)
        self.actionbg.addButton(self.archiveOption,4)
        self.updatebg.addButton(self.restrictedOption,5)
        self.updatebg.addButton(self.reviewedOption,6)
        self.updatebg.addButton(self.cleanedOption,7)
        self.updatebg.setExclusive(False)

    def exit_app(self):
        engine.dispose()
        QtCore.QCoreApplication.instance().quit()

    def clear_inputs(self): #clears all selections
        self.actionbg.setExclusive(False)
        for button in self.actionbg.buttons():
            button.setChecked(False)
        self.actionbg.setExclusive(True)
        for button in self.updatebg.buttons():
            button.setChecked(False)
        self.notesText.clear()

    def project_info(self): #displays project details for selected project
        l_items = self.projectListWidget.selectedItems()
        l_label=str(l_items[0].text())
        pname = l_label.split()[0]
        p_label = 'Project Name: '+pname
        py = readprojs.ix[pname, 'prior_action']
        cy = readprojs.ix[pname, 'current_action']
        notes = readprojs.ix[pname, 'notes']
        status = readprojs.ix[pname, 'project_status']
        role = readprojs.ix[pname, 'role']
        rf = readprojs.ix[pname, 'restrictedfolder']
        if rf == 1: isRestricted = '    *has restricted folder'
        else: isRestricted = ''
        self.projDetailsLabel1.setText(p_label+isRestricted)
        self.projDetailsLabel2.setText("Role: "+role)
        self.projDetailsLabel3.setText("Status: "+status)
        self.projDetailsLabel4.setText("Prior Year Action: "+py+'   /   '+"Current Year Action: "+cy)
        self.notesText.setPlainText(notes)

    def submit_inputs(self): #sends data to SQL database
        def catch_error(usr, prj, rev, restr, cln, cyact, nts, em):
            #first create function to log errors
            today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            submitdata = [{'pca_user':usr, 'project':prj, 'error_timestamp':today, 'reviewed':rev,
                           'restricted':restr,'cleaned':cln,'current_action':cyact,'notes':nts, 'errormessage':em}]
            errordata = pd.DataFrame(submitdata)
            errordata.to_sql('error_log', engine, if_exists='append', schema='PCA', index=False)

        l_items = self.projectListWidget.selectedItems()
        l_label=str(l_items[0].text())
        pname = l_label.split()[0]
        
        buttongroups = {1:'Saved',2:'NA',3:'Delete',4:'Archive',5:'Restricted',6:'Reviewed',7:'Cleaned'}
        actionSelected=0
        reviewed=0
        cleaned=0
        restricted=0
        updateSelected=[]
        action=''
        notes = self.notesText.toPlainText()

        #determine if any of the buttons have been checked
        for button in self.actionbg.buttons():
            if button.isChecked():
                actionSelected = self.actionbg.checkedId()
        for button in self.updatebg.buttons():
            if button.isChecked():
                update = self.updatebg.checkedId()
                updateSelected.append(buttongroups[update])

        if actionSelected>0 :action = buttongroups[actionSelected]
        if 'Reviewed' in updateSelected: reviewed=1
        if 'Cleaned' in updateSelected: cleaned=1
        if 'Restricted' in updateSelected: restricted=1

        squery2 = "EXEC [dbo].[update_cleaninglog] @project = \'{0}\',@user = \'{1}\',@notes = \'{2}\',@action = \'{3}\',@reviewed = {4},@cleaned = {5},@restricted = {6};".format(pname,user1,notes,action,reviewed,cleaned,restricted)
        
        try: #try to send the form data to be update the SQL table, and log if there are any errors
            datasubmit = pd.read_sql_query(squery2, engine)
            if datasubmit.iloc[0]['result'] == 'success':
                self.messageLog.appendPlainText(pname+' project updated')
                self.clear_inputs()
            elif datasubmit.iloc[0]['result'] == 'failure':
                errorm='sp executed, but result returned failure'
                catch_error(user1,pname,reviewed,restricted,cleaned,action,notes,errorm)
                self.messageLog.appendPlainText('Error updating project '+pname+'; see log')
                self.clear_inputs()
                
        except:
            errorm='sp not executed'
            catch_error(user1,pname,reviewed,restricted,cleaned,action,notes,errorm)
            self.messageLog.appendPlainText('Error updating project '+pname+'; see log')
            self.clear_inputs()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = PCAmod2App()
    form.show() #show the form
    app.exec_() #execute the app

#retrieve user id
def inituser():
    global user1
    user1 = os.getlogin().lower()

#create an initial SQL Server connection
def initsql():
    global engine
    global readprojs
    eparams = urllib.parse.quote("DRIVER={SQL Server Native Client 11.0};SERVER=servernm;DATABASE=dbname;Trusted_Connection=yes")
    squery1 = 'EXEC [dbo].[pull_current_projects] @user = {0};'.format(user1)
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % eparams)
    readprojs = pd.read_sql_query(squery1, engine, index_col='project_name')

if __name__ == '__main__':
    inituser()
    initsql()
    main()
