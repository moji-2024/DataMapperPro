from orm_db import sqlDB

ignor_tuple = ('dict_col_obj', 'class_name', '_unchangeable_id', 'objects')


def _get_cells_from_notDBtable(rows: list[tuple], columns: list[str], target_col: str):
    list_cells = []
    target_index = 0
    for index, col in enumerate(columns):
        if col == target_col:
            target_index = index
            break
    for row in rows:
        list_cells.append(row[target_index])
    return list_cells


def _check_truthnessOfvlaues_of_args_and_kwargs(dict_col_obj: dict, *args, **kwargs):
    newkwargs = {}
    tuple_of_rules_obj = tuple(dict_col_obj.values())
    tuple_of_keies = tuple(dict_col_obj.keys())
    if args != ():
        for index, arg in enumerate(args):
            if tuple_of_rules_obj[index].class_name == 'ForeignKey' or tuple_of_rules_obj[
                index].class_name == 'OneToOneField':
                newkwargs[tuple_of_keies[index] + '_id'] = tuple_of_rules_obj[index]._apply_rule(arg)
            elif tuple_of_rules_obj[index].class_name == 'ManyToManyField':
                pass
            else:
                newkwargs[tuple_of_keies[index]] = tuple_of_rules_obj[index]._apply_rule(arg)
    else:
        for key, value in kwargs.items():
            if dict_col_obj[key].class_name == 'ForeignKey' or dict_col_obj[key].class_name == 'OneToOneField':
                newkwargs[key + '_id'] = dict_col_obj[key]._apply_rule(value)
            elif dict_col_obj[key].class_name == 'ManyToManyField':
                pass
            else:
                newkwargs[key] = dict_col_obj[key]._apply_rule(value)
    return newkwargs


def _create_dict_relationName_by_dict_childClassName_dictAttrObjs(_dict_childClassName_dictAttrObjs: dict):
    # print('_dict_childClassName_dictAttrObjs:::',_dict_childClassName_dictAttrObjs)
    _dict_relationTables = {}
    _dict_product_set = {}
    for class_instance, attr_cls_obj in _dict_childClassName_dictAttrObjs.items():
        for attr, cls_obj in attr_cls_obj.items():
            if cls_obj.class_name == 'ForeignKey' or cls_obj.class_name == 'ManyToManyField' or cls_obj.class_name == 'OneToOneField':
                _dict_relationTables.setdefault(cls_obj.to.__name__, (class_instance, attr, cls_obj))
                _dict_product_set.setdefault(class_instance, _dict_childClassName_dictAttrObjs[class_instance])

    return _dict_relationTables, _dict_product_set


def _create_dict_del_relation_between_tables(_dict_childClassName_dictAttrObjs: dict):
    dict_delete_orderd = {}
    for class_instance, attr_cls_obj in _dict_childClassName_dictAttrObjs.items():
        dict_delete_orderd.setdefault(class_instance, [])
        for attr, cls_obj in attr_cls_obj.items():
            if cls_obj.class_name == 'ForeignKey':
                dict_delete_orderd[cls_obj.to.__name__].append((class_instance, attr + '_id', 'keep_id'))
                for attr_, cls_obj_ in attr_cls_obj.items():
                    if cls_obj_.class_name == 'ManyToManyField':
                        dict_delete_orderd[cls_obj.to.__name__].append(
                            (class_instance + '_' + cls_obj_.to.__name__, class_instance + '_id', 'pass'))
                    elif cls_obj_.class_name == 'OneToOneField':
                        dict_delete_orderd[cls_obj.to.__name__].append(
                            (cls_obj_.to.__name__, class_instance + '_id', 'pass'))
            elif cls_obj.class_name == 'ManyToManyField':
                dict_delete_orderd[class_instance].append(
                    (class_instance + '_' + cls_obj.to.__name__, class_instance + '_id', 'pass'))
                dict_delete_orderd[cls_obj.to.__name__].append(
                    (class_instance + '_' + cls_obj.to.__name__, cls_obj.to.__name__ + '_id', 'pass'))
            elif cls_obj.class_name == 'OneToOneField':
                dict_delete_orderd[class_instance].append((cls_obj.to.__name__, class_instance + '_id', 'pass'))
                dict_delete_orderd[cls_obj.to.__name__].append((class_instance, attr + '_id', 'keep_id'))
                for attr_, cls_obj_ in attr_cls_obj.items():
                    if cls_obj_.class_name == 'ManyToManyField':
                        dict_delete_orderd[cls_obj.to.__name__].append(
                            (class_instance + '_' + cls_obj_.to.__name__, class_instance + '_id', 'pass'))
    return dict_delete_orderd


