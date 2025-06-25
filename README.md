# cse564
testing environment github repo

# SPEC
How to use: 
get_census_block.py:

from get_census_block import get_block_group_geoid
geoid = get_block_group_geoid(street, city, state)

How to use utils.py:
create_user: pass in: (username(string), name(string), email(string), password(string)) -- this will encrypt the password and create the user in the users table in walkdatadb
validate_user: pass in: (username(string), plain_password(string)) and this will return a boolean if its succesful or note and print the error if not
