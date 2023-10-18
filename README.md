# auto_service_app

APP STILL UNDER CONSTRUCTION WITH A LONG TODO LIST

GUI app that tracks repairs and other information to run an auto repair service

Uses SQLite3 and PyQt 6 to make a GUI that tracks repairs and other data such as customer, vehicles and employees in the database.

Directory is currently hard coded to local data folder.




vvv----- TODO list -----vvv

clear login boxes after login --> other pages too where applicable

uncheck checkboxes after submit

go to edit page after new submit for all items

move all functions to their proper module, move string construction the app module not in gui or DB

reduce lines in modules look at validte.py for example, is_valid = False --> return is_valid...just return False or True

search for cut off diplay labels ---> extend width in gui

list of parts text browser not in same location on gui as other list pages

merge technicians and servicewriters? add column to display area of work and just have employees table?

set restrictions on class set methods?

protect against SQL race condition, options -> thread lock? queue? connection pool?

consolidate code as much as possible --> edit customer submit make a update customer edit page function

search for bugs

update doc strings to describe things better

change naming conventions to uniform naming conventions

place comments where needed because you didnt do it at time of writing, also spell check stuff

handle too many lines in module linter flags


https://docs.python.org/3/library/sqlite3.html
https://doc.qt.io/qtforpython-5/api.html#basic-modules