class objects:
    def __init__(self, class_name: str, dict_attr: dict, **kwargs):
        self.class_name = class_name
        self.dict_attr = dict_attr
        self.kwargs = kwargs

    def all(self):
        return db_class(self.class_name, self.dict_attr, **self.kwargs)

    def filter(self, **kwargs):
        query = dict()
        query.update(**self.kwargs)
        for key, value in kwargs.items():
            list_key_splited = key.split('__')
            if self.dict_attr[list_key_splited[0]].class_name == 'ForeignKey':
                column = '__'.join(list_key_splited[1:])
                rows, columns = sqlDB.search4(self.dict_attr[list_key_splited[0]].to.__name__, 'map_db',
                                              **{column: value})
                try:
                    query[list_key_splited[0] + '_id'] = rows[0][0]
                except:
                    query[list_key_splited[0] + '_id'] = []
            elif self.dict_attr[list_key_splited[0]].class_name == 'ManyToManyField':
                column = '__'.join(list_key_splited[1:])
                query = self._get_rootTable_id_from_col_of_class_match_to_ManyToManyField(
                    self.dict_attr[list_key_splited[0]].to.__name__, {column: value},
                    self.class_name + '_' + self.dict_attr[list_key_splited[0]].to.__name__, self.class_name
                )
            else:
                query[key] = value
        if query == {}:
            return []
        return db_class(self.class_name, self.dict_attr, **{**self.kwargs, **query})

    def get(self, **kwargs):
        query = dict()
        query.update(**self.kwargs)
        for key, value in kwargs.items():
            list_key_splited = key.split('__')
            if self.dict_attr[list_key_splited[0]].class_name == 'ForeignKey':
                column = '__'.join(list_key_splited[1:])
                rows, columns = sqlDB.search4(self.dict_attr[list_key_splited[0]].to.__name__, 'map_db',
                                              **{column: value})
                query[list_key_splited[0] + '_id'] = rows[0][0]
            elif self.dict_attr[list_key_splited[0]].class_name == 'ManyToManyField':
                column = '__'.join(list_key_splited[1:])
                query = self._get_rootTable_id_from_col_of_class_match_to_ManyToManyField(
                    self.dict_attr[list_key_splited[0]].to.__name__, {column: value},
                    self.class_name + '_' + self.dict_attr[list_key_splited[0]].to.__name__, self.class_name
                )
            else:
                query[key] = value
        if query == {}:
            return []
        rows, columns = sqlDB.search4(self.class_name, 'map_db', **query)
        return self._append_obj_to_objList(rows, columns)[0]

    def create(self, *args, **kwargs):
        dict_col_obj = self._return_dict_attr_objValue()
        newkwargs = _check_truthnessOfvlaues_of_args_and_kwargs(dict_col_obj, *args, **kwargs)
        last_id = sqlDB.insert4(self.class_name, 'map_db', *args, **newkwargs)
        rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=f'ORDER BY id_ DESC LIMIT 1')
        self._unchangeable_id = last_id
        self._create_connection_to_OneToOneField(dict_col_obj, last_id, *args, **kwargs)
        created_obj_without_impeliment_manyToMany_objs = self._append_obj_to_objList(rows, columns)[0]
        if kwargs != {}:
            for attr, value in dict_col_obj.items():
                if value.class_name == 'ManyToManyField':
                    try:
                        self._add_data_to_intermediate_table_and_refine_obj(attr,
                                                                            created_obj_without_impeliment_manyToMany_objs,
                                                                            kwargs[attr])
                    except:
                        break
        return created_obj_without_impeliment_manyToMany_objs

    def _get_rootTable_id_from_col_of_class_match_to_ManyToManyField(self, to_table_name, to_dict_kwargs,
                                                                     intermediate_table_name,
                                                                     root_table_name):
        query = {}
        rows, columns = sqlDB.search4(to_table_name, 'map_db', **to_dict_kwargs)
        list_toTable_id = _get_cells_from_notDBtable(rows, columns, 'id_')
        if list_toTable_id != []:
            rows, columns = sqlDB.search4(intermediate_table_name, 'map_db', **{to_table_name + '_id': list_toTable_id})
            list_rootTable_related_id = _get_cells_from_notDBtable(rows, columns, root_table_name + '_id')
            if list_rootTable_related_id != []:
                query['id_'] = list_rootTable_related_id
        return query

    def _add_data_to_intermediate_table_and_refine_obj(self, key_to_return_manyToMany_obj: str, root_obj,
                                                       obj_of_class_which_ManyToMany_obj_mentioned: list):
        manyToMany_obj = getattr(root_obj, key_to_return_manyToMany_obj)
        manyToMany_obj.add(*obj_of_class_which_ManyToMany_obj_mentioned)

    def _create_connection_to_OneToOneField(self, dict_col_obj: dict, last_id: list[int], *args, **kwargs):
        if args == ():
            for attr, obj in dict_col_obj.items():
                if obj.class_name == 'OneToOneField':
                    sqlDB.update('map_db', obj.to.__name__, f'id_ = {kwargs[attr]._unchangeable_id}',
                                 **{self.class_name + '_id': last_id, })
        else:
            for obj in args:
                try:
                    if obj.class_name == 'OneToOneField':
                        sqlDB.update('map_db', obj.to.__name__, f'id_ = {obj._unchangeable_id}',
                                     **{self.class_name + '_id': last_id, })
                except:
                    pass

    def _append_obj_to_objList(self, rows: list[tuple], columns: list[str]):
        local_list = []
        for row in rows:
            dict_col_obj = self._return_dict_attr_objValue()
            local_list.append(raw_Class(row, columns, self.class_name, dict_col_obj))
        return local_list

    def _return_dict_attr_objValue(self):
        return {k: v for k, v in self.dict_attr.items() if not k.startswith('__')}


