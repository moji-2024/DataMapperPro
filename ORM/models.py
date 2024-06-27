import sqlDB

ignor_tuple = ('dict_col_obj', 'class_name', '_unchangeable_id', 'objects')


def _get_cells_from_notDBtable(rows, columns, target_col):
    list_cells = []
    target_index = 0
    for index, col in enumerate(columns):
        if col == target_col:
            target_index = index
            break
    for row in rows:
        list_cells.append(row[target_index])
    return list_cells


def _check_truthnessOfvlaues_of_args_and_kwargs(dict_col_obj, *args, **kwargs):
    newkwargs = {}
    tuple_of_rules_obj = tuple(dict_col_obj.values())
    tuple_of_keies = tuple(dict_col_obj.keys())
    if args != ():
        for index, arg in enumerate(args):
            if tuple_of_rules_obj[index].name == 'ForeignKey':
                newkwargs[tuple_of_keies[index] + '_id'] = tuple_of_rules_obj[index]._apply_rule(arg)
            elif tuple_of_rules_obj[index].name == 'ManyToManyField':
                pass
            else:
                newkwargs[tuple_of_keies[index]] = tuple_of_rules_obj[index]._apply_rule(arg)
    else:
        for key, value in kwargs.items():
            if dict_col_obj[key].name == 'ForeignKey':
                newkwargs[key + '_id'] = dict_col_obj[key]._apply_rule(value)
            elif dict_col_obj[key].name == 'ManyToManyField':
                pass
            else:
                newkwargs[key] = dict_col_obj[key]._apply_rule(value)
    return newkwargs


def _create_dict_relationName_by_dict_childClassName_dictAttrObjs(_dict_childClassName_dictAttrObjs):
    _dict_relationTabels = {}
    _dict_product_set = {}
    for class_instance, attr_cls_obj in _dict_childClassName_dictAttrObjs.items():
        for attr, cls_obj in attr_cls_obj.items():
            if cls_obj.name == 'ForeignKey' or cls_obj.name == 'ManyToManyField':
                _dict_relationTabels.setdefault(cls_obj.to.__name__, (class_instance, attr, cls_obj))
                _dict_product_set.setdefault(class_instance, _dict_childClassName_dictAttrObjs[class_instance])
    return _dict_relationTabels, _dict_product_set

def _get_id_related2root_table_from_col_of_ManyToManyField_table(to_table_name,to_dict_kwargs,intermediate_table_name,root_table_name):
    query = {}
    rows, columns = sqlDB.search4(to_table_name, 'map_db',**{to_dict_kwargs})
    list_toTable_id = _get_cells_from_notDBtable(rows, columns, 'id_')
    if list_toTable_id != []:
        rows, columns = sqlDB.search4(intermediate_table_name,'map_db',**{root_table_name + '_id':list_toTable_id})
        list_rootTable_related_id = _get_cells_from_notDBtable(rows, columns, root_table_name + '_id')
        if list_rootTable_related_id != []:
            query['id_'] = list_rootTable_related_id
    return query
class objects:
    def __init__(self, class_name, dict_attr, **kwargs):
        self.class_name = class_name
        self.obj_list = []
        self.dict_attr = dict_attr
        self.kwargs = kwargs

    def all(self):
        return db_class(self.class_name, self.dict_attr, **self.kwargs)

    def filter(self, **kwargs):
        query = dict()
        query.update(**self.kwargs)
        for key, value in kwargs.items():
            key_splited = key.split('__')
            if self.dict_attr[key_splited[0]].name == 'ForeignKey':
                rows, columns = sqlDB.search4(self.dict_attr[key_splited[0]].to.__name__, 'map_db',
                                              **{key_splited[1]: value})
                query[key_splited[0] + '_id'] = rows[0][0]
            elif self.dict_attr[key_splited[0]].name == 'ManyToManyField':
                query = _get_id_related2root_table_from_col_of_ManyToManyField_table(
                    self.dict_attr[key_splited[0]].to.__name__,{key_splited[1]: value},
                    self.class_name + '_' + self.dict_attr[key_splited[0]].to.__name__,self.class_name
                )
            else:
                query[key_splited[0]] = value
        return db_class(self.class_name, self.dict_attr, **{**self.kwargs,**query})
        # rows, columns = sqlDB.search4(self.class_name, 'map_db', **query)
        # return self._append_obj_to_objList(rows, columns)

    def get(self, **query):
        query.update(**self.kwargs)
        rows, columns = sqlDB.search4(self.class_name, 'map_db', **query)
        return self._append_obj_to_objList(rows, columns)[0]

    def create(self, *args, **kwargs):
        dict_col_obj = self._return_dict_attr_objValue()
        newkwargs = _check_truthnessOfvlaues_of_args_and_kwargs(dict_col_obj, *args, **kwargs)
        last_id = sqlDB.insert4(self.class_name, 'map_db', *args, **newkwargs)
        rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=f'ORDER BY id_ DESC LIMIT 1')
        self._unchangeable_id = last_id
        return self._append_obj_to_objList(rows, columns)[0]

    def _append_obj_to_objList(self, rows, columns):
        local_list = []
        for row in rows:
            dict_col_obj = self._return_dict_attr_objValue()
            local_list.append(raw_Class(row, columns, self.class_name, dict_col_obj))
        return local_list

    def _return_dict_attr_objValue(self):
        return {k: v for k, v in self.dict_attr.items() if not k.startswith('__')}


