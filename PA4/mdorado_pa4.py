# Name: Michael Dorado
# Date: 11/21/2021
# Class: CS 457 Database Managment Systems 
# Project: This project is a base level implementation of a multithreaded database program. By implementing a locking feature we can ensure only concurrent access to tables so that there are no transaction errors.

##---Libraries---##
#This allows me to interact with CSV files easily, there is no "managment" of files or directories, it is only used to read and write from industry standard csv files
import csv
#This allows for easy file work and listing
import os
from os import path, read, walk
#This allows for the path of the current directory and script directory to be easily found
import pathlib
import sys
#This is needed to delete directories
import shutil
#This is used to implement sleep functions as the code moves to fast for examples
import time
#This is used to avoid collisions
import random

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
#This is used in reading in command scripts and will be appened to if a command spans mutiple lines
lastFileLineRead = ""
#This is used when a command spans more than one line, its a temp string holder
tempFileLineRead = ""
#This is used in cases of selective read, which need to know the distance for the statement 'where'
indexFromWhere = 0
#This is used to hold all of the comparison operators for a given command
attributeCompareList = []
#When mutiple files are going to be joined and read, this is used for storing the reference to them
tableDict = {}
#
attributeDict = {}

processID = 0

readInFlag = 0

tempCommandsCache = []
#This is used as the locking mechanic, it is a static path
lockPath = os.path.join(pathlib.Path(__file__).parent.resolve(),'lockFile')
#This is the static path used to store lock file variables
processIDDir = os.path.join(pathlib.Path(__file__).parent.resolve(),'processIDDir')
#This is a bit flip flag that is used to determine if a process has permission to write a variable
lockFlag = 0



#---Main Program---#
def main():
    global lastFileLineRead, tempFileLineRead, processID
    #Create a random interval when start two process at the same time as to avoid collisons
    time.sleep(random.uniform(0,1))
    #Checks to see if the locking directory exists (i.e. is this the first process) make it if it is the first process
    if not os.path.isdir(processIDDir):
        os.mkdir(processIDDir)
        setProcessID()
    #If not the first process, wait 1 second and then set the process ID
    else:
        time.sleep(1)
        setProcessID()    
    #Open up the test file named PA4_test.sql   
    with open("PA4_test.sql",'r', encoding='UTF8') as filePointer:
        while menuControl != 0:
            #Reset these two variables for use
            lastFileLineRead = ""
            tempFileLineRead = ""
            #Read in a command from the sql file, if the command is multiple lines, recursively call this function on the next line of the file
            readInFileLine(filePointer)
            #Clear out the rows global variable that is used for queries
            clearRows()
            #Search the directory that the program script resides in and list all directories for use in queries
            compileDatabaseList()
            #Translate the raw command string into a list of commandSplit and arguementSplit (if applicable)
            takeCommand()
            #Interpret and preform the command
            commandInterpt()
            #Small delay to avoid collisions
            time.sleep(.5)
    #Destroy the process file and destroy the directory if all process files are destroyed
    destroyProcess()
    print("All Done.")


#---Helper Functions for Concurrent Process Managment---#
#Observe the processes already made and assign the process ID based on that.
def setProcessID():
    global processID
    processID = len([name for name in os.listdir(processIDDir) if os.path.isfile(os.path.join(processIDDir, name))]) + 1
    tempName = os.path.join(processIDDir, "process" + str(processID))
    f=open(tempName,'x')
    time.sleep(1)
#Look at the process DIR and find if the process is present in the file, if it is destroy it
def destroyProcess():
    global processID
    tempName = os.path.join(processIDDir, "process" + str(processID))
    os.remove(tempName)
    #If there are no files in the DIR, destroy the DIR as well
    if len([name for name in os.listdir(processIDDir) if os.path.isfile(os.path.join(processIDDir, name))]) == 0:
        shutil.rmtree(processIDDir)