class db_class(objects):
    def __init__(self, class_name: str, dict_attr: dict = None, conditions: str = '', **kwargs):
        self.conditions = conditions
        self.class_name = class_name
        self.obj_list = []
        self.dict_attr = dict_attr
        self.kwargs = kwargs

    def order_by(self, order_str: str):
        if order_str[0] == '-':
            self.conditions += f'ORDER BY {order_str} DESC '
        else:
            self.conditions += f'ORDER BY {order_str} '
        return db_class(self.class_name, self.dict_attr, conditions=self.conditions, **self.kwargs)

    def __repr__(self):
        rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=self.conditions, **self.kwargs)
        return repr(self._append_obj_to_objList(rows, columns))

    def __getitem__(self, index: slice | int):
        if isinstance(index, slice):
            offset = index.start
            end = index.stop
            if offset == None:
                offset = 0
            if end == None:
                rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                            sort_by=self.conditions + f'limit {-1} offset {offset}', **self.kwargs)
                return self._append_obj_to_objList(rows, columns)
            limit = end - offset
            rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                        sort_by=self.conditions + f'limit {limit} offset {offset}', **self.kwargs)
            return self._append_obj_to_objList(rows, columns)
        elif isinstance(index, int):
            if index < 0:
                rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                            sort_by=self.conditions + f'ORDER BY id_ DESC LIMIT 1 OFFSET {abs(index) - 1}',
                                            **self.kwargs)
            elif index == -1:
                rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=f'ORDER BY id_ DESC LIMIT 1',
                                            **self.kwargs)
            else:
                rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                            sort_by=self.conditions + f'limit {1} offset {index}', **self.kwargs)
            return self._append_obj_to_objList(rows, columns)[0]


