This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. 
The databases will be organized as directories in the same file directory that the program resides in. The tables will be implemented as CSV files, storing the data in an array like format inside the directories that the user creates. Other than being an industry standard, the CSV format will help to keep the tables neat and easy to access. To create a table, you must first be in an existing database. Files must have unique names inside each database, there can be duplicate file names if they are in separate database.
To implement this DBMS, I parsed out the user input, making patterns in the command structure. There is a level of error checking that is associated with determining which command is being given. Then I pass the parsed commands into a filter/menu function that completes the tasks that the user gave. This command line structure is run on a loop that more or less resets every iteration until it receives an exit command, to which it promptly ends the program. I use os libraries to handle creating the file and directories and a parallel shutil library to destroy the directories.
For file reading, I use a CSV reader and writer, that I have to specify how the reading and writing is done
I use many global variables to help keep track of what database, file, and command is being worked with. 

PA2 Design Document Questions:
Tuples are stored, separated by commas, in rows within a csv file. The header or attributes will always be the first row in the file. Every row below that represents a tuple in the order in which they are inserted.

The implementations of the following methods for this project are defined as such:
INSERT: This takes a tuple in, as a list of arguments from the user and then appends them to the end of the table that is selected
MODIFY: This takes in a table to look at, an attribute to search for, and an attribute to replace once the previous one is found. It writes all of the tuples to a new temp file, modifying tuples that match the search criteria, and then it creates a new version of the original file and writes the new data there.
DELETE: This takes in a table to look at, an attribute to search for. It writes all the non matching attributes and writes them to a temp file and then writes the temp file back to the original problem
SELECT: This does a special version of the rest of the code. It takes in arguments until it reaches 'from'. It then calculates the table and the type of arguments as well as the parameters using the relative position of 'from'

**--EXECUTION AND COMPILE INSTRUCTIONS:--**
Open the file location such that you see a directory filled with "mdorado_pa2.py" and "PA2_test.sql" in your terminal or command prompt

Make sure the test script labeled “PA2_test.sql” is in the same dir as the python file

type "python mdorado_pa2.py" and press enter, this will run the test file and give the correct output.

