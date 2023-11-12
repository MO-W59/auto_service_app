# auto_service_app

This app was originally designed to be a project to learn a combination of SQL, security, and gui consepts. As it progressed it grew in size quite unexpectedly. Certainly the app still is in need of improvements but I have learned so much from constructing it getting it to its current state. Long term todo items are listed below, but from now this project will be taking a back seat to other projects and studies.

--Description--

    GUI app that tracks repairs and other information to run an auto repair service.

    Uses SQLite3 and PyQt 6 to make a GUI that tracks repairs and other data such as customer, vehicles and employees in the database.

    Directory is currently hard coded to local data folder using SQLite (this has some inherent weaknesses -> see below long term items).


--Requirements--

    PyQt6

    SQLite3

    passlib

--Usage--

    1. To run the app go to your CLI in the script directory and type --> python app.py

    2. From there you will need to create a new user to reach the other pages.

    3. After user creation go login and you are free to explore the app.

    Note: Before a new repair can be made a vehicle must be input into the system and have an owner assigned to it first.


_-_-TODO list-_-_
    
--Bugs-- 

    Not currently tracking any bugs.

--Long Term--

    Add home page for users -> direct widget stack to new page after login

    Reimplement OOP style for objects rather than purely using the database? --> large rewrite/redesign

    Improve visuals of the UI

    Rather than using one stacked widgit would it be better to use multiple windows instead?

    SQLite documentation --> "locking mechanism might not work correctly if the database file is kept on an NFS filesystem." Thus if wanting multipe mahcines to access the database, a different database is recommended.



https://docs.python.org/3/library/sqlite3.html
https://doc.qt.io/qtforpython-6/api.html#basic-modules