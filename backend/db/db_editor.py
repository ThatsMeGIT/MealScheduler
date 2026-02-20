# db_editor.py
# Editiert, Löscht oder Fügt Einträge in die SQLite-Datenbank ein

from abc import ABC, abstractmethod

class Editor(ABC):

    @abstractmethod
    def add(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, id):
        pass

    @abstractmethod
    def edit(self, id, *args, **kwargs):
        pass


class RecipesEditor(Editor):

    def add(self, name, ingredients, steps, tags=None):
        sql = "INSERT INTO recipes (name) VALUES (?)"
        print("adding recipe")
        

    def delete(self, recipe_id):
        sql = "DELETE FROM recipes WHERE id = ?"
        print("deleting recipe")

    def edit(self, recipe_id, **changes):
        sql = "UPDATE recipes SET "
        print("editing recipe")


class IngredientsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO ingredients (name) VALUES (?)"
        print("adding Ingredient")
        
    def delete(self):
        sql = "DELETE FROM ingredients WHERE id = ?"
        print("deleting ingredient")
        
    def edit(self):
        sql = "UPDATE ingredients SET name = ? WHERE id = ?"
        print("editing ingredient")
    
    
class StepsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO steps (recipe_id, step_number, description) VALUES (?, ?, ?)"
        print("adding Step")
        
    def delete(self):
        sql = "DELETE FROM steps WHERE id = ?"
        print("deleting Step")
        
    def edit(self):
        sql = "UPDATE steps SET step_number = ?, description = ? WHERE id = ?"
        print("editing Step")
    
    
class TagsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO tags (name) VALUES (?)"
        print("adding Tag")
        
    def delete(self):
        sql = "DELETE FROM tags WHERE id = ?"
        print("deleting Tag")
        
    def edit(self):
        sql = "UPDATE tags SET name = ? WHERE id = ?"
        print("editing Tag")
    
    
class UnitsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO units (name, abbr) VALUES (?, ?)"
        print("adding Unit")
        
    def delete(self):
        sql = "DELETE FROM units WHERE id = ?"
        print("deleting Unit")
        
    def edit(self):
        sql = "UPDATE units SET name = ?, abbr = ? WHERE id = ?"
        print("editing Unit")
    
    
class RecipeIngredientsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit_id, note, position) VALUES (?, ?, ?, ?, ?, ?)"
        print("adding Recipe/Ingredient")
        
    def delete(self):
        sql = "DELETE FROM recipe_ingredients WHERE id = ?"
        print("deleting Recipe/Ingredient")
        
    def edit(self):
        sql = "UPDATE recipe_ingredients SET recipe_id = ?, ingredient_id = ?, quantity = ?, unit_id = ?, note = ?, position = ? WHERE id = ?"
        print("editing Recipe/Ingredient")
    
    
class RecipeTagsEditor(Editor):
    
    def add(self):
        sql = "INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)"
        print("adding Recipe/Tag")
        
    def delete(self):
        sql = "DELETE FROM recipe_tags WHERE recipe_id = ? AND tag_id = ?"
        print("deleting Recipe/Tag")
        
    def edit(self):
        sql = "UPDATE recipe_tags SET tag_id = ? WHERE recipe_id = ? AND tag_id = ?"
        print("editing Recipe/Tag")