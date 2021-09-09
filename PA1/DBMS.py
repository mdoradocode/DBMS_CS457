# Name: Michael Dorado
# Date: 9/6/2021
# Class: CS 457 Database Managment Systems 
# Project: This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. I would like to implement a GUI to work along side this project, but I am not sure how feasible that is with the time constraints.
# Functionailites to implement:
#   After the program has started, from the terminal you should be able to 
#       "CREATE DATABASE db_name" <enter> **Create a database directory to store tables 
#       "USE db_name" <enter> **Specify that the tables we will be working with are under a certain database
#       "CREATE TABLE test_tbl (a1 int, a2 char(9))" <enter> **Create a table with the dynamically specified contents
#       "DROP DATABASE db_name" <enter> **Delete the database and its underlying contents
#       "DROP TABLE test_tbl" <enter> **Delete the table and its contents, maybe add a warning message
#       "SELECT * FROM test_tbl" <enter> **Display the table contents as they currently stand
#       "ALTER TABLE test_tbl ADD a3 float" <enter> **Add an attribute to the selected table
# Functions to implement
#   Database Create
#   Database Destroy
#   Table create
#   Table destroy
#   Database Create
#   Query (Display Table contents)
#   update Table
#   Help function to display commands
#   CREATE TABLE tbl_1 (a1 int, a2 varchar(20))

##---Libraries---##
#This allows me to interact with CSV files easily
import csv
#This allows for easy file work and listing
from os import path, walk
import os
#This allows for the path of the current directory and script directory to be easily found
import pathlib

##---Global Variables---##
#For directories and taking in commands
commandWhole = None
argumentsWhole = None
commandSplit = None
argumentsSplit = None
scriptDir = pathlib.Path(__file__).parent.resolve()
currentDir = pathlib.Path(__file__).parent.resolve()
path = None
databaseList = []
##maybe not going to work
currDBTables = []


def main():
    print(scriptDir)
    print(currentDir)
    checkDatabaseList()
    takeCommand()
    createDatabase('db_1')


    ##example = Table(commandSplit[2], *argumentsSplit)

def createDatabase(databaseName):
    global path
    path = os.path.join(scriptDir,databaseName)
    try:
        os.mkdir(path)
    except OSError as error:
        print('!Failed to create database "' + databaseName + '" because it already exists.')

##This lists the current working directory/database##
##def getCurrDir():
    ##global currentDir
    ##print("The current working dir is: ")
    ##print(currentDir)

##This will gather a list of current databases##
def checkDatabaseList():
    global scriptDir, databaseList
    for (dirPath, dirNames, fileNames) in walk(scriptDir):
        databaseList.extend(dirNames)
    print(databaseList)

##This will gather a list of current tables in the working database##
def checkTables():
    global currentDir

##This takes in command line user prompts and turns them into lists for access##
def takeCommand():
    global commandWhole,argumentsWhole,argumentsSplit,commandSplit
    commandWhole, argumentsWhole = input('Enter Command: ').split(' (')
    argumentsWhole = argumentsWhole.removesuffix(')')
    ##This is needed to take off the trailign ')'
    argumentsWhole = argumentsWhole.removesuffix(')')

    argumentsSplit = argumentsWhole.split(',')
    commandSplit = commandWhole.split(' ')
    pass

##Table Class##
class Table:
    def __init__(self, tableName, *args):
        ##Need to check if the table exists before creating one and throw error if it does
        with open(tableName + '.csv', 'w', encoding='UTF8',newline='') as f:
            writer = csv.writer(f)
            writer.writerow(args)
    def deleteTable(self):
        pass


main()