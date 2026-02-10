# Only edits the elements of a table

from abc import ABC, abstractmethod

class Repository(ABC):

    @abstractmethod
    def add(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, id):
        pass

    @abstractmethod
    def edit(self, id, *args, **kwargs):
        pass


class RecipesRepository(Repository):

    def add(self, name, ingredients, steps, tags=None):
        print("adding recipe")

    def delete(self, recipe_id):
        print("deleting recipe")

    def edit(self, recipe_id, **changes):
        print("editing recipe")


class IngredientsRepository(Repository):
    
    def add(self):
        print("adding Ingredient")
        
    def delete(self):
        print("deleting ingredient")
        
    def edit(self):
        print("editing ingredient")
    
    
class StepsRepository(Repository):
    
    def add(self):
        print("adding Step")
        
    def delete(self):
        print("deleting Step")
        
    def edit(self):
        print("editing Step")
    
    
class TagsRepository(Repository):
    
    def add(self):
        print("adding Tag")
        
    def delete(self):
        print("deleting Tag")
        
    def edit(self):
        print("editing Tag")
    
    
class UnitsRepository(Repository):
    
    def add(self):
        print("adding Unit")
        
    def delete(self):
        print("deleting Unit")
        
    def edit(self):
        print("editing Unit")
    
    
class RecipeIngredientsRepository(Repository):
    
    def add(self):
        print("adding Recipe/Ingredient")
        
    def delete(self):
        print("deleting Recipe/Ingredient")
        
    def edit(self):
        print("editing Recipe/Ingredient")
    
    
class RecipeTagsRepository(Repository):
    
    def add(self):
        print("adding Recipe/Tag")
        
    def delete(self):
        print("deleting Recipe/Tag")
        
    def edit(self):
        print("editing Recipe/Tag")