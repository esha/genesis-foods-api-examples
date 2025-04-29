import requests
import configparser
import json
import csv
import os

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Retrieve the input file path from the configuration
input_csv = config.get('files', 'input_csv')

# Retrieve options
food_type = config.get('options', 'food_type')
output_limit = int(config.get('options', 'limit', fallback=10000))

# Define the headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

ENGLISH = "973847da-8760-4b54-9981-a596640a4659"

UNITS = {
    "Gram": "a7df0af5-0008-0000-7484-751e8eaf05c6",
    "Pound": "a7df0af5-0007-0000-7484-751e8eaf05c6",
    "Kilogram": "a7df0af5-0009-0000-7484-751e8eaf05c6",
    "Ounce-weight": "a7df0af5-0006-0000-7484-751e8eaf05c6"
}

nutrients = {
    "Calories": "84a8709a-0000-0000-ebf9-90cea7d9d44f",
    "Protein": "84a8709a-0001-0000-ebf9-90cea7d9d44f",
    "Carbohydrates": "84a8709a-0002-0000-ebf9-90cea7d9d44f",
    "Total Dietary Fiber": "84a8709a-0003-0000-ebf9-90cea7d9d44f",
    "Total Soluble Fiber": "84a8709a-0004-0000-ebf9-90cea7d9d44f",
    "Total Sugars": "84a8709a-0006-0000-ebf9-90cea7d9d44f",
    "Monosaccharides": "84a8709a-0007-0000-ebf9-90cea7d9d44f",
    "Disaccharides": "84a8709a-000b-0000-ebf9-90cea7d9d44f",
    "Other Carbohydrate": "84a8709a-0010-0000-ebf9-90cea7d9d44f",
    "Fat": "84a8709a-0011-0000-ebf9-90cea7d9d44f",
    "Saturated Fat": "84a8709a-0012-0000-ebf9-90cea7d9d44f",
    "Monounsaturated Fat": "84a8709a-0013-0000-ebf9-90cea7d9d44f",
    "Polyunsaturated Fat": "84a8709a-0014-0000-ebf9-90cea7d9d44f",
    "Trans Fat": "84a8709a-0015-0000-ebf9-90cea7d9d44f",
    "Cholesterol": "84a8709a-0016-0000-ebf9-90cea7d9d44f",
    "Water": "84a8709a-0017-0000-ebf9-90cea7d9d44f",
    "Vitamin A - IU": "84a8709a-0019-0000-ebf9-90cea7d9d44f",
    "Carotenoid RE": "84a8709a-001b-0000-ebf9-90cea7d9d44f",
    "Retinol RE": "84a8709a-001c-0000-ebf9-90cea7d9d44f",
    "Beta-Carotene": "84a8709a-001d-0000-ebf9-90cea7d9d44f",
    "Vitamin B1 - Thiamin": "84a8709a-001e-0000-ebf9-90cea7d9d44f",
    "Vitamin B2 - Riboflavin": "84a8709a-001f-0000-ebf9-90cea7d9d44f",
    "Vitamin B3 - Niacin": "84a8709a-0020-0000-ebf9-90cea7d9d44f",
    "Vitamin B6": "84a8709a-0022-0000-ebf9-90cea7d9d44f",
    "Vitamin B12": "84a8709a-0023-0000-ebf9-90cea7d9d44f",
    "Biotin": "84a8709a-0024-0000-ebf9-90cea7d9d44f",
    "Vitamin C": "84a8709a-0025-0000-ebf9-90cea7d9d44f",
    "Vitamin D - IU": "84a8709a-0026-0000-ebf9-90cea7d9d44f",
    "Vitamin D": "84a8709a-0027-0000-ebf9-90cea7d9d44f",
    "Folate": "84a8709a-002b-0000-ebf9-90cea7d9d44f",
    "Vitamin K": "84a8709a-002c-0000-ebf9-90cea7d9d44f",
    "Pantothenic Acid": "84a8709a-002d-0000-ebf9-90cea7d9d44f",
    "Calcium": "84a8709a-002f-0000-ebf9-90cea7d9d44f",
    "Chromium": "84a8709a-0031-0000-ebf9-90cea7d9d44f",
    "Copper": "84a8709a-0032-0000-ebf9-90cea7d9d44f",
    "Fluoride": "84a8709a-0033-0000-ebf9-90cea7d9d44f",
    "Iodine": "84a8709a-0034-0000-ebf9-90cea7d9d44f",
    "Iron": "84a8709a-0035-0000-ebf9-90cea7d9d44f",
    "Magnesium": "84a8709a-0036-0000-ebf9-90cea7d9d44f",
    "Manganese": "84a8709a-0037-0000-ebf9-90cea7d9d44f",
    "Molybdenum": "84a8709a-0038-0000-ebf9-90cea7d9d44f",
    "Phosphorus": "84a8709a-0039-0000-ebf9-90cea7d9d44f",
    "Potassium": "84a8709a-003a-0000-ebf9-90cea7d9d44f",
    "Selenium": "84a8709a-003b-0000-ebf9-90cea7d9d44f",
    "Sodium": "84a8709a-003c-0000-ebf9-90cea7d9d44f",
    "Zinc": "84a8709a-003d-0000-ebf9-90cea7d9d44f",
    "Omega 3": "84a8709a-005b-0000-ebf9-90cea7d9d44f",
    "Omega 6": "84a8709a-005c-0000-ebf9-90cea7d9d44f",
    "Alcohol": "84a8709a-006f-0000-ebf9-90cea7d9d44f",
    "Caffeine": "84a8709a-0070-0000-ebf9-90cea7d9d44f",
    "Choline": "84a8709a-007f-0000-ebf9-90cea7d9d44f",
    "Kilojoules": "84a8709a-0081-0000-ebf9-90cea7d9d44f",
    "Vitamin E - Alpha Toco": "84a8709a-0087-0000-ebf9-90cea7d9d44f",
    "Added Sugar": "84a8709a-0094-0000-ebf9-90cea7d9d44f",
    "Folate DFE": "84a8709a-00b7-0000-ebf9-90cea7d9d44f",
    "Vitamin A - RAE": "84a8709a-00c6-0000-ebf9-90cea7d9d44f",
    "Salt": "84a8709a-00cf-0000-ebf9-90cea7d9d44f",
    "Dietary Fiber (US 2016)": "84a8709a-00d0-0000-ebf9-90cea7d9d44f",
    "Soluble Dietary Fiber (US 2016)": "84a8709a-00d1-0000-ebf9-90cea7d9d44f",
    "Calories from Fat": "84a8709a-03ec-0000-ebf9-90cea7d9d44f",
    "Calories from SatFat": "84a8709a-03ed-0000-ebf9-90cea7d9d44f",
    "Calories from TransFat": "84a8709a-03f7-0000-ebf9-90cea7d9d44f",
    "Vitamin A - RE": "30f21f68-ddba-4a1f-8020-b02d7839ede5"
}