class model:
    _dict_relationTables = {}
    _dict_childClassName_dictAttrObjs = {}

    def __init_subclass__(cls, **kwargs):
        # super().__init_subclass__(**kwargs)
        model._dict_childClassName_dictAttrObjs[cls.__name__] = {k: v for k, v in cls.__dict__.items() if
                                                                 not k.startswith('__')}

    def __init__(self, *args, **instance_kwargs):
        self.class_name = self.__class__.__name__
        dict_childClass_attrs_values = {k: v for k, v in self.__class__.__dict__.items() if not k.endswith('__')}
        self.objects = objects(self.class_name, dict_childClass_attrs_values)
        for attr, obj in dict_childClass_attrs_values.items():
            obj.root_className = self.class_name
            obj.root_attr = attr
        if args == ():
            for key, value in instance_kwargs.items():
                if key in dict_childClass_attrs_values.keys():
                    setattr(self, key, value)
                else:
                    raise 'argument error'
        self._unchangeable_id = None

    def save(self):
        query = dict()
        attributes = self.__dict__
        dict_childClass_attrs_classObj = {k: v for k, v in self.__class__.__dict__.items() if not k.startswith('__')}
        for attr, object_ in dict_childClass_attrs_classObj.items():
            if attr in attributes:
                query[attr] = attributes[attr]
        saved_obj = self.objects.create(**query)
        self._unchangeable_id = saved_obj._unchangeable_id
        return saved_obj

    def get_child_class_name(self):
        return self.__class__.__name__

    def __repr__(self):
        dictforstr = {k: v for k, v in self.__dict__.items() if k not in ignor_tuple}
        return 'class model :' + str(dictforstr)


class raw_Class:
    def __init__(self, rows: list[tuple], columns: list[str], class_name: str, dict_col_obj: dict):
        self.dict_col_obj = dict_col_obj
        self.class_name = class_name
        _dict_relationTables, dict_product_set = _create_dict_relationName_by_dict_childClassName_dictAttrObjs(
            model._dict_childClassName_dictAttrObjs)
        self._create_attr_by_row_column(rows, columns)
        self._create_setAttr_by_dict_relationTabels(class_name, _dict_relationTables, dict_product_set)
        self._create_Attr_to__toClass___by_dict_col_obj_(dict_col_obj, class_name)

    def _create_attr_by_row_column(self, rows: list[tuple], columns: list[str]):
        for i in range(len(columns)):
            if i == 0:
                setattr(self, '_unchangeable_id', rows[i])
            else:
                setattr(self, columns[i], rows[i])

    def _create_setAttr_by_dict_relationTabels(self, class_name: str, _dict_relationTables: dict,
                                               dict_product_set: dict):
        if class_name in _dict_relationTables.keys():
            name_target_key = _dict_relationTables[class_name][0]
            set_dict_to_setattr = {}
            if _dict_relationTables[class_name][2].class_name == 'ForeignKey':
                set_dict_to_setattr[_dict_relationTables[class_name][1] + '_id'] = self._unchangeable_id
                setattr(self, name_target_key + '_set',
                        objects(name_target_key, dict_product_set[name_target_key], **set_dict_to_setattr))
            elif _dict_relationTables[class_name][2].class_name == 'ManyToManyField':
                ManyToManyField_related_table_name = name_target_key + '_' + self.class_name
                rows, columns = sqlDB.search4(ManyToManyField_related_table_name, 'map_db', related_col='Or',
                                              **{self.class_name + '_id': self._unchangeable_id})
                list_cells = _get_cells_from_notDBtable(rows, columns, name_target_key + '_id')
                if list_cells != []:
                    set_dict_to_setattr['id_'] = list_cells

                setattr(self, name_target_key + '_set',
                        objects(name_target_key, dict_product_set[name_target_key], **set_dict_to_setattr))
            elif _dict_relationTables[class_name][2].class_name == 'OneToOneField':
                set_dict_to_setattr = {}
                set_dict_to_setattr[_dict_relationTables[class_name][1] + '_id'] = self._unchangeable_id
                setattr(self, name_target_key + '_match',
                        objects(name_target_key, dict_product_set[name_target_key], **set_dict_to_setattr))

    def _create_Attr_to__toClass___by_dict_col_obj_(self, dict_col_obj: dict, class_name: str):
        for attr, obj in dict_col_obj.items():
            if obj.__class__.__name__ == 'ForeignKey' or obj.__class__.__name__ == 'OneToOneField':
                obj.root_className = class_name
                obj._root_id = self._unchangeable_id
                obj.root_attr = attr
                obj._related_obj_id = getattr(self, attr + '_id')
                setattr(self, attr, obj)

            elif obj.__class__.__name__ == 'ManyToManyField':
                obj.root_className = class_name
                obj._root_id = self._unchangeable_id
                obj.root_attr = attr
                setattr(self, attr, obj)
            else:
                pass

    def delete(self):
        dict_delete_orderd = _create_dict_del_relation_between_tables(model._dict_childClassName_dictAttrObjs)
        del_rowID_root_table = sqlDB.delete4(self.class_name, 'map_db', id_=self._unchangeable_id)
        for table_delCol in dict_delete_orderd[self.class_name]:
            table = table_delCol[0]
            del_col = table_delCol[1]
            if table_delCol[2] == 'keep_id':
                del_rowID_root_table = sqlDB.delete4(table, 'map_db', **{del_col: del_rowID_root_table})
            else:
                sqlDB.delete4(table, 'map_db', **{del_col: del_rowID_root_table})

    def save(self):
        attributes = self.__dict__
        query = dict()
        for key in self.dict_col_obj:
            if attributes[key].__class__.__name__ == 'ForeignKey' or attributes[
                key].__class__.__name__ == 'ManyToManyField' or attributes[key].__class__.__name__ == 'OneToOneField':
                continue
            query[key] = attributes[key]
        newkwargs = _check_truthnessOfvlaues_of_args_and_kwargs(self.dict_col_obj, **query)
        sqlDB.update('map_db', self.class_name, f'id_ = {self._unchangeable_id}', **newkwargs)

    def __repr__(self):
        dictforstr = {k: v for k, v in self.__dict__.items() if k not in ignor_tuple}
        return 'class raw_Class :' + str(dictforstr)