class db_class(objects):
    def __init__(self, class_name, dict_attr=None, conditions='', **kwargs):
        self.conditions = conditions
        self.class_name = class_name
        self.obj_list = []
        self.dict_attr = dict_attr
        self.kwargs = kwargs

    def order_by(self, order_str):
        if order_str[0] == '-':
            self.conditions += f'ORDER BY {order_str} DESC '
        else:
            self.conditions += f'ORDER BY {order_str} '
        return db_class(self.class_name, self.dict_attr, conditions=self.conditions, **self.kwargs)

    def __repr__(self):
        rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=self.conditions, **self.kwargs)
        return repr(self._append_obj_to_objList(rows, columns))

    def __getitem__(self, key):
        if isinstance(key, slice):
            offset = key.start
            end = key.stop
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
        elif isinstance(key, int):
            if key < 0:
                rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                            sort_by=self.conditions + f'ORDER BY id_ DESC LIMIT 1 OFFSET {abs(key) - 1}',
                                            **self.kwargs)
            elif key == -1:
                rows, columns = sqlDB.view4(self.class_name, 'map_db', sort_by=f'ORDER BY id_ DESC LIMIT 1',
                                            **self.kwargs)
            else:
                rows, columns = sqlDB.view4(self.class_name, 'map_db',
                                            sort_by=self.conditions + f'limit {1} offset {key}', **self.kwargs)
            return self._append_obj_to_objList(rows, columns)[0]


