from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree
import sqlite3
import apsw

def sql_sqlite(tree: DerivationTree) -> bool:
    sql_query = str(tree)
    try:
        conn = sqlite3.connect("test.db")  # pre-created db
        cur = conn.cursor()
        cur.execute(sql_query)  
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def sql_apsw(tree: DerivationTree) -> bool:
    sql_query = str(tree)
    try:
        conn = apsw.Connection("test.db")
        cur = conn.cursor()
        cur.execute(sql_query)
        conn.close()
        return True
    except Exception as e:
        return False