#Check to see if the lock is available from the lock path, if so acquire it
def acquireLock():
    global lockPath,lockFlag
    print("Begin Transaction:")
    if os.path.exists(lockPath):
        lockFlag = 0
    else:
        f=open(lockPath,'x')
        lockFlag = 1



#---Helper Functions for File I/O---#
#When updating a value with concurrent processes, cache the commands to make sure they can be executed
def updateTempCommandCache():
    tempCommandsCache.append(lastFileLineRead)
#This is used to help deal with some nonsense off the commented out portions of the SQL code
def trimTempFileLineRead():
    global tempFileLineRead
    if "--" in tempFileLineRead:
        tempFileLineRead,throwAway = tempFileLineRead.split(';',1)
        tempFileLineRead = tempFileLineRead +';'+'\n'
#This function acts as a mid point between command interpretation and the test file, it determines what is comment and what isnt, what should be read by what process, and can parse multi-line commands
def readInFileLine(filePointer):
    global lastFileLineRead, tempFileLineRead,readInFlag
    tempFileLineRead = filePointer.readline()
    #This case skips a line if it is empty or a newline
    if tempFileLineRead.startswith('\n'):
        readInFileLine(filePointer)
    #This is to check if this process is allowed to read the following section
    elif tempFileLineRead.startswith("-- On "):
        if tempFileLineRead.find(str(processID)) != -1:
            readInFlag = 1
        else:
            readInFlag = 0
        readInFileLine(filePointer)
    #This is if we are at the exit command (.exit)
    elif tempFileLineRead.startswith('.'):
        tempFileLineRead = tempFileLineRead.rstrip('\n')
        tempFileLineRead = tempFileLineRead.rstrip()
        lastFileLineRead = tempFileLineRead
    #If the file is allowed to read in a sectiom, this is where it is actually done
    elif readInFlag == 1:
        trimTempFileLineRead()
        if tempFileLineRead.endswith(';', len(tempFileLineRead)-2, len(tempFileLineRead)-1) == True:
            #If this is the first line of a command
            if not lastFileLineRead:
                tempFileLineRead = tempFileLineRead.rstrip('\n')
                tempFileLineRead = tempFileLineRead.rstrip()
                lastFileLineRead = tempFileLineRead
            #If this is a secondary line of a command
            else:
                tempFileLineRead = tempFileLineRead.rstrip('\n')
                tempFileLineRead = tempFileLineRead.rstrip()
                lastFileLineRead = lastFileLineRead + ' ' + tempFileLineRead
        else:
            #If this is the first line of a command
            if not lastFileLineRead:
                tempFileLineRead = tempFileLineRead.rstrip('\n')
                tempFileLineRead = tempFileLineRead.rstrip()
                lastFileLineRead = tempFileLineRead
                readInFileLine(filePointer)
            #If this is a secondary line of a command
            else:
                tempFileLineRead = tempFileLineRead.rstrip('\n')
                tempFileLineRead = tempFileLineRead.rstrip()
                lastFileLineRead = lastFileLineRead + ' ' + tempFileLineRead
                readInFileLine(filePointer)
    #If there is a throw away line, recurse
    elif tempFileLineRead.startswith('-'):
        readInFileLine(filePointer) 
    else:
        readInFileLine(filePointer) 
#This method takes in various queries and optimizes the statment for use, replaces certain verbage with other, standardized verbage
def optimizeSelect():
    global commandSplit, indexFromWhere
    indexFromWhere = 0
    if 'join'in commandSplit:
        commandSplit.remove('join')
        commandSplit = ['where' if x == 'on' else x for x in commandSplit]
        if 'left' in commandSplit:
            commandSplit.remove('left')
            commandSplit.insert(commandSplit.index('where')-indexFromWhere, 'left')
            indexFromWhere += 1
        elif 'right' in commandSplit:
            commandSplit.remove('right')
            commandSplit.insert(commandSplit.index('where')-indexFromWhere, 'right')
            indexFromWhere += 1
        if 'inner' in commandSplit:
            commandSplit.remove('inner')
            commandSplit.insert(commandSplit.index('where')-indexFromWhere, 'inner')
            indexFromWhere += 1
        elif 'outer' in commandSplit:
            commandSplit.remove('outer')
            commandSplit.insert(commandSplit.index('where')-indexFromWhere, 'outer')
            indexFromWhere += 1
    commandSplit = [arguements.rstrip(',') for arguements in commandSplit]




