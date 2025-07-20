# Walkability Data Application

This repository contains a Flask-based web application for managing walkability data, user authentication, and census block group lookups. The application allows users to register, log in, add cities with walkability scores, and perform census block group lookups based on street, city, and state information.

---

## Features

1. **User Authentication**:
   - Register new users with encrypted passwords.
   - Log in and maintain session-based authentication.
   - Logout functionality to clear user sessions.

2. **City Management**:
   - Add cities with walkability scores.
   - View walkable cities (feature coming soon).

3. **Census Block Group Lookup**:
   - Perform lookups for census block group information based on street, city, and state.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cse564.git
   cd cse564
   ```

2. Log into the virtual environment
cd /path/to/working/directory
venv/bin/activate
pip install -r requirements.txt

3. Set up the .env file: Create a .env file in the root directory and add the following environment variables:
DB_HOST=localhost
DB_USER=walkdbuser
DB_PASSWORD=your_database_password
DB_NAME=walkdatadb
SECRET_KEY=**insert some form of gibberish**

4. run the app
python web.py



# SPEC
How to use: 
get_census_block.py:

from get_census_block import get_block_group_geoid
geoid = get_block_group_geoid(street, city, state)

How to use utils.py:
create_user: pass in: (username(string), name(string), email(string), password(string)) -- this will encrypt the password and create the user in the users table in walkdatadb

validate_user: pass in: (username(string), plain_password(string)) and this will return a boolean if its succesful or note and print the error if not

# Setting up your walkdatadb 
Using these mysql commands to build the tables:
CREATE DATABASE IF NOT EXISTS walkdatadb;
USE walkdatadb;

CREATE TABLE WalkabilityIndex (
    STATEFP CHAR(2),
    COUNTYFP CHAR(3),
    TRACTCE CHAR(6),
    BLKGRPCE CHAR(1),
    intersection_density INT,
    transit_access INT,
    job_housing_mix INT,
    population_employment_density INT,
    NatWalkInd DECIMAL(5,2),
    census_block CHAR(12) NOT NULL,
    PRIMARY KEY (census_block)
);

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE searches (
    user_id INT NOT NULL,
    search_id INT NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    census_block VARCHAR(20),
    PRIMARY KEY (user_id, search_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE walkability_titles (
    id INT NOT NULL AUTO_INCREMENT,
    key_name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
);

And create a walkdbuser for it:
CREATE USER 'walkdbuser'@'localhost' IDENTIFIED BY '*Insert a password here*';
GRANT ALL PRIVILEGES ON walkdatadb.* TO 'walkdbuser'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

# import the .csv for walkability dataset.
-- make sure you're in the same directory as the WalkabilityIndex.csv data set, here are some steps from the lab

You may need to login into mysql as a root user and issue:
SET GLOBAL local_infile = true;
Before you could load data from a text file in console.
After you downloaded all the csv files from Canvas, please logout from MySQL console:
Mysql> exit
You are then brought back to command line. At the command line, please type:
mysql -u <your username> -p --local-infile walkdatadb

You will be asked to type in your password. Please replace <your username> with the actual user name in your
set up.
Then after login successfully inside the MySQL, load a csv file into a table as follows:

mysql> load data local infile <path to the csv file> into table <table name> fields
terminated by ',' lines terminated by '\n';

ex)

LOAD DATA LOCAL INFILE '/full/path/WalkabilityIndex.csv'
INTO TABLE WalkabilityIndex
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
  STATEFP,
  COUNTYFP,
  TRACTCE,
  BLKGRPCE,
  intersection_density,
  transit_access,
  job_housing_mix,
  population_employment_density,
  NatWalkInd,
  census_block
);