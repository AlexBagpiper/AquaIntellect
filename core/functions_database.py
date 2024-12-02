# -*- coding: utf-8 -*-

# IMPORT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *

from config.file_path import *
from core.functions import *


# LOAD UI MAIN
# ///////////////////////////////////////////////////////////////
from uis.windows.main_window.ui_main import *

# FUNCTIONS
class DatabaseFunctions():
    def __init__(self):
        super().__init__()

    # CREATE COMMON DATABASE
    # ///////////////////////////////////////////////////////////////
    def create_common_database():
        if not os.path.isfile(COMMON_DATABASE_PATH):
            shutil.copyfile(COMMON_DATABASE_TEMPLATE_PATH, COMMON_DATABASE_PATH)
            con = sqleet.connect(str(COMMON_DATABASE_PATH), key='basekey')
            con.change_key(Functions.get_hwid())
            con.close()


    def connect_database(database):
        try:
            if DATABASE_ENCRYPTION:
                con = sqleet.connect(str(database), key=Functions.get_hwid())
                con.row_factory = sqleet.Row
            else:
                con = sqlite3.connect(database)
                con.row_factory = sqlite3.Row
            cur = con.cursor()
        except:
            con = False
            cur = False
        return con, cur


    def close_database(con, cur):
        cur.close()
        con.close()


    # SELECT DATA FROM BASE
    # ///////////////////////////////////////////////////////////////
    def select_data(
        database,
        table,
        column=None,
        where=None,
        value=None,
        where_and=None,
        value_and=None,
        function=None
    ):
        con, cur = DatabaseFunctions.connect_database(database)
        if not con and not cur:
            return False, 'connect_database_error'
        if function == 'lower':
            con.create_function(function, 1, lambda x: x.lower())
        try:
            if column and where and value:
                cur.execute(f"SELECT {column} FROM {table} WHERE {where} = '{value}'")
                temp = [x for (x,) in cur.fetchall()]
                data = []
                for x in temp:
                    data.append({cur.description[0][0]: x})
            elif column and where and not value:
                return False, f"value None"
            elif column and not where and not value:
                cur.execute(f"SELECT {column} FROM {table}")
                temp = [x for (x,) in cur.fetchall()]
                data = []
                for x in temp:
                    data.append({cur.description[0][0]: x})
            elif not column and not where and not value:
                cur.execute(f"SELECT * FROM {table}")
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            elif not column and where and value and not where_and and not value_and and not function:
                cur.execute(f"SELECT * FROM {table} WHERE {where} = '{value}'")
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            elif not where_and and not value_and and function == 'lower':
                if value:
                    query = "SELECT * FROM "+ table + " WHERE lower(" + column +") LIKE '" + value.lower() + "%'"
                    cur.execute(query)
                else:
                    cur.execute(f"SELECT * FROM {table}")
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            elif where_and and value_and and function == 'lower':
                if value:
                    query = "SELECT * FROM "+ table + " WHERE lower(" + column +") LIKE '" + value.lower() + "%' AND "+ where_and +" = '"+ value_and +"'"
                    cur.execute(query)
                else:
                    cur.execute(f"SELECT * FROM {table}")
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            elif where_and and value_and and function == 'date_search':
                query = "SELECT * FROM "+ table + " WHERE " + column +" LIKE '" + value + "%' AND "+ where_and +" = '"+ value_and +"'"
                cur.execute(query)
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            elif not column and where and value and where_and and value_and and not function:
                query = f"SELECT * FROM {table} WHERE {where} = '{value}' AND {where_and} = '{value_and}'"
                cur.execute(query)
                data = []
                for x in cur.fetchall():
                    data.append({cur.description[idx][0]: x[idx] for idx in range(len(x))})
            con.commit()
            DatabaseFunctions.close_database(con, cur)
        except Exception as e:
            return False, f"select_data_error {e}"

        return True, data


    # DELETE DATA FROM BASE
    # ///////////////////////////////////////////////////////////////
    def delete_data(
        database,
        table,
        where=None,
        value=None
    ):
        con, cur = DatabaseFunctions.connect_database(database)
        if not con and not cur:
            return False, 'connect_database_error'
        try:
            data = []
            if where and value:
                cur.execute(f"SELECT * FROM {table} WHERE {where} = '{value}'")
                for x in cur.fetchall():
                    data.append([y for y in x])
                cur.execute(f"DELETE FROM {table} WHERE {where} = '{value}'")
            elif not where and not value:
                cur.execute(f"SELECT * FROM {table}")
                for x in cur.fetchall():
                    data.append([y for y in x])
                cur.execute(f"DELETE FROM {table}")
            con.commit()
            DatabaseFunctions.close_database(con, cur)
            return True, data
        except Exception as e:
            return False, f"delete_data_error {e}"

    # INSERT DATA TO BASE
    # ///////////////////////////////////////////////////////////////
    def insert_data(
        database,
        table,
        column_list=None,
        value_list=None
    ):
        con, cur = DatabaseFunctions.connect_database(database)
        if not con and not cur:
            return False, 'connect_database_error'
        try:
            value_list = [f"'{x}'" for x in value_list]
            if column_list and len(column_list) == len(value_list):
                cur.execute(f"INSERT INTO {table} ({','.join(column_list)}) VALUES ({','.join(value_list)})")
            elif not column_list and value_list:
                cur.execute(f"INSERT INTO {table} VALUES ({','.join(value_list)})")
            con.commit()
            DatabaseFunctions.close_database(con, cur)
            return True
        except Exception as e:
            return False, f"insert_data_error {e}"


    # UPDATE DATA TO BASE
    # ///////////////////////////////////////////////////////////////
    def update_data(
        database,
        table,
        column_list,
        value_list,
        where_column,
        where_value
    ):
        con, cur = DatabaseFunctions.connect_database(database)
        if not con and not cur:
            return False, 'connect_database_error'
        if len(column_list) != len(value_list):
            return False, 'not_equal_database_error'
        try:
            set_list = [f"{column_list[i]} = '{value_list[i]}'" for i in range(len(column_list))]
            cur.execute(f"UPDATE {table} SET {','.join(set_list)} WHERE {where_column} = '{where_value}'")
            con.commit()
            DatabaseFunctions.close_database(con, cur)
            return True
        except Exception as e:
            return False, f"update_data_error {e}"