class model:
    _dict_relationTabels = {}
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
    def __init__(self, rows, columns, class_name, dict_col_obj):
        self.dict_col_obj = dict_col_obj
        self.class_name = class_name
        _dict_relationTabels, dict_product_set = _create_dict_relationName_by_dict_childClassName_dictAttrObjs(
            model._dict_childClassName_dictAttrObjs)
        self._create_attr_by_row_column(rows, columns)
        self._create_setAttr_by_dict_relationTabels(class_name, _dict_relationTabels, dict_product_set)
        self._create_Attr_to__toClass___by_dict_col_obj_(dict_col_obj, class_name)
    def _create_attr_by_row_column(self,rows,columns):
        for i in range(len(columns)):
            if i == 0:
                setattr(self, '_unchangeable_id', rows[i])
            else:
                setattr(self, columns[i], rows[i])
    def _create_setAttr_by_dict_relationTabels(self,class_name,_dict_relationTabels,dict_product_set):
        if class_name in _dict_relationTabels.keys():
            set_dict_to_setattr = {}
            name_target_key = _dict_relationTabels[class_name][0]
            if _dict_relationTabels[class_name][2].name == 'ForeignKey':
                set_dict_to_setattr[_dict_relationTabels[class_name][1] + '_id'] = self._unchangeable_id
                setattr(self, name_target_key + '_set',
                        objects(name_target_key, dict_product_set[name_target_key], **set_dict_to_setattr))
            elif _dict_relationTabels[class_name][2].name == 'ManyToManyField':
                ManyToManyField_related_table_name = name_target_key + '_' + self.class_name
                rows, columns = sqlDB.search4(ManyToManyField_related_table_name, 'map_db', related_col='Or',
                                              **{self.class_name + '_id': self._unchangeable_id})
                list_cells = _get_cells_from_notDBtable(rows, columns, name_target_key + '_id')
                if list_cells != []:
                    set_dict_to_setattr['id_'] = list_cells

                setattr(self, name_target_key + '_set',
                        objects(name_target_key, dict_product_set[name_target_key], **set_dict_to_setattr))

    def _create_Attr_to__toClass___by_dict_col_obj_(self,dict_col_obj,class_name):
        for attr, obj in dict_col_obj.items():
            if obj.__class__.__name__ == 'ForeignKey':
                obj.root_attr = attr
                obj._unchangeable_id = self._unchangeable_id
                obj.root_className = class_name
                setattr(self, attr, obj)

            elif obj.__class__.__name__ == 'ManyToManyField':
                obj.root_className = class_name
                obj._unchangeable_id = self._unchangeable_id
                obj.attr = attr
                setattr(self, attr, obj)
            else:
                pass
    def delete(self):
        _dict_relationTabels, dict_product_set = _create_dict_relationName_by_dict_childClassName_dictAttrObjs(
            model._dict_childClassName_dictAttrObjs)
        del_rowID_root_table = sqlDB.delete4(self.class_name, 'map_db', id_=self._unchangeable_id)

        def del_from_related_tables():
            # delete from intermdiated table
            del_rowID_related_table = None
            if self.class_name in dict_product_set.keys():
                for obj in dict_product_set[self.class_name].values():
                    if obj.name == 'ManyToManyField':
                        del_rowID_related_table = sqlDB.delete4(self.class_name + '_' + obj.to.__name__, 'map_db',
                                                                **{self.class_name + '_id': self._unchangeable_id})
                return del_rowID_root_table, del_rowID_related_table
            # delete from main related table
            try:
                if _dict_relationTabels[self.class_name][2].name == 'ForeignKey':
                    ForeignKey_related_table_name = _dict_relationTabels[self.class_name][0]
                    del_rowID_related_table = sqlDB.delete4(ForeignKey_related_table_name, 'map_db',
                                                            **{self.class_name + '_id': self._unchangeable_id})

                elif _dict_relationTabels[self.class_name][2].name == 'ManyToManyField':
                    ManyToManyField_related_table_name = _dict_relationTabels[self.class_name][
                                                             0] + '_' + self.class_name
                    del_rowID_related_table = sqlDB.delete4(ManyToManyField_related_table_name, 'map_db',
                                                            **{self.class_name + '_id': self._unchangeable_id})
            except:
                pass
            return del_rowID_root_table, del_rowID_related_table

        return del_from_related_tables()

    def save(self):
        attributes = self.__dict__
        query = dict()
        for key in self.dict_col_obj:
            query[key] = attributes[key]
        _check_truthnessOfvlaues_of_args_and_kwargs(self.dict_col_obj, **query)
        sqlDB.update('map_db', self.class_name, f'id_ = {self._unchangeable_id}', **query)

    def __repr__(self):
        dictforstr = {k: v for k, v in self.__dict__.items() if k not in ignor_tuple}
        return 'class raw_Class :' + str(dictforstr)


class DecimalField:
    name = 'DecimalField'
    dtype = 'REAL'
    _unchangeable_id = None
    root_className = None
    root_attr = None

    def __init__(self, max_digits=8, decimal_places=2):
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
    name = 'CharField'
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
    name = 'ForeignKey'
    dtype = 'INTEGER'
    _unchangeable_id = None
    root_className = None
    root_attr = None

    def __init__(self, to, on_delete, null=True):
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
            sqlDB.update('map_db', self.root_className, f'id_ = {self._unchangeable_id}',
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

            sqlDB.update('map_db', self.root_className, f'id_ = {self._unchangeable_id}',
                         **{self.root_attr + '_id': naw_obj._unchangeable_id, })
            return naw_obj

    def get(self):
        root_Obj_rows, columns_names = sqlDB.search4(self.root_className, 'map_db', related_col='Or',
                                                     **{'id_': self._unchangeable_id})
        root_aatr_id = _get_cells_from_notDBtable(root_Obj_rows, columns_names, self.root_attr + '_id')[0]
        objs = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{'id_': root_aatr_id})
        return objs.all()[0]

    def __repr__(self):
        return str(self.root_className + '.' + self.root_attr + ' has to methods update and get')


