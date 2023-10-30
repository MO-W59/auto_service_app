# auto_service_app

APP STILL UNDER CONSTRUCTION WITH A LONG TODO LIST

GUI app that tracks repairs and other information to run an auto repair service

Uses SQLite3 and PyQt 6 to make a GUI that tracks repairs and other data such as customer, vehicles and employees in the database.

Directory is currently hard coded to local data folder.




vvv----- TODO list -----vvv

In depth review --> shortening, docstrings, comments, bug hunt

---Long Term---

reimplement OOP style for objects? --> large rewrite/redesign

Improve visuals of the UI

SQLite documentation --> "locking mechanism might not work correctly if the database file is kept on an NFS filesystem." thus if wanting multipe mahcines to access the database a different database is recommended.



https://docs.python.org/3/library/sqlite3.html
https://doc.qt.io/qtforpython-5/api.html#basic-modules