class DecimalField:
    class_name = 'DecimalField'
    dtype = 'REAL'
    _unchangeable_id = None
    root_className = None
    root_attr = None

    def __init__(self, max_digits: int = 8, decimal_places: int = 2):
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def _apply_rule(self, value):
        try:
            value + 1
            str_value = str(value)
            parts = str_value.split('.')
            if len(parts) == 1:
                if len(str_value) > self.max_digits:
                    raise 'max_digits length error'
                else:
                    return value
            if len(str_value) > self.max_digits:
                raise 'max_digits length error'
            else:
                if len(parts[1]) > 2:
                    raise 'DecimalField decimal_places error'
                else:
                    return value

        except:
            raise 'DecimalField float error'


class CharField:
    class_name = 'CharField'
    dtype = 'VARCHAR'
    _unchangeable_id = None
    root_className = None
    root_attr = None

    def __init__(self, max_length=300):
        self.max_length = max_length

    def _apply_rule(self, value):
        try:
            if len(value) > self.max_length:
                raise 'DecimalField error'
        except:
            raise 'DecimalField error'
        return value


def CASCADE():
    pass


class ForeignKey:
    class_name = 'ForeignKey'
    dtype = 'INTEGER'
    _related_obj_id = None
    _root_id = None
    root_className = None
    root_attr = None

    def __init__(self, to, on_delete=CASCADE, null=True):
        self.to = to
        self.on_delete = on_delete
        self.null = null
        self.dict__to__Class_attrs_values = {k: v for k, v in to.__dict__.items() if not k.endswith('__')}

    def _apply_rule(self, value):
        dict_attributes_value = value.__dict__
        for attr in dict_attributes_value:
            if attr == 'id_':
                return value.id_
            elif attr == '_unchangeable_id':
                return value._unchangeable_id
        raise 'error'

    def update(self, obj=None, **kwargs):
        if (obj != None) and (kwargs == {}):
            sqlDB.update('map_db', self.root_className, f'id_ = {self._root_id}',
                         **{self.root_attr + '_id': obj._unchangeable_id, })
            return obj
        elif (obj != None) and (kwargs != {}):
            raise 'error: pass value to method as raw object or **kwargs not both at once'
        else:
            ForeignKeyobj = objects(self.to.__name__, self.dict__to__Class_attrs_values, **kwargs)
            try:
                naw_obj = ForeignKeyobj.all()[0]
            except:
                raise 'error your ForeignKey not found. Check ForeignKey table'

            sqlDB.update('map_db', self.root_className, f'id_ = {self._root_id}',
                         **{self.root_attr + '_id': naw_obj._unchangeable_id, })
            return naw_obj

    def get(self):
        objs = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{'id_': self._related_obj_id})
        return objs.get()


