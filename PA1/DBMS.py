# Name: Michael Dorado
# Date: 9/6/2021
# Class: CS 457 Database Managment Systems 
# Project: This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. I would like to implement a GUI to work along side this project, but I am not sure how feasible that is with the time constraints.
# Functionailites to implement:
#   After the program has started, from the terminal you should be able to 
#!       "CREATE DATABASE db_name" <enter> **Create a database directory to store tables 
#!       "USE db_name" <enter> **Specify that the tables we will be working with are under a certain database
#!       "CREATE TABLE test_tbl (a1 int, a2 char(9))" <enter> **Create a table with the dynamically specified contents
#       "DROP DATABASE db_name" <enter> **Delete the database and its underlying contents
#       "DROP TABLE test_tbl" <enter> **Delete the table and its contents, maybe add a warning message
#       "SELECT * FROM test_tbl" <enter> **Display the table contents as they currently stand
#       "ALTER TABLE test_tbl ADD a3 float" <enter> **Add an attribute to the selected table
# Functions to implement
#!   Database Create
#!   Database Destroy
#!   Table create
#!   Table destroy
#!   Query (Display Table contents)
#   update Table
#   Help function to display commands
#   CREATE TABLE tbl_1 (a1 int, a2 varchar(20))
#   CREATE TABLE tbl_2 (a1 Float, a2 varchar(40))
#   CREATE TABLE tbl_3 (a1 longInt, a2 varchar(20), a3 string(60))
#   SELECT * FROM 

##---Libraries---##
#This allows me to interact with CSV files easily
import csv
#This allows for easy file work and listing
import os
from os import path, read, walk
#This allows for the path of the current directory and script directory to be easily found
import pathlib
import sys
import shutil

##---Global Variables---##
#For directories and taking in commands
commandWhole = None
argumentsWhole = None
commandSplit = None
argumentsSplit = None
##scriptDir = pathlib.Path(__file__).parent.resolve()
currentDir = pathlib.Path(__file__).parent.resolve()
path = None
databaseList = []
currentDB = []
menuControl = 1
rows = []


def main():
    while menuControl != 0:
        clearRows()
        compileDatabaseList()
        takeCommand()
        commandInterpt()
    print("All Done.")

def commandInterpt():
    global commandSplit, currentDir,currentDB,menuControl
    #All commands that begin with CREATE, which can be followed by TABLE or DATABASE
    if commandSplit[0] == 'CREATE':
        ##This also needs to make sure you are accessing a database
        if commandSplit[1] == 'TABLE':
            if currentDB != []:
                createTable()
            else:
                print("!Failed to make " + commandSplit[2] + " because you are not in a Database")
        elif commandSplit[1] == 'DATABASE':
                createDatabase(commandSplit[2])
    elif commandSplit[0] == 'USE':
        ##A Database will be the only command to follow this one
        if commandSplit[1] in databaseList:
            currentDB = commandSplit[1]
            print('Now using Database '+ currentDB + '!')
        else:
            ##Send them back to the command loop
            print("!Failed to use " + commandSplit[1])
    elif commandSplit[0] == 'DROP':
        if commandSplit[1] == 'TABLE':
            dropTable()
        elif commandSplit[1] == 'DATABASE':
            dropDatabase()
    elif commandSplit[0] == 'SELECT':
        #Will always be followed by * FROM tableName
        #Will need to be expanded for future projects
        if currentDB != []:
            fullFileRead()
        else:
            print('!Failed not currently in a database.')
    elif commandSplit[0] == 'ALTER':
        if commandSplit[1] == 'TABLE':
            if commandSplit[3] == 'ADD':
                alterTable()
    elif commandSplit[0] == '.EXIT':
        menuControl = 0
    else:
        print("!Failed: Command not recognized")
def alterTable():
    global commandSplit
    fullName = os.path.join(getCurrentDir(),commandSplit[2]+'.csv')
    tempList = []
    for command in range(4, len(commandSplit),2):
        tempCommand = commandSplit[command] + ' ' + commandSplit[command+1]
        tempList.append(tempCommand)
        print(tempCommand)
    with open(fullName, 'w', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(argumentsSplit)
        print(argumentsSplit)
def clearRows():
    global rows
    rows = []
def fullFileRead():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), commandSplit[3] + '.csv')
    try:
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            for row in reader:
                rows.append(row)
            for row in rows:
                for col in row:
                   print('{:>5}'.format(col) + ' | ' , end= '')
                print("\n")
    except:
        print("!Failed to read file.")

def dropTable():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), commandSplit[2] + '.csv')
    try:
        os.remove(fullName)
        print('Dropped table ' + commandSplit[2])
    except OSError:
        print("!Failed could not drop table " + commandSplit[2] + ", may not be in current database.")

def dropDatabase():
    global commandSplit
    try: 
        shutil.rmtree(os.path.join(currentDir,commandSplit[2]))
        print("Removed database " + commandSplit[2])
    except OSError:
        print('!Failed could not drop database ' + commandSplit[2])

def getCurrentDir():
    global currentDB, currentDir
    return os.path.join(currentDir, currentDB)


def createTable():
    global commandSplit
    tempDir = getCurrentDir()
    fullName = os.path.join(tempDir,commandSplit[2]+'.csv')
    if os.path.exists(fullName) == False:
        try:
            if argumentsSplit == ['']:
                f = open(fullName, "x")
            else:
                with open(fullName, 'w', encoding='UTF8',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(argumentsSplit)
                    print(argumentsSplit)
                print("Table " + commandSplit[2] + " created!")
        except:
            print("!Table failed to create: arguement format incorrect.")
    else:
        print("!Failed to create table " + commandSplit[2] + " because it already exists")

def createDatabase(databaseName):
    ##global path
    path = os.path.join(currentDir,databaseName)
    try:
        os.mkdir(path)
        print("Database " + commandSplit[2] + " created!")
    except OSError as error:
        print('!Failed to create database "' + databaseName + '" because it already exists.')

##This will gather a list of current databases##
def compileDatabaseList():
    global scriptDir, databaseList
    databaseList = []
    for (dirPath, dirNames, fileNames) in walk(currentDir):
        databaseList.extend(dirNames)

##This takes in command line user prompts and turns them into lists for access##
def takeCommand():
    global commandWhole,argumentsWhole,argumentsSplit,commandSplit
    tempInput = input('Enter Command: ')
    try:
        commandWhole, argumentsWhole = tempInput.split(' (')
        ##This is needed to take off the trailing ')'
        argumentsWhole = argumentsWhole.removesuffix(')')
        argumentsSplit = argumentsWhole.split(', ')
        commandSplit = commandWhole.split(' ')
    except ValueError:
        commandSplit = tempInput.split(' ')


main()