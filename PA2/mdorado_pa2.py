# Name: Michael Dorado
# Date: 10/6/2021
# Class: CS 457 Database Managment Systems 
# Project: This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. Adding to the last version of this code, PA1, there will be implementation for data handling within this iteration including inserting data, deleting data, querying data and updating data

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
#List of all currently present tables in a database
tableList = []
#The name of the current database for use in file path definition
currentDB = []
#Menu while loop controller
menuControl = 1
#Used to assist in the query function
rows = []
#Used to keep track of different types of input for users 
userInput = []
#Used to keep track of the current table command if needed
currentTable = []


#---Main Program---#
def main():
    while menuControl != 0:
        clearRows()
        compileDatabaseList()
        takeCommand()
        commandInterpt()
    print("All Done.")

#---Helper Functions---#
#Parse out the user input into cascading if else statments to decide on program direction
def commandInterpt():
    global commandSplit,currentDir,currentDB,menuControl,currentTable
    #All commands that begin with CREATE, which can be followed by TABLE or DATABASE
    if commandSplit[0].upper() == 'CREATE':
        if commandSplit[1].upper() == 'TABLE':
            if currentDB != []:
                currentTable = commandSplit[2]
                createTable()
                compileTableList()
            else:
                print("!Failed to make " + currentTable + " because you are not in a Database")
        elif commandSplit[1].upper() == 'DATABASE':
                createDatabase()

    elif commandSplit[0].upper() == 'USE':
        ##A Database will be the only command to follow this one
        if commandSplit[1] in databaseList:
            currentDB = commandSplit[1]
            print('Now using Database '+ currentDB + '!')
            compileTableList()
        else:
            ##Send them back to the command loop
            print("!Failed to use " + commandSplit[1])

    elif commandSplit[0].upper() == 'DROP':
        if commandSplit[1].upper() == 'TABLE':
            currentTable = commandSplit[2]
            dropTable()
            compileTableList()
        elif commandSplit[1].upper() == 'DATABASE':
            dropDatabase()

    elif commandSplit[0].upper() == 'SELECT':
        #Will need to be expanded for future projects
        currentTable = commandSplit[3]
        if currentDB != []:
            if commandSplit[1] == '*':
                fullFileRead()
            else:
                selectiveFileRead()
        else:
            print('!Failed not currently in a database.')

    elif commandSplit[0].upper() == 'ALTER':
        if commandSplit[1] == 'TABLE':
            currentTable = commandSplit[2]
            if commandSplit[3] == 'ADD':
                alterTable()

    elif commandSplit[0].upper() == 'INSERT':
        currentTable = commandSplit[2]
        if commandSplit[2]+'.csv' in tableList:
            insertValue()
        else:
            print('Failed')

    elif commandSplit[0].upper() == '.EXIT':
        menuControl = 0

    elif commandSplit[0].upper() == 'UPDATE':
        currentTable = commandSplit[1]
        if commandSplit[2].upper() == 'SET':
            updateRecords()
        else:
            print("Failed")
    elif commandSplit[0].upper() == 'DELETE':
        if currentDB != []:
            currentTable = commandSplit[2]
            deleteRow()
        else:
            print('!Failed not currently in a database.')
        
    else:
        print("!Failed: Command not recognized")

def countAttributesBeforeFrom(displayAttributes,indexOfFrom):
    for index in range(1, len(commandSplit)):
        if commandSplit[index].upper() == 'FROM':
            indexOfFrom = index
            break
        else:
            commandSplit[index].rstrip(",")
            displayAttributes.append(commandSplit[index])
        

def selectiveFileRead():
    displayAttributes = []
    indexOfFrom = 0
    countAttributesBeforeFrom(displayAttributes,indexOfFrom)
    print(displayAttributes)
    print(indexOfFrom)