class ManyToManyField:
    name = 'ManyToManyField'
    dtype = 'INTEGER'
    root_className = None
    _unchangeable_id = None
    root_attr = None
    list_ManyToManyObjcts = []

    def __init__(self, to, null=True):
        self.to = to
        self.null = null
        self.dict__to__Class_attrs_values = {k: v for k, v in to.__dict__.items() if not k.endswith('__')}

    def _apply_rule(self, value):
        pass
    def _check_duplication(self,**kwargs):
        rows,columns = sqlDB.search4(self.root_className + '_' + self.to.__name__, 'map_db',**kwargs)
        if rows == []:
            return False
        else:
            return True
    def add(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            for obj in objs:
                col_val = {self.root_className + '_id': self._unchangeable_id,
                                 self.to.__name__ + '_id': obj._unchangeable_id}
                if self._check_duplication(**col_val) == True:
                    continue
                self.list_ManyToManyObjcts.append(obj)
                sqlDB.insert4(self.root_className + '_' + self.to.__name__, 'map_db',
                              **{self.root_className + '_id': self._unchangeable_id,
                                 self.to.__name__ + '_id': obj._unchangeable_id})
            return self.list_ManyToManyObjcts
        elif (objs != ()) and (kwargs != {}):
            raise 'error: pass value to method as *raw objects or **kwargs not both at once'
        else:
            for col, value in kwargs.items():
                obj = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{col: value})
                raw_obj = obj.all()[0]
                col_val = {self.root_className + '_id': self._unchangeable_id,
                                 self.to.__name__ + '_id': raw_obj._unchangeable_id}
                if self._check_duplication(**col_val) == True:
                    continue
                self.list_ManyToManyObjcts.append(raw_obj)
                sqlDB.insert4(self.root_className + '_' + self.to.__name__, 'map_db',
                              **{self.root_className + '_id': self._unchangeable_id,
                                 self.to.__name__ + '_id': raw_obj._unchangeable_id})
            return self.list_ManyToManyObjcts
    def _return_all_toTableObj_related2rootTable(self,to_table_related_col,list_toTable_id=None,**kwargs):
        if list_toTable_id == None:
            list_toTable_id = self.__return_list_Id_related_to_root_obj()
        toObj_rows, columns_names = sqlDB.search4(self.to.__name__, 'map_db', related_col=to_table_related_col,
                                                  **{'id_': list_toTable_id,**kwargs})
        list_toTable_id = _get_cells_from_notDBtable(toObj_rows, columns_names, 'id_')
        objs = objects(self.to.__name__, self.dict__to__Class_attrs_values, **{'id_': list_toTable_id})
        return objs.all()
    def all(self):
        return self._return_all_toTableObj_related2rootTable('or')

    def filter(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            list_toTable_id = self._get_final_objID_list_from_input_objs(objs)
            return self._return_all_toTableObj_related2rootTable('and',list_toTable_id)
        elif (objs != ()) and (kwargs != {}):
            raise 'error: pass value to method as *raw objects or **kwargs not both at once'
        else:
            return self._return_all_toTableObj_related2rootTable('and',**kwargs)

    def pop(self, *objs, **kwargs):
        if (objs != ()) and (kwargs == {}):
            final_objID_list = self._get_final_objID_list_from_input_objs(objs)
            sqlDB.delete4(self.root_className + '_' + self.to.__name__, 'map_db', **{self.to.__name__ + '_id': final_objID_list})

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
    def _get_final_objID_list_from_input_objs(self,objs):
        final_objID_list = []
        list_id_of_ManyToMeny_tabel_which_is__to__ = self.__return_list_Id_related_to_root_obj()
        for obj in objs:
            if obj._unchangeable_id in list_id_of_ManyToMeny_tabel_which_is__to__:
                final_objID_list.append(obj._unchangeable_id)
        return final_objID_list
    def __return_list_Id_related_to_root_obj(self):
        selfObj_related_toObj_rows, columns_name = sqlDB.search4(self.root_className + '_' + self.to.__name__, 'map_db',
                                                                 **{self.root_className + '_id': self._unchangeable_id})
        list_id = _get_cells_from_notDBtable(selfObj_related_toObj_rows, columns_name, self.to.__name__ + '_id')
        return list_id

    # def __repr__(self):
    #     # print(self.__dict__)
    #     # print(self.root_className,self.root_attr)
    #     return repr(self.name)
        # return self.name
        # return self.root_className + '.' + self.root_attr + ' has methods add, all and filter'


# class _save_attr_from_rowsAndColumns_of_db:
#     def __init__(self, rows, columns):
#         if rows != []:
#             for value, attr in zip(rows[0], columns):
#                 setattr(self, attr, value)
#     def __repr__(self):
#         return 'Inner obj: ' + str(self.__dict__)
