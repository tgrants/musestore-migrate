"""

Nano-ORM in Python - generate SQL for basic CRUD statements
============================================================

Usage examples:
----------------
	>>> upsert("tbl", LogID=500, LoggedValue=5)
	"INSERT INTO tbl (LogID, LoggedValue) VALUES ('500', '5') ON DUPLICATE KEY UPDATE LogID = '500', LoggedValue = '5';"

	>>> read("tbl", **{"username": "morten"})
	"SELECT * FROM tbl WHERE username = 'morten';"

	>>> read("tbl", **{"user_type": 1, "user_group": "admin"})
	"SELECT * FROM tbl WHERE user_type = '1' AND user_group = 'admin';"

	>>> parameterized(insert("test", c1=None, c2="?"))
	"INSERT INTO test (c1, c2) VALUES (NULL, ?);"


Note: Don't pass user-controlled variables un-sanitized! Examples of malicious use:

	>>> read("tbl", **{"user_group": "random'; DROP TABLE tbl; --"})
	"SELECT * FROM tbl WHERE user_group = 'random'; DROP TABLE tbl; --';"

"""

def parameterized(qry):
	""" Remove quotes around '?' in 'qry', to enable parameterized queries """
	return qry.replace("'?'", "?")

def _make_repr(value):
	""" Hack to convert None to NULL instead of 'NULL' """
	return "NULL" if value is None else repr(value)


def create_table(table, **kwargs):
	""" Generates SQL for a CREATE TABLE statement, matching the columns passed as kwargs
		E.g. create_table("tbl_name", col1="integer primary key autoincrement", col2="text not null") """
	sql = list()
	sql.append("CREATE TABLE %s (" % table)
	sql.append(",\n".join(["\t%-12s\t%s" % (col_name, col_typ) for col_name, col_typ in kwargs.items()]))
	sql.append(");")
	return "\n".join(sql)


def read(table, **kwargs):
	""" Generates SQL for a SELECT statement matching the kwargs passed. """
	sql = list()
	sql.append("SELECT * FROM %s " % table)
	if kwargs:
		sql.append("WHERE " + " AND ".join("%s = %s" % (k, repr(v)) for k, v in kwargs.items()))
	sql.append(";")
	return "".join(sql)


def insert(table, **kwargs):
	""" insert rows into objects table given the key-value pairs in kwargs """
	keys = ["%s" % k for k in kwargs]
	values = [_make_repr(v) for v in kwargs.values()]
	sql = list()
	sql.append("INSERT INTO %s (" % table)
	sql.append(", ".join(keys))
	sql.append(") VALUES (")
	sql.append(", ".join(values))
	sql.append(");")
	return "".join(sql)


def upsert(table, **kwargs):
	""" update/insert rows into objects table (update if the row already exists)
		given the key-value pairs in kwargs """
	keys = ["%s" % k for k in kwargs]
	values = [_make_repr(v) for v in kwargs.values()]
	sql = list()
	sql.append("INSERT INTO %s (" % table)
	sql.append(", ".join(keys))
	sql.append(") VALUES (")
	sql.append(", ".join(values))
	sql.append(") ON DUPLICATE KEY UPDATE ")
	sql.append(", ".join("%s = %s" % (k, _make_repr(v)) for k, v in kwargs.items()))
	sql.append(";")
	return "".join(sql)


def delete(table, **kwargs):
	""" deletes rows from table where **kwargs match """
	sql = list()
	sql.append("DELETE FROM %s " % table)
	sql.append("WHERE " + " AND ".join("%s = %s" % (k, _make_repr(v)) for k, v in kwargs.items()))
	sql.append(";")
	return "".join(sql)
