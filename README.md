# auto_service_app

APP STILL UNDER CONSTRUCTION WITH A LONG TODO LIST

GUI app that tracks repairs and other information to run an auto repair service

Uses SQLite3 and PyQt 6 to make a GUI that tracks repairs and other data such as customer, vehicles and employees in the database.

Directory is currently hard coded to local data folder.




vvv----- TODO list -----vvv

new user/remove user functions refactor

edit/go to edit repair functions refactor

add remove functions for all objects

reduce lines in modules look at validte.py for example, is_valid = False --> return is_valid...just return False or True

search for cut off diplay labels ---> extend width in gui

list of parts text browser not in same location on gui as other list pages

protect against SQL race condition, options -> thread lock? queue? connection pool?

search for bugs

update doc strings to describe things better

change naming conventions to uniform naming conventions

place comments where needed because you didnt do it at time of writing, also spell check stuff



https://docs.python.org/3/library/sqlite3.html
https://doc.qt.io/qtforpython-5/api.html#basic-modules