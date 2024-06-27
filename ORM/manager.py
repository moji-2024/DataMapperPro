import sqlDB
import models
# import table_class
data_types = {
    "NULL",      # Python equivalent: None
    "INTEGER",   # Python equivalent: int
    "REAL",      # Python equivalent: float
    "TEXT",      # Python equivalent: str
    "BLOB",      # Python equivalent: bytes
    "VARCHAR"    # Alias for TEXT, Python equivalent: str
}
import inspect
# Print the list of classes
# print(classes)
# Get all classes defined in the module
# classes = [(member[0],member[1]) for member in inspect.getmembers(table_class, inspect.isclass)]
class manager(object):
    # def __init__(self,*dbs):
    #     self.dbs = {}
    #     for db in dbs:
    #         self.dbs.setdefault(db,{})
    @staticmethod
    def create_tabels():
        classes_attrs = models.model._dict_childClassName_dictAttrObjs
        for class_name , dict_attr_obj in classes_attrs.items():
            sqlDB.tabel_maker4(class_name, 'map_db')
            for attr_name, value_class_obj in dict_attr_obj.items():
                if value_class_obj.name == 'ForeignKey':
                    attr_name += '_id'
                elif value_class_obj.name == 'ManyToManyField':
                    sqlDB.tabel_maker4(class_name + '_' + value_class_obj.to.__name__, 'map_db',
                                       class_name + '_id' + ' INTEGER',
                                       value_class_obj.to.__name__ + '_id' + ' INTEGER')
                    continue
                sqlDB.add_col('map_db', class_name, attr_name, dType=value_class_obj.dtype)
        print('all tables created')
    def make_tabels(self,classes_contain_classname_And_Class):
        for class_ in classes_contain_classname_And_Class:
            sqlDB.tabel_maker4(class_[1].__name__, 'map_db')
            dict_class_attrs_values = {k: v for k, v in class_[1].__dict__.items() if not k.startswith('__')}
            for attr_name, column_type in dict_class_attrs_values.items():
                if column_type.__class__.__name__ == 'ForeignKey':
                    attr_name += '_id'
                elif column_type.__class__.__name__ == 'ManyToManyField':
                    sqlDB.tabel_maker4(class_[1].__name__ + '_' + column_type.to.__name__, 'map_db', class_[1].__name__+'_id' + ' INTEGER',column_type.to.__name__+'_id'+ ' INTEGER')
                    continue
                sqlDB.add_col('map_db', class_[1].__name__, attr_name, dType=column_type.dtype)

    def make_tabels_by_classesList(self, classes):
        for class_ in classes:
            sqlDB.tabel_maker4(class_.__name__, 'map_db')
            dict_class_attrs_values = {k: v for k, v in class_.__dict__.items() if not k.startswith('__')}
            for attr_name, column_type in dict_class_attrs_values.items():
                if column_type.__class__.__name__ == 'ForeignKey':
                    attr_name += '_id'
                elif column_type.__class__.__name__ == 'ManyToManyField':
                    sqlDB.tabel_maker4(class_.__name__ + '_' + column_type.to.__name__, 'map_db', class_.__name__+'_id' + ' INTEGER',column_type.to.__name__+'_id'+ ' INTEGER')
                    continue
                sqlDB.add_col('map_db', class_.__name__, attr_name, dType=column_type.dtype)













