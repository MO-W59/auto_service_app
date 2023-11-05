# auto_service_app

This app was originally designed to be a combination of a SQL, security, and gui project to learn from and add to my portfolio. As it progressed it grew in size quite unexpectedly. Certainly the app still is in need of improvements but I have learned so much from constructing it getting it to its current state. Long term todo items are listed below, but from now this project will be taking a back seat to other projects and studies.

--Description--

GUI app that tracks repairs and other information to run an auto repair service

Uses SQLite3 and PyQt 6 to make a GUI that tracks repairs and other data such as customer, vehicles and employees in the database.

Directory is currently hard coded to local data folder using SQLite (this has some inherent weaknesses -> see below long term items).




vvv----- TODO list -----vvv

-- Bugs -- 

User can force invalid lane or section by inputing value in opposite input and checking the related boxes/radio button

User can avoid lane or section input by using opposite radio button and inputing an invalid value

---Long Term---

reimplement OOP style for objects? --> large rewrite/redesign

Improve visuals of the UI

Rather than using one stacked widgit would it be better to use multiple windows instead?

SQLite documentation --> "locking mechanism might not work correctly if the database file is kept on an NFS filesystem." thus if wanting multipe mahcines to access the database a different database is recommended.



https://docs.python.org/3/library/sqlite3.html
https://doc.qt.io/qtforpython-5/api.html#basic-modules