supplier_query = """
query ($input: GetUserAddedSuppliersInput!) {
    suppliers {
        getUserAdded(input: $input) {
            suppliers {
                id
                name
            }
        }
    }
}
"""

create_ingredient_mutation = """
mutation($input : CreateFoodInput!){
    foods{
        create(input:$input)
        {
            food{
                id
                name
            }
        }
    }
}
"""

create_supplier_mutation = """
mutation($input: CreateSupplierInput!){
    suppliers{
        create(input: $input) {
            supplier {
               id
               name
            }
        }
    }
}
"""

update_nutrients_mutation = """
mutation($input: SetNutrientValuesInput!){
    foods{
        setNutrientValues(input: $input){
            food{
                id
                name
            }
        }
    }
}
"""

update_alias_mutation = """
mutation($input: SetAliasesInput!){
    foods{
        setAliases(input: $input){
            food{
                aliases{
                    id
                    name
                }
            }
        }
    }
}
"""

update_item_mutation = """
mutation($input: SetNutrientValuesInput!, $amountInput: SetFoodAmountInput!){
    foods{
        setNutrientValues(input: $input){
            food{
                id
                name
            }
        },
        setAmount(input: $amountInput){
            food{
                id
            }
        }
    }
}
"""

set_supplier_mutation = """
mutation($input: SetSupplierInput!){
    foods{
        setSupplier(input: $input){
            food{
                supplier{
                    id
                    name
                }
            }
        }
    }
}
"""


