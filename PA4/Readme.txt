This project is intended to be a bare bones version of a DBMS that can create and delete databases(and their associated tables), create and delete tables (that will be in a subdirectory under the database), and query and update the tables. 
The databases will be organized as directories in the same file directory that the program resides in. The tables will be implemented as CSV files, storing the data in an array like format inside the directories that the user creates. Other than being an industry standard, the CSV format will help to keep the tables neat and easy to access. To create a table, you must first be in an existing database. Files must have unique names inside each database, there can be duplicate file names if they are in separate database.
To implement this DBMS, I parsed out the user input, making patterns in the command structure. There is a level of error checking that is associated with determining which command is being given. Then I pass the parsed commands into a filter/menu function that completes the tasks that the user gave. This command line structure is run on a loop that more or less resets every iteration until it receives an exit command, to which it promptly ends the program. I use os libraries to handle creating the file and directories and a parallel shutil library to destroy the directories.
For file reading, I use a CSV reader and writer, that I have to specify how the reading and writing is done
I use many global variables to help keep track of what database, file, and command is being worked with. 

PA3 Design Document Questions:
Joins are implemented by taking in the statement and optimizing it to be understood by the programming. It then checks the join conditions (left, right, inner, and outer) and writes the corresponding rows to a temp file for display


**--EXECUTION AND COMPILE INSTRUCTIONS:--**
Open the file location such that you see a directory filled with "mdorado_pa3.py" and "PA3_test.sql" in your terminal or command prompt

Make sure the test script labeled “PA3_test.sql” is in the same dir as the python file

type "python mdorado_pa3.py" and press enter, this will run the test file and give the correct output.

