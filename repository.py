from models import GuestBook
import sqlite3

"""
    Design proposal:
Map (object, operation) pair to a specific query to be run.

    Ideas for future improvement:
1. Have query_for_model be automatically created given the list of models
"""

FETCH_ALL_QUERY = "SELECT * FROM ?"

query_for_model = {
    (GuestBook, "save"): "INSERT INTO GuestBook (?, ?, ?) VALUES (?, ?, ?)",
#    (GuestBook, "search_by_id"): "SELECT * FROM GuestBook WHERE id = ?",
    (GuestBook, "delete_by_id"): "DELETE FROM GuestBook WHERE id = ?",
}

class Repository:
    def __init__(self, class_declaration) -> None:
        self._class_declaration = None

    def execute_query(self, query):
            # Idea: Make guestbook the app's name somehow so it can be accessed globally?
            self.connection = sqlite3.connect("guestbook.db")
            cursor = self.connection.execute(query)
            self.connection.commit()

            # This will return an empty list if e.g. an INSERT is executed
            return cursor.fetchall()

    def get_object_variable_values_from_object(self, obj):
        return [(attr, getattr(obj, attr)) for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith("__") and not attr == "id"]
    
    def prepare_query(self, instance_variables, query):
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
    
    def save(self, obj):
         obj_variable_values = self.get_object_variable_values_from_object(obj)
         return self.execute_query(self.prepare_query(obj_variable_values, query_for_model[(type(obj), "save")]))
    
    def fetch_all(self):
        return self.execute_query(self.prepare_query_2(self._class_declaration, FETCH_ALL_QUERY))
    
    def search_by_id(self, id):
        obj_to_find = None
        for obj in self.fetch_all(self._class_declaration):
            if obj.id == id:
                obj_to_find = obj
                break
        
        return obj_to_find
    
    def search_by_attributes(self, attributes):
        for obj in self.fetch_all(self._class_declaration):
            for property, value in attributes.items():
                if not getattr(obj, property) == value:
                    found = False
            
            if found:
                return obj
            
        return None

    def delete(self):
        pass

    def update(self):
        # TODO remove update, handle it in save
        pass

"""
    Convention:
Repository name will be <model_class_name>Repository so we can get class declaration
"""

class GuestBookRepository(Repository):
    def __init__(self) -> None:
        # GuestBookRepository => Guestbook
        self._class_declaration = self.__class__.__name__[:self.__class__.__name__.rfind("Repository")]