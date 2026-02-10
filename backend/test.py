from db_new import Database


def main():
    Database.build_db()
    print("did it")

    Database.add_recipe(
        name="Tomatensalat",
        ingredients=[
            {"name": "Tomate", "quantity": 3, "unit": "Stk", "note": "gewürfelt"},
            {"name": "Olivenöl", "quantity": 2, "unit": "EL"},
            {"name": "Salz", "note": "nach Geschmack"},
        ],
        steps=[
            "Tomaten würfeln.",
            "Mit Öl und Salz vermengen.",
            "Kurz ziehen lassen."
        ],
        tags=["vegan", "schnell"]
    )

    print("Inserted recipe")


main()