def run_query(graphql_query, variables):
    """Run a GraphQL query against the Genesis API with variables."""
    response = requests.post(
        endpoint,
        json={'query': graphql_query, 'variables': variables},
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None


def update_food_item(item_id, nutrientValues, amounts):
    variables = {
        "input": {
            "foodId": item_id,
            "nutrientValues": nutrientValues
        }, "amountInput": {
            "foodId": item_id,
            "amount": amounts
        }
    }
    result = run_query(update_item_mutation, variables)


def update_aliases(item_id, aliases):
    variables = {
        "input": {
            "aliases": aliases,
            "foodId": item_id
        }
    }
    result = run_query(update_alias_mutation, variables)


def create_ingredient(name):
    item_id = ""
    variables = {
        "input": {
            "name": name,
            "foodType": "Ingredient",
        }
    }
    result = run_query(create_ingredient_mutation, variables)
    if result:
        food = result.get("data", {}).get("foods", {}).get("create", {}).get("food", {})
        return food["id"]


def create_supplier(name):
    variables = {
        "input": {"name": name}
    }

    result = run_query(create_supplier_mutation, variables)
    if result:
        supplier = result.get("data", {}).get("suppliers", {}).get("create", {}).get("supplier", {})
        return supplier["id"]


def get_suppliers():
    output = {}

    variables = {
        "input": {}
    }

    result = run_query(supplier_query, variables)
    if result:
        suppliers = result.get("data", {}).get("suppliers", {}).get("getUserAdded", {}).get("suppliers", {})
        for s in suppliers:
            output[s["name"].lower()] = s["id"]
    return output


def set_supplier_on_food(food_id, supplier_id):

    item = None
    variables = {
        "input": {
            "supplierId": supplier_id,
            "foodId": food_id
        }
    }
    result = run_query(set_supplier_mutation, variables)
    if result:
        item = result.get("data", {}).get("foods", {}).get("setSupplier", {}).get("food", {}).get("supplier", "")

    return item


if __name__ == "__main__":

    # Get the list of suppliers

    suppliers = get_suppliers()

    gnf_supplier_id = ""

    # parse the file
    with open(input_csv, "r", encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile)
        linecount = 0
        for item in csvreader:

            errors = False
            nutrientValues = []

            name = item.get("Name")
            supplier = item.get("Supplier", "")

            # See if we need to create the supplier

            supplier_id = ""
            if supplier != "":
                if supplier.lower() not in suppliers:
                    supplier_id = create_supplier(supplier)
                    print(f"Created new supplier for {supplier}")
                else:
                    supplier_id = suppliers[supplier.lower()]

            # Alias Handling
            aliases = []
            alias_string = item.get("Alias", "")
            if alias_string != "":
                for a in alias_string.split(","):
                    aliases.append({
                            "languageId": ENGLISH,
                            "name": a.strip()
                        })

            # Weights and Conversions; Default to 100g

            weight = item.get("Weight", "100")
            unit = item.get("Unit", "Gram")

            if unit not in UNITS:
                print(f"Unable to find unit '{unit}'!")
                errors = True

            weights = {
                "quantity": weight,
                "unitId": UNITS[unit]
            }

            # Build out the nutrients

            for key in item.keys():
                if key in ["Name", "Product", "Supplier", "Weight", "Unit", "Alias"]:
                    continue
                if key not in nutrients:
                    errors = True
                    print(f"Unknown column header '{key}' - Please correct")
                else:
                    # Add to array
                    nutrient = {}
                    nutrient["nutrientId"] = nutrients[key]
                    nutrient["value"] = item[key]
                    nutrientValues.append(nutrient)

            if errors is False:
                ingredient_id = create_ingredient(name)
                # ingredient_id = "40159a64-6143-4aad-897f-905adc889bfd"
                print(f"Created {name} with Ingredient ID f{ingredient_id}")

                update_food_item(ingredient_id, nutrientValues, weights)
                print(f"Updated nutrients and weights on {name}")

                if supplier_id != "":
                    set_supplier_on_food(ingredient_id, supplier_id)
                    print(f"Set supplier on {name} to {supplier}")

                if aliases != []:
                    update_aliases(ingredient_id, aliases)
                    print(f"Updated aliases on {name}")
            else:
                print(f"Skipped creation of '{name}'!")
