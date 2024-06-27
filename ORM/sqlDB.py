import sqlite3


# def tabel_maker(tabel_name):
#     conn = sqlite3.connect('sample.db')
#     cur = conn.cursor()
#     cur.execute(
#         f'create table if not exists {tabel_name} (Receipt_num integer primary key not null ,Date_Recieved text,Time_Recieved text,Item_Description text, Repair_Type text, Max_Pick_Up_Date text, Customer_Name text, Customer_Phone text, Price_Estimate text)')
#     conn.commit()
#     conn.close()
#
#
# def insert(tabel_name, Date_Recieved='', Time_Recieved='', Item_Description='', Repair_Type='', Max_Pick_Up_Date='',
#            Customer_Name='', Customer_Phone='', Price_Estimate=''):
#     conn = sqlite3.connect('sample.db')
#     cur = conn.cursor()
#     cur.execute(f'insert into {tabel_name} values (null,?,?,?,?,?,?,?,?)', (
#     Date_Recieved, Time_Recieved, Item_Description, Repair_Type, Max_Pick_Up_Date, Customer_Name, Customer_Phone,
#     Price_Estimate))
#     conn.commit()
#     conn.close()
#
#
# def view(tabel_name):
#     conn = sqlite3.connect('sample.db')
#     cur = conn.cursor()
#     cur.execute(f'select * from {tabel_name}')
#     result = cur.fetchall()
#     conn.close()
#     return result
#
#
# def truncate(tabel_name):
#     conn = sqlite3.connect('sample.db')
#     cur = conn.cursor()
#     cur.execute(f'delete from {tabel_name}')
#     conn.commit()
#     conn.close()
#
#
# def delete(tabel_name, Receipt_num):
#     conn = sqlite3.connect('sample.db')
#     cur = conn.cursor()
#     cur.execute(f'delete from {tabel_name} where Receipt_num = ?', (Receipt_num,))
#     conn.commit()
#     conn.close()
#
#
# def tabel_maker2(tabel_name, *args):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'create table if not exists {tabel_name} (id integer primary key not null,seller text)')
#     conn.commit()
#     conn.close()
#
#
# def insert2(tabel_name, seller):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'insert into {tabel_name} values (null,?)', (seller,))
#     conn.commit()
#     conn.close()
#
#
# def delete2(tabel_name, id=None, seller=''):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'delete from {tabel_name} where seller = ? or id = ?', (seller, id))
#     conn.commit()
#     conn.close()
#
#
# def view2(tabel_name):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'select * from {tabel_name}')
#     result = cur.fetchall()
#     conn.close()
#     return result
#
#
# def search2(tabel_name, seller):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'select * from {tabel_name} where seller = ?', (seller,))
#     result = cur.fetchall()
#     conn.close()
#     return result
#
#
# def tabel_maker3(tabel_name, *args):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     args_str = ""
#     for i in args:
#         args_str += i + ","
#     args_str = args_str[:-1]
#     cur.execute(f'create table if not exists {tabel_name} (id_ integer primary key ,{args_str})')
#     conn.commit()
#     conn.close()
#
#
# def insert3(tabel_name, *args):
#     ques = ''
#     for i in args:
#         ques += "?,"
#     ques = ques.replace(ques, ques[:-1])
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'insert into {tabel_name} values (null,{ques})', args)
#     conn.commit()
#     conn.close()
#
#
# def delete3(tabel_name):
#     conn = sqlite3.connect('sample2.db')
#     cur = conn.cursor()
#     cur.execute(f'delete from {tabel_name}')
#     conn.commit()
#     conn.close()


# -----------------------------------------------------------------------------------------------
def make_connection(db):
    conn = sqlite3.connect(f'{db}.db')
    # Create a cursor object
    cursor = conn.cursor()
    return conn, cursor

def create_query_by_colValue_relatedCol_condition(related_col='and',**col_vlues):
    list_col_val_str = []
    params = []
    queri = ""
    for col, value in col_vlues.items():
        if isinstance(value, (tuple, list)):
            placeholders = ','.join(['?' for _ in value])
            list_col_val_str.append(f"{col} IN ({placeholders})")
            params.extend(value)
        else:
            list_col_val_str.append(f"{col} = ?")
            params.append(value)
    queri += f' {related_col} '.join(list_col_val_str)
    return queri ,params

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
        rows = cursor.fetchall()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        return rows
    queri , params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_vlues)
    conn, cursor = make_connection(db)
    cursor.execute(f"SELECT rowid FROM {table_name} WHERE {queri}", params)
    rows = cursor.fetchall()

    if rows is []:
        # No matching row found, nothing to delete
        conn.close()
        return None


    # Perform the deletion
    cursor.execute(f"DELETE FROM {table_name} WHERE {queri}", params)
    conn.commit()
    conn.close()
    return rows





def view4(table_name, db, sort_by=None, **col_val):
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
    list_col_val_str = []
    params = []
    for col, value in col_val.items():
        if value is not None:
            if isinstance(value, (tuple, list)):
                placeholders = ','.join(['?' for _ in value])
                list_col_val_str.append(f"{col} IN ({placeholders})")
                params.extend(value)
            else:
                list_col_val_str.append(f"{col} = ?")
                params.append(value)

    search_into_columns += ' AND '.join(list_col_val_str)

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



def search4(tabel_name, db,related_col='and', **col_vlues):
    queri, params = create_query_by_colValue_relatedCol_condition(related_col=related_col, **col_vlues)
    conn, cursor = make_connection(db)
    # print(f'select * from {tabel_name} where {queri} ',tuple(params))
    cursor.execute(f'select * from {tabel_name} where {queri} ', tuple(params))
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

# tabel_maker4('mytable','mydb','col1 integer', 'col2 varchar(60)')
# insert4('mytable','mydb',22,'ll')
# insert4('mytable','mydb',55,'tt')
# insert4('mytable','mydb',55,'dj')
# insert4('mytable','mydb',46,'dj')
# insert4('mytable','mydb',78,'dj')
# print(view4('mytable','mydb'))
# print(delete4('mytable','mydb'))

# drop_col('mydb','mytable','col2')

# rows , cols = view4('product','map_db')
# print('rows',rows)
# print('cols',cols)
# update('map_db','product','id_ = 1',title='shirt')
# tabel_maker4('tabel_test','dbTest')
# add_col('dbTest','tabel_test','newCol','integer')

# print(dec.items())
# print(search4('period','date_record' ,date_='>= 2023-12-06',name= '= Fatemeh'))
# print(search4('period','date_record',name='',time_='>= 11:56:07'))
# print(view4('period','date_record'))
# delete4('period','date_record',time_='11:56:07')
# print(view4('period','date_record'))
# tabel_maker2('seller')
# tabel_maker3('shoes','seller_name text','model_shoe text','quantity integer','price flaot', 'time text')
# tabel_maker('tabel1')
# insert('tabel1',6)
# insert('tabel1')
# insert('tabel1')
# update('tabel1',4)
# print(view2('shoes'))

# update('map_db', 'product', f'id_ = {15}', title= 'test16',price=11414)
#
# rows,columns = search4('product', 'map_db',category_id= 2)
# print(rows)
# print(columns)