#---Helper Functions for Command Processing and Interpretation---#
#Parse out the user input into cascading if else statments to decide on program direction
def commandInterpt():
    global commandSplit,currentDir,currentDB,menuControl,currentTable,lastFileLineRead,lockFlag
    #All commands that begin with CREATE, which can be followed by TABLE or DATABASE
    if commandSplit[0].upper() == 'CREATE':
        if commandSplit[1].upper() == 'TABLE':
            if currentDB != []:
                currentTable = commandSplit[2].lower()
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
            currentTable = commandSplit[2].lower()
            dropTable()
            compileTableList()
        elif commandSplit[1].upper() == 'DATABASE':
            dropDatabase()

    elif commandSplit[0].upper() == 'SELECT':
        #Will need to be expanded for future projects
        if currentDB != []:
            optimizeSelect()
            #Write a function to change on to where in the command split here
            if commandSplit[1] == '*':
                if 'where' in commandSplit:
                    selectiveJoinFileRead()
                else:
                    currentTable = commandSplit[3].lower()
                    fullFileRead()
            else:
                selectiveFileRead()
        else:
            print('!Failed not currently in a database.')

    elif commandSplit[0].upper() == 'ALTER':
        if commandSplit[1] == 'TABLE':
            currentTable = commandSplit[2].lower()
            if commandSplit[3] == 'ADD':
                alterTable()

    elif commandSplit[0].upper() == 'INSERT':
        currentTable = commandSplit[2].lower()
        if commandSplit[2].lower()+'.csv' in tableList:
            insertValue()
        else:

            print('Failed')

    elif commandSplit[0].upper() == '.EXIT':
        menuControl = 0
        if os.path.exists(lockPath):
            os.remove(lockPath)

    elif commandSplit[0].upper() == 'UPDATE':
        currentTable = commandSplit[1].lower()
        if commandSplit[2].upper() == 'SET':
            updateTempCommandCache()
        else:
            print("Failed")
    elif commandSplit[0].upper() == 'DELETE':
        if currentDB != []:
            currentTable = commandSplit[2].lower()
            deleteRow()
        else:
            print('!Failed not currently in a database.')
    elif commandSplit[0].upper() == 'BEGIN' and commandSplit[1].upper() == 'TRANSACTION':
        acquireLock()
    elif commandSplit[0].upper() == 'COMMIT':
        if lockFlag == 1:
            for command in tempCommandsCache:
                lastFileLineRead = command
                takeCommand()
                time.sleep(1)
                updateRecords()
            lockFlag = [0]
            with open(lockPath, 'w', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(lockFlag)
            lockFlag = 0
            print("Transaction Commited")
        elif lockFlag == 0:
            print("Transaction Abort")
    else:
        print("!Failed: Command not recognized") 
#This method finds the number of attributes before from, this is used in processing reading select attributes from a file
def countAttributesBeforeFrom(displayAttributesIndex):
    for index in range(1, len(commandSplit)):
        if commandSplit[index].upper() == 'FROM':
            return index
        else:
            displayAttributesIndex.append(index)
#This method creates a list of attributes to look at between tables and will be evaluated in sets of two
def createSelectAttributeDict():
    global attributeCompareList
    thisDict = {}
    whereIndex = commandSplit.index('where')
    itemIndex = whereIndex + 1
    while itemIndex < len(commandSplit):
        if commandSplit[itemIndex] in ('=','>','<','<=', '>='):
            attributeCompareList = commandSplit[itemIndex]
        else:
            attribute = commandSplit[itemIndex].split('.')
            thisDict[attribute[0]] = attribute[1]
        itemIndex+=1
    return thisDict
##This takes in command line user prompts and turns them into lists for access
def takeCommand():
    global commandWhole,argumentsWhole,argumentsSplit,commandSplit
    userInput = lastFileLineRead
    #Base case of commands and arguments
    try:
        #This is the clause for commands with attribute arguments to parse up
        commandWhole, argumentsWhole = userInput.split(' (')
        ##This is needed to take off the trailing ');'
        argumentsWhole = argumentsWhole.rstrip(');')
        argumentsSplit = argumentsWhole.split(', ')
        commandSplit = commandWhole.split(' ')
        if commandSplit[len(commandSplit)-1] == 'values':
            raise ValueError   
    #This is a case for some of the file io we got for some reason
    except ValueError as err:
        try:
        
            commandWhole, argumentsWhole = userInput.split(' (')
            ##This is needed to take off the trailing ');'
            argumentsWhole = argumentsWhole.rstrip(');')
            argumentsSplit = argumentsWhole.split(',')
            commandSplit = commandWhole.split(' ')
            argumentsSplit = list(map(str.strip,argumentsSplit))

        except ValueError as err2:
        #This is the clause for commmands that do not involve attributes/arguements
            commandWhole = userInput.rstrip(';')
            commandSplit = commandWhole.split(' ')
  


#---Helper Functions for File Readin---#
#This method displays the contents of a table, only displaying specific contents
def selectiveFileRead():
    global currentTable
    displayAttributesIndex = []
    #This is a number that gives the position of from, which is used to calculate other arguments of a selctive display
    indexOfFrom = countAttributesBeforeFrom(displayAttributesIndex)
    currentTable = commandSplit[indexOfFrom + 1].lower()
    #This is the attribute that is being searched for when determining what rows to display
    attributeToFind = findColumn(commandSplit[indexOfFrom + 3])
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    if attributeToFind == "Attribute not present":
        print("Unable to display record, attribute not present")
    else:
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            header = next(reader)
            tempFile = os.path.join(getCurrentDir(), 'tempFile.csv')
            #Write the desired information to a temp file
            with open(tempFile, 'w', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                #This if else statment is to determine what kind of operator is being used for the searching attribute
                for row in reader:
                    if commandSplit[indexOfFrom+4] == '>':
                        if float(row[attributeToFind]) > float(commandSplit[indexOfFrom+5]):
                            writer.writerow(row)
                    elif commandSplit[indexOfFrom+4] == '=':
                        if row[attributeToFind] == commandSplit[indexOfFrom+5]:
                            writer.writerow(row)
                    elif commandSplit[indexOfFrom+4] == '!=':
                        if row[attributeToFind] != commandSplit[indexOfFrom+5]:
                            writer.writerow(row)
                    elif commandSplit[indexOfFrom+4] == '<':
                        if float(row[attributeToFind]) < float(commandSplit[indexOfFrom+5]):
                            writer.writerow(row)
    #Read and display the temp file 
    with open(tempFile,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            for row in reader:
                rows.append(row)
            for row in rows:
                printingIndex = 0
                for col in row:
                    if printingIndex in displayAttributesIndex:
                        print('{:>15}'.format(col) + ' | ', end= '')
                    printingIndex+=1
                print("\n")
    os.remove(tempFile)
#This method merges two tables into one table based on the type of join provided (this is a gross function dont stress about it)
def mergeTables(table1Path, table2Path,attributecomaprisonIndex,attributeCompareList,tempFile):
    global currentTable
    #The code below this an above the if statement creates the index value for the columns that will be compared between the two tables
    currentTable = table1Path
    valuesView = attributeDict.values()
    valuesIterator = iter(valuesView)
    value = next(valuesIterator)
    table1ColIndex = findColumn(value)
    currentTable = table2Path
    value = next(valuesIterator)
    table2ColIndex = findColumn(value)
    #If this is an outer left join
    if 'left' in commandSplit:
        with open(tempFile,"w",encoding='UTF8') as tempFileSource:
            tempFileWriter = csv.writer(tempFileSource)
            with open(table1Path + '.csv',"r",encoding="UTF8") as table1Source:
                table1Reader = csv.reader(table1Source)
                table1Header = next(table1Reader)
                with open(table2Path + '.csv', "r", encoding="UTF8") as table2Source:
                    table2Reader = csv.reader(table2Source)
                    table2Header = next(table2Reader)
                    tempFileWriter.writerow(table1Header+table2Header)
                    for table1Row in table1Reader:
                        noMatchBit = 0
                        for table2Row in table2Reader:
                            if attributeCompareList[attributecomaprisonIndex] == '>':
                                if table1Row[table1ColIndex] > table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                                    noMatchBit = 1
                            elif attributeCompareList[attributecomaprisonIndex] == '=':
                                if table1Row[table1ColIndex] == table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                                    noMatchBit = 1
                            elif attributeCompareList[attributecomaprisonIndex] == '!=':
                                if table1Row[table1ColIndex] != table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                                    noMatchBit = 1
                            elif attributeCompareList[attributecomaprisonIndex] == '<':
                                if table1Row[table1ColIndex] < table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                                    noMatchBit = 1
                        if noMatchBit == 0:
                            tempFileWriter.writerow(table1Row)
                        table2Source.seek(0)

    #This is if it is an outer right join
    elif 'right' in commandSplit:
        with open(tempFile,"w",encoding='UTF8') as tempFileSource:
            tempFileWriter = csv.writer(tempFileSource)
            with open(table1Path + '.csv',"r",encoding="UTF8") as table1Source:
                table1Reader = csv.reader(table1Source)
                table1Header = next(table1Reader)
                with open(table2Path + '.csv', "r", encoding="UTF8") as table2Source:
                    table2Reader = csv.reader(table2Source)
                    table2Header = next(table2Reader)
                    tempFileWriter.writerow(table1Header+table2Header)
                    for table1Row in table1Reader:
                        noMatchBit = 0
                        for table2Row in table2Reader:
                            if attributeCompareList[attributecomaprisonIndex] == '>':
                                if table1Row[table1ColIndex] > table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '=':
                                if table1Row[table1ColIndex] == table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '!=':
                                if table1Row[table1ColIndex] != table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '<':
                                if table1Row[table1ColIndex] < table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                        if noMatchBit == 0:
                                    tempList = []
                                    for x in table1Row:
                                        tempList.append('')
                                    tempFileWriter.writerow(tempList + table2Row)
                        table2Source.seek(0) 
    #this is if its an inner join 
    else:
        with open(tempFile,"w",encoding='UTF8') as tempFileSource:
            tempFileWriter = csv.writer(tempFileSource)
            with open(table1Path + '.csv',"r",encoding="UTF8") as table1Source:
                table1Reader = csv.reader(table1Source)
                table1Header = next(table1Reader)
                with open(table2Path + '.csv', "r", encoding="UTF8") as table2Source:
                    table2Reader = csv.reader(table2Source)
                    table2Header = next(table2Reader)
                    tempFileWriter.writerow(table1Header+table2Header)
                    for table1Row in table1Reader:
                        for table2Row in table2Reader:
                            if attributeCompareList[attributecomaprisonIndex] == '>':
                                if table1Row[table1ColIndex] > table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '=':
                                if table1Row[table1ColIndex] == table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '!=':
                                if table1Row[table1ColIndex] != table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                            elif attributeCompareList[attributecomaprisonIndex] == '<':
                                if table1Row[table1ColIndex] < table2Row[table2ColIndex]:
                                    tempFileWriter.writerow(table1Row+table2Row)
                        table2Source.seek(0) 
#This method will look at a number of files and make them into a singular display
def selectiveJoinFileRead(): 
    global currentTable,commandSplit, attributeCompareList,tableDict,attributeDict
    tableDict = createSelectTableDict()
    attributeDict = createSelectAttributeDict()
    filePathList = []
    tableToCompareIndex = 0
    attributeCompareIndex = 0
    #Makes file path objects based on the tables to compare
    for tableName, tabelSH in tableDict.items():
        filePathList.append(os.path.join(getCurrentDir(), tableName.lower()))
    #This is the temp file that will be used to display the results of the query
    tempFile = os.path.join(getCurrentDir(), 'tempFile' + '.csv')
    
    #This while loop isnt useful for this project, but it will allow for more that two tables to be compared
    while tableToCompareIndex < len(tableDict):
        mergeTables(filePathList[tableToCompareIndex], filePathList[tableToCompareIndex+1], attributeCompareIndex, attributeCompareList, tempFile)
        tableToCompareIndex += 2
        attributeCompareIndex += 1

    currentTable = 'tempFile'
    fullFileRead()
    os.remove(tempFile)
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




#---Helper Functions for Database and Table Manipulation---#
#This method creates a list of tables that will need to be compared to eachother, and will be looked at in pairs of two
def createSelectTableDict():
    thisDict = {}
    whereIndex = commandSplit.index('where')
    fromIndex = commandSplit.index('from')
    itemIndex = 0
    while itemIndex < len(commandSplit):
        if itemIndex > fromIndex and itemIndex < (whereIndex-indexFromWhere):
            thisDict[commandSplit[itemIndex].lower()] = commandSplit[itemIndex+1].lower()
            itemIndex += 2
        else:
            itemIndex += 1
    return thisDict
#Delete a row from a given table        
def deleteRow():
    #This is to record how many records are deleted
    changeCounter = 0
    attributeToFind = findColumn(commandSplit[4])
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    if attributeToFind == "Attribute not present":
        print("Unable to update record, attribute not present")
    else:
        #Open the original file to read
        with open(fullName,"r",encoding="UTF8") as source:
            reader = csv.reader(source)
            header = next(reader)
            tempFile = os.path.join(getCurrentDir(), 'tempFile.csv')
            with open(tempFile, 'w', encoding='UTF8',newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in reader:
                    #This if else statment is to determine what kind of operator is being used for the searching attribute
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
                    elif commandSplit[5] == '!=':
                        if row[attributeToFind] != commandSplit[6]:
                            changeCounter += 1
                        else:
                            writer.writerow(row)
                    elif commandSplit[5] == '<':
                        if float(row[attributeToFind]) < float(commandSplit[6]):
                            changeCounter += 1
                        else:
                            writer.writerow(row)
        #read out the temp file to the original file
        with open(tempFile, 'r', encoding='UTF8',newline='') as f:
            reader = csv.reader(f)
            with open(fullName,"w",encoding="UTF8") as destination:
                writer = csv.writer(destination)
                for row in reader:
                    writer.writerow(row)
        os.remove(tempFile)
        print("{} record(s) deleted".format(changeCounter))
#This just changes a row element at an index to the specified value
def modifyRow(row,attributeToUpdate):
    row[attributeToUpdate] = commandSplit[5]
    return row
#This searches the first row of a table to find the column with a matching attribute
def findColumn(attribute):
    fullName = os.path.join(getCurrentDir(), currentTable + '.csv')
    with open(fullName,"r",encoding="UTF8") as source:
        reader = csv.reader(source)
        header = next(reader)
        for col in header:
            if col.startswith(attribute):
                return header.index(col)
    return "Attribute not present"
#This function write the table to a temp table, with modified values, and then write that temp file back to the original file
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
#This function inserts a record into a table
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
    fullName = os.path.join(tempDir,currentTable.lower()+'.csv')
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
#This method will compile a list of all the tables currently in the working database
def compileTableList():
    global tableList
    tableList = []
    tempDir = getCurrentDir()
    #Walk the current directory (Database) and gather the names of all the files (Tables) 
    for (dirPath, dirNames, fileNames) in walk(tempDir):
        tableList.extend(fileNames)
#This will gather a list of current databases
def compileDatabaseList():
    global databaseList
    databaseList = []
    #Walk the current directory and gather the names of all the subdirectories 
    for (dirPath, dirNames, fileNames) in walk(currentDir):
        databaseList.extend(dirNames)

main()