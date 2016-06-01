import sqlite3

with sqlite3.connect("email.db") as connection:
	c = connection.cursor()
	c.execute("CREATE TABLE emails (id INTEGER PRIMARY KEY, company_name char(100) NOT NULL, email char(100), url char(100) NOT NULL)")
	c.execute("INSERT INTO emails (company_name, email, url) VALUES ('Eyeview','sheldon@tetsteyeview.com', 'https://unify.tapad.com/dga/#/dataflows/325')")
	c.execute("INSERT INTO emails (company_name, email, url) VALUES ('Sojern','sheldon@testsojern.com', 'https://unify.tapad.com/dga/#/dataflows/45/metrics')")
	c.close()