def deleteRow():
    changeCounter = 0
    attributeToFind = findColumn(commandSplit[4])
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    if attributeToFind == "Attribute not present":
        print("Unable to update record, attribute not present")
    else:
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            header = next(reader)
            tempFile = os.path.join(getCurrentDir(), 'tempFile.csv')
            with open(tempFile, 'w', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in reader:
                    if commandSplit[5] == '>':
                        if float(row[attributeToFind]) > float(commandSplit[6]):
                            changeCounter += 1
                        else:
                            writer.writerow(row)
                    elif commandSplit[5] == '=':
                        if row[attributeToFind] == commandSplit[6]:
                            changeCounter += 1
                        else:
                            writer.writerow(row)
                    elif commandSplit[5] == '<':
                        if float(row[attributeToFind]) < float(commandSplit[6]):
                            changeCounter += 1
                        else:
                            writer.writerow(row)
        with open(tempFile, 'r', encoding='UTF8',newline='') as f:
            reader = csv.reader(f)
            with open(fullName,"w",encoding="UTF8") as destination:
                writer = csv.writer(destination)
                for row in reader:
                    writer.writerow(row)
        os.remove(tempFile)
        print("{} record(s) deleted".format(changeCounter))

def modifyRow(row,attributeToUpdate):
    row[attributeToUpdate] = commandSplit[5]
    return row


def findColumn(attribute):
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    with open(fullName,"r",encoding="UTF8") as source:
        reader = csv.reader(source)
        header = next(reader)
        for col in header:
            if col.startswith(attribute):
                return header.index(col)
    return "Attribute not present"
        

def updateRecords():
    changeCounter = 0
    attributeToFindUpdate = findColumn(commandSplit[7])
    attributeToUpdate = findColumn(commandSplit[3])
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    if attributeToUpdate == "Attribute not present":
        print("Unable to update record, attribute not present")
    else:
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            tempFile = os.path.join(getCurrentDir(), 'tempFile.csv')
            with open(tempFile, 'w', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                for row in reader:
                    if row[attributeToFindUpdate] == commandSplit[9]:
                        changeCounter += 1
                        row = modifyRow(row,attributeToUpdate)
                        writer.writerow(row)
                    else:
                        writer.writerow(row)
        with open(tempFile, 'r', encoding='UTF8',newline='') as f:
            reader = csv.reader(f)
            with open(fullName,"w",encoding="UTF8") as destination:
                writer = csv.writer(destination)
                for row in reader:
                    writer.writerow(row)
        os.remove(tempFile)
        print("{} record(s) modified".format(changeCounter))
    


#This method will allow for inserting of data into the predetermined fields of the database
def insertValue():
    fullName = os.path.join(getCurrentDir(),currentTable+'.csv')
    with open(fullName, 'a', encoding='UTF8',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(argumentsSplit)
    print("1 new record inserted.")


#This allows an attribute of a table to be added after the creation of a table
def alterTable():
    global commandSplit
    #This gives a special os variable that allows me to access the correct directory
    fullName = os.path.join(getCurrentDir(),currentTable+'.csv')
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
    print("Updated Table " + currentTable)


#Make the rows variable an empty list so that it may be used again to read the tables
def clearRows():
    global rows
    rows = []


#Read the whole file top to bottom and display its contents 
def fullFileRead():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    #Reads the whole file and throws an error if the action could not be completed
    try:
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            for row in reader:
                rows.append(row)
            for row in rows:
                for col in row:
                   print('{:>15}'.format(col) + ' | ', end= '')
                print("\n")
    except:
        print("!Failed to read file.")


#Delete a table
def dropTable():
    global commandSplit
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    try:
        os.remove(fullName)
        print('Dropped table ' + currentTable)
    except OSError:
        print("!Failed could not drop table " + currentTable + ", may not be in current database.")


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
    fullName = os.path.join(tempDir,currentTable+'.csv')
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
                print("Table " + currentTable + " created!")
        except:
            print("!Table failed to create: arguement format incorrect.")
    else:
        print("!Failed to create table " + currentTable + " because it already exists")


#Create a database
def createDatabase():
    ##global path
    databaseName = commandSplit[2]
    path = os.path.join(currentDir,databaseName)
    try:
        os.mkdir(path)
        print("Database " + databaseName + " created!")
    except OSError as error:
        print('!Failed to create database "' + databaseName + '" because it already exists.')


##This method will compile a list of all the tables currently in the working database
def compileTableList():
    global tableList
    tableList = []
    tempDir = getCurrentDir()
    #Walk the current directory (Database) and gather the names of all the files (Tables) 
    for (dirPath, dirNames, fileNames) in walk(tempDir):
        tableList.extend(fileNames)

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
    userInput = input('Enter Command: ')
    try:
        #This is the clause for commands with attribute arguments to parse up
        commandWhole, argumentsWhole = userInput.split(' (')
        ##This is needed to take off the trailing ');'
        argumentsWhole = argumentsWhole.removesuffix(');')
        argumentsSplit = argumentsWhole.split(', ')
        commandSplit = commandWhole.split(' ')
    except ValueError:
        try:
        
            commandWhole, argumentsWhole = userInput.split('values(')
            ##This is needed to take off the trailing ');'
            argumentsWhole = argumentsWhole.removesuffix(');')
            argumentsSplit = argumentsWhole.split(',')
            commandSplit = commandWhole.split(' ')
            argumentsSplit = list(map(str.strip,argumentsSplit))

        except ValueError:
        #This is the clause for commmands that do not involve attributes/arguements
            commandWhole = userInput.removesuffix(';')
            commandSplit = commandWhole.split(' ')


main()