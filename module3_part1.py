from pymodule_imports import *

class PCASetUp(object):
    """An object to initialize procedures to set up the larger Project Cleaning App.

    Attributes:
        none
    """
    today = time.strftime("%Y-%m-%d")
    drives = ['H:\\','K:\\','L:\\']

    cn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};Server=servernm; DATABASE=dbname; Trusted_Connection=yes')
    params1 = urllib.parse.quote("DRIVER={SQL Server Native Client 11.0};SERVER=servernm;DATABASE=dbname;Trusted_Connection=yes")
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params1)

    
    def __init__(self):
        """Initialize the PCASetUp object"""
        #self.name = name

    def pull_folders(self):
        """Retrieve a list of all folders in each drive.
            Insert into SQL database if it doesn't already exist."""
        projects = []
        counter = 0
        #params1 = urllib.parse.quote("DRIVER={SQL Server Native Client 11.0};SERVER=servernm;DATABASE=dbname;Trusted_Connection=yes")
        #engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params1)

        for d in drives:
            dirlist = next(os.walk(d))[1]
            dir_list = [d+f for f in dirlist]
            projects.extend(dir_list)

        networks = pd.read_sql_query("SELECT distinct folderpath FROM PCA.network_folders;", engine)
        folders = networks["folderpath"].tolist()

        sql.execute('BEGIN TRAN', engine)

        for prj in projects:
            if prj not in folders:
                try:
                    sql.execute(sa.text('INSERT INTO PCA.network_folders (folderpath, dtadded) VALUES(:val1, cast(:val2 as date))'), engine, params={'val1': prj, 'val2': today})
                    counter += 1
                except:
                    print('error inserting %s' % prj)
                    continue
        try:
            sql.execute('COMMIT TRAN', engine)
            print(str(counter),'new project folder records were inserted')
        except:
            sql.execute('ROLLBACK TRAN', engine)
            print('No new project folder records were inserted')
        else:
            pass

        #engine.dispose()

    def pull_databases(self):
        """Run a stored procedure to list all databases in the server.
            Insert into SQL database if it doesn't already exist."""
        #cn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};Server=servernm; DATABASE=dbname; Trusted_Connection=yes')
        cursor1 = cn.cursor()

        proc = 'exec [dbo].[pull_databases]'
        cursor1.execute(proc).commit()

        slct = "SELECT COUNT(*) FROM [PCA].[SQL_databases] where dtadded=cast(getdate() as date)"
        cursor1.execute(slct)
        rowcount = cursor1.fetchone()[0]
        print (rowcount, "new database records inserted")

        cn.close()

    def unassigned_dbs(self):
        """List databases which are not already assigned to the master project database"""
        sqry = "SELECT [S_ID],[dbname] FROM [PCA].[SQL_databases] \
        where exclude=0 and S_ID not in (select distinct ID_sqldb as sdbid from [PCA].[projects_master] where ID_sqldb is not null \
        union select distinct ID_restrictedsqldb as sdbid from [PCA].[projects_master] where ID_restrictedsqldb is not null);"
        sqldbs = pd.read_sql_query(sqry, engine)

    def unassigned_folders(self):
        """List folders which are not already assigned to the master project database"""
        sqry = "SELECT [N_ID],[folderpath] FROM [PCA].[network_folders] \
        where exclude=0 and N_ID not in (select distinct ID_network from [PCA].[projects_master] where ID_network is not null);"
        nfolders = pd.read_sql_query(sqry, engine)

    def unassigned_projects(self):
        """List folders which are not already assigned to the master project database"""
        sqry = "SELECT [N_ID],[folderpath] FROM [PCA].[network_folders] \
        where exclude=0 and N_ID not in (select distinct ID_network from [PCA].[projects_master] where ID_network is not null);"
        nfolders = pd.read_sql_query(sqry, engine)

def main():
    mod3 = PCASetUp()

if __name__ == '__main__':
    main()