class ManyToManyField:
    class_name = 'ManyToManyField'
    dtype = 'INTEGER'
    root_className = None
    _root_id = None
    root_attr = None
    list_ManyToManyObjcts = []

    def __init__(self, to, null=True):
        self.to = to
        self.null = null
        self.dict__to__Class_attrs_values = {k: v for k, v in to.__dict__.items() if not k.endswith('__')}

    def _apply_rule(self, value):
        pass

    def _check_duplication(self, **kwargs):
        rows, columns = sqlDB.search4(self.root_className + '_' + self.to.__name__, 'map_db', **kwargs)
        if rows == []:
            return False
        else:
            return True

    def add(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            for obj in objs:
                col_val = {self.root_className + '_id': self._root_id,
                           self.to.__name__ + '_id': obj._unchangeable_id}
                if self._check_duplication(**col_val) == True:
                    continue
                self.list_ManyToManyObjcts.append(obj)
                sqlDB.insert4(self.root_className + '_' + self.to.__name__, 'map_db',
                              **col_val)
            return self.list_ManyToManyObjcts
        elif (objs != ()) and (kwargs != {}):
            raise 'error: pass value to method as *raw objects or **kwargs not both at once'
        else:
            for col, value in kwargs.items():
                obj = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{col: value})
                raw_obj = obj.get()
                col_val = {self.root_className + '_id': self._root_id,
                           self.to.__name__ + '_id': raw_obj._unchangeable_id}
                if self._check_duplication(**col_val) == True:
                    continue
                self.list_ManyToManyObjcts.append(raw_obj)
                sqlDB.insert4(self.root_className + '_' + self.to.__name__, 'map_db',
                              **col_val)
            return self.list_ManyToManyObjcts

    def _return_all_toTableObj_related2rootTable(self, to_table_related_col, list_toTable_id=None, **kwargs):
        if list_toTable_id == None:
            list_toTable_id = self.__return_list_Id_related_to_root_obj()
        if kwargs != {}:
            toObj_rows, columns_names = sqlDB.search4(self.to.__name__, 'map_db', related_col=to_table_related_col,
                                                      **{'id_': list_toTable_id, **kwargs})
            list_toTable_id = _get_cells_from_notDBtable(toObj_rows, columns_names, 'id_')
        objs = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{'id_': list_toTable_id})
        return objs.all()

    def all(self):
        return self._return_all_toTableObj_related2rootTable('or')

    def filter(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            list_toTable_id = self._get_final_objID_list_from_input_objs(objs)
            return self._return_all_toTableObj_related2rootTable('and', list_toTable_id)
        elif (objs != ()) and (kwargs != {}):
            raise 'error: pass value to method as *raw objects or **kwargs not both at once'
        else:
            return self._return_all_toTableObj_related2rootTable('and', **kwargs)

    def pop(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            final_objID_list = self._get_final_objID_list_from_input_objs(objs)
            sqlDB.delete4(self.root_className + '_' + self.to.__name__, 'map_db',
                          **{self.to.__name__ + '_id': final_objID_list})

        elif (objs != ()) and (kwargs != {}):
            raise 'error: pass value to method as *raw objects or **kwargs not both at once'
        elif (objs == ()) and (kwargs == {}):
            last_id = self.__return_list_Id_related_to_root_obj()[-1]
            sqlDB.delete4(self.root_className + '_' + self.to.__name__, 'map_db', **{self.to.__name__ + '_id': last_id})
        else:
            list_id_of_ManyToMeny_tabel_which_is__to__ = self.__return_list_Id_related_to_root_obj()
            toObj_rows, columns_names = sqlDB.search4(self.to.__name__, 'map_db', related_col='and',
                                                      **{'id_': list_id_of_ManyToMeny_tabel_which_is__to__, **kwargs})
            list_id = _get_cells_from_notDBtable(toObj_rows, columns_names, 'id_')
            sqlDB.delete4(self.root_className + '_' + self.to.__name__, 'map_db', **{self.to.__name__ + '_id': list_id})

    def _get_final_objID_list_from_input_objs(self, objs):
        final_objID_list = []
        list_id_of_ManyToMeny_tabel_which_is__to__ = self.__return_list_Id_related_to_root_obj()
        for obj in objs:
            if obj._unchangeable_id in list_id_of_ManyToMeny_tabel_which_is__to__:
                final_objID_list.append(obj._unchangeable_id)
        return final_objID_list

    def __return_list_Id_related_to_root_obj(self):
        selfObj_related_toObj_rows, columns_name = sqlDB.search4(self.root_className + '_' + self.to.__name__, 'map_db',
                                                                 **{self.root_className + '_id': self._root_id})
        list_id = _get_cells_from_notDBtable(selfObj_related_toObj_rows, columns_name, self.to.__name__ + '_id')
        return list_id


class OneToOneField:
    class_name = 'OneToOneField'
    dtype = 'INTEGER'
    _related_obj_id = None
    _root_id = None
    root_className = None
    root_attr = None

    def __init__(self, to, on_delete, null=True):
        self.to = to
        self.on_delete = on_delete
        self.null = null
        self.dict__to__Class_attrs_values = {k: v for k, v in to.__dict__.items() if not k.endswith('__')}

    def _apply_rule(self, value):
        dict_attributes_value = value.__dict__
        conn_id = getattr(value, self.root_className + '_id')
        if conn_id != None:
            raise 'Occupied id Error'
        for attr in dict_attributes_value:
            if attr == '_unchangeable_id':
                return value._unchangeable_id
        raise 'Error'

    def _check_and_fix_old_connection(self, obj):
        conn_id = getattr(obj, self.root_className + '_id')
        if conn_id:
            sqlDB.update('map_db', self.root_className, f'{self.root_attr}_id = {obj._unchangeable_id}',
                         **{self.root_attr + '_id': None, })
            sqlDB.update('map_db', self.to.__name__, f'{self.root_className}_id = {self._root_id}',
                         **{self.root_className + '_id': None, })

    def update(self, obj=None, **kwargs):
        if (obj != None) and (kwargs == {}):
            self._check_and_fix_old_connection(obj)
            sqlDB.update('map_db', self.root_className, f'id_ = {self._root_id}',
                         **{self.root_attr + '_id': obj._unchangeable_id, })
            sqlDB.update('map_db', self.to.__name__, f'id_ = {obj._unchangeable_id}',
                         **{self.root_className + '_id': self._root_id, })
            return obj
        elif (obj != None) and (kwargs != {}):
            raise 'error: pass value to method as raw object or **kwargs not both at once'
        else:
            rawobj = objects(self.to.__name__, self.dict__to__Class_attrs_values, **kwargs)
            try:
                naw_obj = rawobj.get()
            except:
                raise 'error your ForeignKey not found. Check ForeignKey table'
            self._check_and_fix_old_connection(naw_obj)
            sqlDB.update('map_db', self.root_className, f'id_ = {self._root_id}',
                         **{self.root_attr + '_id': naw_obj._unchangeable_id, })
            sqlDB.update('map_db', self.to.__name__, f'id_ = {naw_obj._root_id}',
                         **{self.root_className + '_id': self._unchangeable_id, })
            return naw_obj

    def get(self):
        objs = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{'id_': self._related_obj_id})
        return objs.get()

def deep_copy_of_attrs_because_of_their_safety(list_obj):
    fixed_obj_list = []
    import copy
    for obj in list_obj:
        fixed_obj_list.append(copy.deepcopy(obj))
    return fixed_obj_list

