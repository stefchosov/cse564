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
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
SECRET_KEY=your_secret_key

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
