from models import GuestBook
import sqlite3

"""
    Design proposal:
Map (object, operation) pair to a specific query to be run.
Repository name will be <model_class_name>Repository so the model name
can be extracted.

    Ideas for future improvement:
1. Have query_for_model be automatically created given the list of models
"""

FETCH_ALL_QUERY = "SELECT * FROM ?"

query_for_model = {
    "save": "INSERT INTO <modelname> (?, ?, ?) VALUES (?, ?, ?)",
#    (GuestBook, "search_by_id"): "SELECT * FROM GuestBook WHERE id = ?",
    "fetch_all": "SELECT ?, ?, ?, ? FROM <modelname>",
    "delete_by_id": "DELETE FROM <modelname> WHERE id = ?",
}

class Repository:
    def __init__(self) -> None:
        # XxxRepository => Repository
        self._class_name = self.__class__.__name__[:self.__class__.__name__.rfind("Repository")]

    def execute_query(self, query):
            print(query)
            # Idea: Make guestbook the app's name somehow so it can be accessed globally?
            self.connection = sqlite3.connect("guestbook.db")
            cursor = self.connection.execute(query)
            self.connection.commit()

            # This will return an empty list if e.g. an INSERT is executed
            return cursor.fetchall()

    def get_object_variable_values_from_object(self, obj):
        return [(attr, getattr(obj, attr)) for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__") and not attr == "id"]
    
    def prepare_query(self, instance_variables, query):
         query = query.replace("<modelname>", self._class_name)

         # Replace ?s in a query with actual attributes/values
         # TODO get rid of these two loops, this should be done in only one
         for attr, _ in instance_variables:
              query = query.replace("?", attr, 1)
        
         for _, value in instance_variables:
            if isinstance(value, str):
                value = "'" + value + "'"

            query = query.replace("?", value, 1)

         return query
    
    # can we overload prepare_query by explicitly setting expected types for parameters?
    def prepare_query_2(self, class_name, query):
        query = query.replace("?", class_name, 1)
        return query
    
    def prepare_fetch_all_query(self, instance_variables, query):
        query = query.replace("<modelname>", self._class_name)
        for property_name, _ in instance_variables:
            query = query.replace("?", property_name, 1)

        return query
            
    
    def save(self, obj):
         obj_variable_values = self.get_object_variable_values_from_object(obj)
         return self.execute_query(self.prepare_query(obj_variable_values, query_for_model["save"]))
    
    def fetch_all(self):
        # Maybe move this so that repo always has access to _class?
        import importlib
        _class = getattr(importlib.import_module("models"), self._class_name)
        instance_variables = self.get_object_variable_values_from_object(_class())
        instance_variables.append(("id", None))
        print(instance_variables)

        items = []
        for row in self.execute_query(self.prepare_fetch_all_query(instance_variables, query_for_model["fetch_all"])):
            item = _class()
            for i in range(len(instance_variables)):
                setattr(item, instance_variables[i][0], row[i])
            items.append(item)
        
        return items
    
    def search_by_id(self, id):
        obj_to_find = None
        for obj in self.fetch_all(self._class_name):
            if obj.id == id:
                obj_to_find = obj
                break
        
        return obj_to_find
    
    def search_by_attributes(self, attributes):
        items = []
        for obj in self.fetch_all():
            found = True
            for property, value in attributes.items():
                if not getattr(obj, property) == value:
                    found = False
            
            if found:
                items.append(obj)
            
        return items

    def delete(self):
        pass

    def update(self):
        # TODO remove update, handle it in save
        pass



class GuestBookRepository(Repository):
    pass