import sqlite3


# -----------------------------------------------------------------------------------------------
def make_connection(db):
    conn = sqlite3.connect(f'{db}.db')
    # Create a cursor object
    cursor = conn.cursor()
    return conn, cursor
def return_condition_rule_from_str(column_str):
    condition_rule = ''
    list_key_splited = column_str.split('__')
    if 'contains' in list_key_splited:
        condition_rule = 'contains'
    elif 'operator' in list_key_splited:
        condition_rule = 'operator'
    return condition_rule,list_key_splited[0]
def create_query_by_colValue_relatedCol_condition(related_col='and',**col_vlues):
    list_col_val_str = []
    params = []
    for pre_process_column, value_or_values in col_vlues.items():
        condition_rule,column = return_condition_rule_from_str(pre_process_column)
        if condition_rule == 'contains':
            if isinstance(value_or_values, list):
                # iterable of value_or_values
                column_conditions = [f"{column} LIKE ?" for _ in value_or_values]
                list_col_val_str.append(f"({' OR '.join(column_conditions)})")
                params.extend([f"%{substring}%" for substring in value_or_values])
            elif isinstance(value_or_values, str):
                # Single substring
                list_col_val_str.append(f"{column} LIKE ?")
                params.append(f"%{value_or_values}%")
        elif condition_rule == 'operator':
            if isinstance(value_or_values, tuple) and len(value_or_values) == 2:
                # Comparison operator and float number
                operator, number = value_or_values
                if operator in ('<', '>', '<=', '>=', '='):
                    list_col_val_str.append(f"{column} {operator} ?")
                    params.append(number)

        else:
            if isinstance(value_or_values, (tuple, list)):
                placeholders = ','.join(['?' for _ in value_or_values])
                list_col_val_str.append(f"{column} IN ({placeholders})")
                params.extend(value_or_values)
            else:
                list_col_val_str.append(f"{column} = ?")
                params.append(value_or_values)
    where_clause = f" {related_col} ".join(list_col_val_str)
    return where_clause ,params

def get_tableName_and_columnsFromDBmaster(db):
    conn, cursor = make_connection(db)

    # Execute the query to find all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all results
    tables = cursor.fetchall()
    # Dictionary to store tables and their columns
    tables_columns = {}

    # Iterate through the tables and get their columns
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        tables_columns[table_name] = column_names
    # Close the connection
    conn.close()
    return tables_columns


def get_columnsNameFromTable(db, table_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    conn.close()
    return column_names


def check_table_exists(db, table_name):
    conn, cursor = make_connection(db)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    res = cursor.fetchone() is not None
    conn.close()
    return res


def update_ColNameType(db, table_name, old_colName, new_col_name, new_col_type):
    conn, cursor = make_connection(db)
    cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_colName} TO {new_col_name};")
    cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {new_col_name} {new_col_type};")
    conn.commit()
    conn.close()


def drop_table(db, tabel_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"DROP TABLE {tabel_name}")
    conn.commit()
    conn.close()


def tabel_maker4(tabel_name, db, *args, strick_flag=False):
    conn, cursor = make_connection(db)
    args_str = ""
    for i in args:
        args_str += i + ","
    args_str = args_str[:-1]

    if strick_flag == False:
        if args_str != "":
            cursor.execute(f'create table if not exists {tabel_name} (id_ integer primary key ,{args_str})')
        else:
            cursor.execute(f'create table if not exists {tabel_name} (id_ integer primary key)')
    else:
        if args_str != "":
            cursor.execute(f'create table {tabel_name} (id_ integer primary key ,{args_str})')
        else:
            cursor.execute(f'create table {tabel_name} (id_ integer primary key)')
    conn.commit()
    conn.close()


def insert4(tabel_name, db, *args, **kwargs):
    conn, cursor = make_connection(db)
    if args == ():
        columns = ','.join([col for col in kwargs.keys()])
        args = tuple(kwargs.values())
        ques = ','.join(['?' for _ in args])
        # print(f'insert into {tabel_name} ({columns}) values ({ques})', args)
        cursor.execute(f'insert into {tabel_name} ({columns}) values ({ques})', args)
    else:
        ques = ','.join(['?' for _ in args])
        cursor.execute(f'insert into {tabel_name} values (NULL,{ques})', args)
    last_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return last_id


