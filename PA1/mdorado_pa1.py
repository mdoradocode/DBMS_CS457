# Name: Michael Dorado
# Date: 9/6/2021
# Class: CS 457 Database Managment Systems 
# Project: This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. I would like to implement a GUI to work along side this project, but I am not sure how feasible that is with the time constraints.

##---Libraries---##
#This allows me to interact with CSV files easily, there is no "managment" of files or directories, it is only used to read and write from industry standard csv files
import csv
#This allows for easy file work and listing
import os
from os import path, walk
#This allows for the path of the current directory and script directory to be easily found
import pathlib
import sys
#This is needed to delete directories
import shutil

##---Global Variables---##
#Take in user input commands
commandWhole = None
#Take in user attributes
argumentsWhole = None
#Split up the current command into a list
commandSplit = None
#Split up the current attribute input into a list
argumentsSplit = None
#This begins as the directory the file of the project resides in and follows the working directory
currentDir = pathlib.Path(__file__).parent.resolve()
#Used to set the current subdirectory without changing the directory
path = None
#List of all currently present databases
databaseList = []
#The name of the current database for use in file path definition
currentDB = []
#Menu while loop controller
menuControl = 1
#Used to assist in the query function
rows = []


def main():
    while menuControl != 0:
        clearRows()
        compileDatabaseList()
        takeCommand()
        commandInterpt()
    print("All Done.")


#Parse out the user input into cascading if else statments to decide on program direction
def commandInterpt():
    global commandSplit, currentDir,currentDB,menuControl
    #All commands that begin with CREATE, which can be followed by TABLE or DATABASE
    if commandSplit[0] == 'CREATE':
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


#This allows an attribute of a table to be added after the creation of a table
def alterTable():
    global commandSplit
    #This gives a special os variable that allows me to access the correct directory
    fullName = os.path.join(getCurrentDir(),commandSplit[2]+'.csv')
    tempList = []
    existingRow = []
    #This parses up the attributes to be added and appends it into a neat list
    for command in range(4, len(commandSplit),2):
        tempCommand = commandSplit[command] + ' ' + commandSplit[command+1]
        tempList.append(tempCommand)
    #This opens the table that is being altered and reads the first row (attributes) of the table and creates a list of the original attributes
    with open(fullName,'r',encoding='UTF8') as s:
        reader = csv.reader(s)
        existingRow = list(reader)
    #Combines the new list and the existing list
    finalRow = existingRow[0] + tempList
    #Writes the new attribute list to the file (this recreates the file, so this implementation will need to be adjusted for the next project)
    with open(fullName, 'w', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(finalRow)
    print("Updated Table " + commandSplit[2])


#Make the rows variable an empty list so that it may be used again to read the tables
def clearRows():
    global rows
    rows = []


#Read the whole file top to bottom and display its contents 
def fullFileRead():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), commandSplit[3] + '.csv')
    #Reads the whole file and throws an error if the action could not be completed
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


#Delete a table
def dropTable():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), commandSplit[2] + '.csv')
    try:
        os.remove(fullName)
        print('Dropped table ' + commandSplit[2])
    except OSError:
        print("!Failed could not drop table " + commandSplit[2] + ", may not be in current database.")


#Delete a database
def dropDatabase():
    global commandSplit
    try: 
        shutil.rmtree(os.path.join(currentDir,commandSplit[2]))
        print("Removed database " + commandSplit[2])
    except OSError:
        print('!Failed could not drop database ' + commandSplit[2])


#Get the current directory and modify the actual variable to be working in a descrete database
def getCurrentDir():
    global currentDB, currentDir
    return os.path.join(currentDir, currentDB)


#Create a table
def createTable():
    global commandSplit
    tempDir = getCurrentDir()
    fullName = os.path.join(tempDir,commandSplit[2]+'.csv')
    #This checks to make sure that the database doesnt already exist before trying to create the database
    if os.path.exists(fullName) == False:
        try:
            #If there is no arguements or a database with no attributes
            if argumentsSplit == ['']:
                f = open(fullName, "x")
            #This is the clause for table creation with arguments
            else:
                with open(fullName, 'w', encoding='UTF8',newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(argumentsSplit)
                print("Table " + commandSplit[2] + " created!")
        except:
            print("!Table failed to create: arguement format incorrect.")
    else:
        print("!Failed to create table " + commandSplit[2] + " because it already exists")


#Create a database
def createDatabase(databaseName):
    ##global path
    path = os.path.join(currentDir,databaseName)
    try:
        os.mkdir(path)
        print("Database " + commandSplit[2] + " created!")
    except OSError as error:
        print('!Failed to create database "' + databaseName + '" because it already exists.')



##This will gather a list of current databases
def compileDatabaseList():
    global databaseList
    databaseList = []
    #Walk the current directory and gather the names of all the subdirectories 
    for (dirPath, dirNames, fileNames) in walk(currentDir):
        databaseList.extend(dirNames)



##This takes in command line user prompts and turns them into lists for access
def takeCommand():
    global commandWhole,argumentsWhole,argumentsSplit,commandSplit
    tempInput = input('Enter Command: ')
    try:
        #This is the clause for commands with attribute arguments to parse up
        commandWhole, argumentsWhole = tempInput.split(' (')
        ##This is needed to take off the trailing ');'
        argumentsWhole = argumentsWhole.removesuffix(');')
        argumentsSplit = argumentsWhole.split(', ')
        commandSplit = commandWhole.split(' ')
    except ValueError:
        #This is the clause for commmands that do not involve attributes/arguements
        commandWhole = tempInput.removesuffix(';')
        commandSplit = commandWhole.split(' ')


main()