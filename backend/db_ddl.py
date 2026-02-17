# Creates Tables 

from abc import ABC, abstractmethod

class TableCreator(ABC):

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def drop(self, id):
        pass
    

class RecipesCreator(TableCreator):
class IngredientsCreator(TableCreator):
class StepsCreator(TableCreator):
class TagsCreator(TableCreator):
class UnitsCreator(TableCreator):
class RecipeIngredientsCreator(TableCreator):
class RecipeTagsCreator(TableCreator):
