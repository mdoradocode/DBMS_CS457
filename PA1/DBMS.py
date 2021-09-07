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