def delete4(table_name, db,related_col='and', **col_vlues):
    if col_vlues == {}:
        conn, cursor = make_connection(db)
        cursor.execute(f"SELECT rowid FROM {table_name}")
        rows_id = cursor.fetchall()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        return [id_[0] for id_ in rows_id]
    queri , params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_vlues)
    conn, cursor = make_connection(db)
    # print(f"SELECT rowid FROM {table_name} WHERE {queri}",params)
    cursor.execute(f"SELECT rowid FROM {table_name} WHERE {queri}", params)
    rows_id = cursor.fetchall()

    if rows_id is []:
        # No matching row found, nothing to delete
        conn.close()
        return [id_[0] for id_ in rows_id]


    # Perform the deletion
    cursor.execute(f"DELETE FROM {table_name} WHERE {queri}", params)
    conn.commit()
    conn.close()
    return [id_[0] for id_ in rows_id]





def view4(table_name, db, sort_by=None,related_col='and',filter_kind='', **col_vlues):
    """
    Query a database table based on provided column-value pairs and additional conditions.

    Args:
        table_name (str): Name of the table to query.
        db (str): Database file.
        conditions (str, optional): Additional SQL conditions. Defaults to None.
        **col_val: Column-value pairs to filter the query.

    Returns:
        tuple: A tuple containing the query result and column names.
    """
    search_into_columns = 'WHERE '
    where_clause, params = create_query_by_colValue_relatedCol_condition(related_col=related_col,**col_vlues)
    search_into_columns += where_clause
    if search_into_columns == 'WHERE ':
        search_into_columns = ''

    if sort_by:
        search_into_columns += f" {sort_by}"


    sql_command = f'SELECT * FROM {table_name} {search_into_columns}'

    conn, cursor = make_connection(db)
    # print(sql_command)  # Debugging line to see the generated SQL command
    cursor.execute(sql_command, params)
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    conn.close()

    return result, columns



def search4(table_name, db,related_col='and', **col_vlues):
    where_clause, params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_vlues)
    conn, cursor = make_connection(db)
    # print(f'-- select * from {table_name} where {where_clause} ',tuple(params))
    cursor.execute(f'select * from {table_name} where {where_clause} ', tuple(params))
    columns = [description[0] for description in cursor.description]
    result = cursor.fetchall()
    conn.close()
    return result, columns

def update(db, table_name, condition_str, **kwargs):
    queri = ''
    for key, value in kwargs.items():
        if value == '':
            continue
        queri += key + ' = ?' + ', '
    queri = queri[:-2] + ' '
    listlOfValues = []
    for v in kwargs.values():
        if v == '':
            continue
        listlOfValues.append(v)
    tuple_of_values = tuple(listlOfValues)
    # Connect to the SQLite database
    conn, cursor = make_connection(db)
    # Define the SQL statement to add a new column
    query = f"UPDATE {table_name} SET {queri} WHERE {condition_str}"
    # Execute the SQL statement
    cursor.execute(query, tuple_of_values)
    # Commit the changes
    conn.commit()


def add_col(db, table_name, col_name, dType, id='id_'):
    conn, cursor = make_connection(db)
    column_names = get_columnsNameFromTable(db, table_name)
    result = check_col_exist_and_return_col_rows(db, table_name, col_name, column_names, id=id)
    if result:
        pass
    else:
        # Define the SQL statement to add a new column
        alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {dType}"
        # Execute the SQL statement
        cursor.execute(alter_query)
        # Commit the changes
        conn.commit()

    # Close the connection
    conn.close()


def check_col_exist_and_return_col_rows(db, table_name, col_name, column_names, id='id_'):
    if col_name in column_names:
        conn, cursor = make_connection(db)
        cursor.execute(f'SELECT {id}, {col_name} FROM {table_name}')
        data = cursor.fetchall()
        conn.close()
        return data
    else:
        return False


def drop_col(db, table_name, col_name):
    conn, cursor = make_connection(db)
    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")
    conn.commit()
    conn.close()
