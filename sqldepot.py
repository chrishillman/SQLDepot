#!/usr/bin/env python
# coding: utf-8

import adodbapi as ado
from flask import Flask, render_template, redirect, request, url_for
import os
import sys


#Global variables:

app = Flask(__name__)                       #FLASK needs an app name
sqldict = {}                                #This dictionary will hold all the FileNames (key) and their queries (values)
dbhostlist = ["MS-SQL-1", "MS-SQL-2"]      #list of database servers to be queried every time
dbname = "DATABASE"                  		#Name of database on MSSQL server
dbuser = "dbuser"                          #MSSQL Username to use
dbpw = "dolphin1!"           #MSSQL User Password
connstr = """Provider=SQLOLEDB;Server=%s;Trusted_Connection=No;Database=%s;uid=%s;pwd=%s;""" #MSSQL Connection String

#Functions:
#Runs the query against the database Server
def getsqldict(server, sql):
    dbhost = server
    dbconstr = connstr % (dbhost, dbname, dbuser, dbpw)
    myconn = ado.connect(dbconstr)
    dbcur = myconn.cursor()
    dbsql = sql
    dbcur.execute(dbsql)
    if dbcur.rowcount > 0:
        rows = dbcur.fetchall()
    else:
        rows = None
    return rows

#Loads the sqldict with all the sql files in the sql folder
def getsqlfiles():
    for file in os.listdir("sql"):
        if file.endswith(".sql"):
            sqlfile = open("sql" + os.sep + file, mode="r")
            sqldict[file] = sqlfile.read()


#FLASK routes:
@app.route("/")
@app.route("/index.html")
def index():
    getsqlfiles()
    return render_template("index.html", sqldict=sqldict)

@app.route('/getrows.html')
def returnQuery():
    headers = []
    rowslist = []
    sql = None
    sqlfile = request.values.get("f")
    if sqlfile:
        try:
            sql = sqldict[sqlfile]
        except:
            sql = None
            print("ERROR IN QUERY: SQLFILE IS NONE {}".format(sys.exc_info()[0]))
        if sql is not None:
            for server in dbhostlist:
                rows = getsqldict(server, sql)
                if rows is not None:
                    try:
                        if len(headers) == 0:
                            headers.append("server")
                            for key in rows.columnNames.keys():
                                headers.append(key)
                        for item in rows:
                            rowitem = []
                            rowitem.append(server)
                            for iitem in item:
                                rowitem.append(iitem)
                            rowslist.append(rowitem)
                    except:
                        print("ERROR IN QUERY: ROWS NONE: {}".format(sys.exc_info()[0]))
    else:
        return redirect(url_for('index'))
    return render_template("getrows.html", headers=headers, rows=rowslist, sql=sql, sqlfile=sqlfile)

@app.route('/getrows.csv')
def returnCSV():
    headers = []
    rowslist = []
    sql = None
    sqlfile = request.values.get("f")
    if sqlfile:
        try:
            sql = sqldict[sqlfile]
        except:
            sql = None
            print("ERROR IN QUERY: SQLFILE IS NONE")
        if sql is not None:
            for server in dbhostlist:
                rows = getsqldict(server, sql)
                if rows is not None:
                    try:
                        if len(headers) == 0:
                            headers.append("server")
                            for key in rows.columnNames.keys():
                                headers.append(key)
                        for item in rows:
                            rowitem = []
                            rowitem.append(server)
                            for iitem in item:
                                rowitem.append(iitem)
                            rowslist.append(rowitem)
                    except:
                        print("ERROR IN QUERY: ROWS NONE")
    else:
        return redirect(url_for('index'))
    return render_template("getrows.csv", headers=headers, rows=rowslist)

@app.route('/updatequery.html', methods=["POST"])
def updatequery():
    confirm = False
    sqlquery = ""
    sqlfile = ""
    if request.method == "POST":
        if request.form.get("query"):
            sqlquery = request.form.get("query")
        if request.form.get("sqlfile"):
            sqlfile = request.form.get("sqlfile")
        if sqlfile and sqlquery:
            with open(os.path.join("sql", sqlfile), "w") as f:
                f.write(sqlquery)
            getsqlfiles()
            for file in sqldict.keys():
                if file == sqlfile:
                    confirm = True
    return redirect(url_for('index'))


@app.route('/saveasquery.html', methods=["POST"])
def saveasquery():
    confirm = False
    sqlquery = ""
    sqlfile = ""
    if request.method == "POST":
        if request.form.get("newquery"):
            sqlquery = request.form.get("newquery")
        if request.form.get("newfilename"):
            sqlfile = request.form.get("newfilename")
        if sqlfile and sqlquery:
            with open(os.path.join("sql", sqlfile), "w") as f:
                f.write(sqlquery)
            getsqlfiles()
            for file in sqldict.keys():
                if file == sqlfile:
                    confirm = True
    return redirect(url_for('index'))

@app.route('/upload.html', methods=["GET", "POST"])
def uploadSQL():
    confirm = False
    if request.method == "POST":
        uploadfile = request.files["filename"]
        assert uploadfile, "File Missing"
        filename = uploadfile.filename
        if filename:
            uploadfile.save(os.path.join("sql", filename))
            confirm = True
    return render_template("upload.html", confirm=confirm)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port="8000")




