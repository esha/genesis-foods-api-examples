import requests
import configparser
import json
import csv
import os
from logging_config import setup_logging
from constants import *

# Set up logging
logger = setup_logging()

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

set_allergen_mutation = """
mutation($input: SetAllergensInput!){
    foods{
        setAllergens(input: $input){
            food{
                id
                allergens{
                    allergen{
                        id
                        name
                    }
                    occurrence
                }
            }
        }
    }
}
"""

verify_allergens_mutation = """
mutation($input: SetAllergensVerifiedInput!){
    foods{
        setAllergensVerified(input: $input){
            food{
                allergensVerified
            }
        }
    }
}
"""

approve_food_mutation = """
mutation($input: ApproveDocumentInput!){
    documents{
        approve(input: $input){
            document{
                id
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
        logger.error(f"Request failed with status code {response.status_code}")
        logger.error(response.text)
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


def set_allergens(item_id, allergenlist):
    variables = {
        "input": {
            "foodId": item_id,
            "foodAllergenInputs": allergenlist
        }
    }
    result = run_query(set_allergen_mutation, variables)

    return result


def verify_allergens(item_id):
    variables = {
        "input": {
            "foodId": item_id,
            "allergensVerified": True
        }
    }
    result = run_query(verify_allergens_mutation, variables)

    return result


def approve_food(item_id):
    variables = {
        "input": {
            "documentId": item_id
        }
    }
    result = run_query(approve_food_mutation, variables)

    return result


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

    # Base work - Get the list of suppliers

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
                    logger.info(f"Created new supplier for {supplier}")
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
                logger.error(f"Unable to find unit '{unit}'!")
                errors = True

            weights = {
                "quantity": weight,
                "unitId": UNITS[unit]
            }

            # Build out the nutrients

            for key in item.keys():
                if key in ["Name", "Product", "Status", "Supplier", "Weight", "Unit", "Alias", "Authority", "Contains Allergens", "May Contain Allergens"]:
                    continue
                if key not in NUTRIENTS:
                    errors = True
                    logger.error(f"Unknown column header '{key}' - Please correct")
                else:
                    # Add to array
                    nutrient = {}
                    nutrient["nutrientId"] = NUTRIENTS[key]
                    nutrient["value"] = item[key]
                    nutrientValues.append(nutrient)

            # Set allergens, if appropriate

            authority = item.get("Authority", "us")
            contains = item.get("Contains Allergens", "")
            maycontain = item.get("May Contain Allergens", "")
            allergeninputs = []

            # If any field is set, process allergens

            if contains != "" or maycontain != "":

                allergens = {}
                if authority.lower() in ["us", "united states"]:
                    allergens = ALLERGENS_US
                elif authority.lower() in ["ca", "canada"]:
                    allergens = ALLERGENS_CA
                elif authority.lower() in ["aus", "australia", "nz"]:
                    allergens = ALLERGENS_AUS
                elif authority.lower() in ["mexico", "mx"]:
                    allergens = ALLERGENS_MX
                elif authority.lower() in ["eu", "european union"]:
                    allergens = ALLERGENS_EU
                else:
                    errors = True
                    logger.error(f"Unable to find valid authority for {authority}!")

                # We have the authority, now let's gather allergens

                if contains != "":
                    for i in [value.lower().strip() for value in contains.split(",")]:
                        if i not in allergens:
                            logger.error(f"Could not find '{i}' in allergens for the {authority} authority!")
                            errors = True
                        else:
                            allergen = {
                                "allergenId": allergens[i],
                                "occurrence": "Present"
                            }
                            allergeninputs.append(allergen)

                if maycontain != "":
                    for i in [value.lower().strip() for value in maycontain.split(",")]:
                        if i not in allergens:
                            logger.error(f"Could not find '{i}' in allergens for the {authority} authority!")
                            errors = True
                        else:
                            allergen = {
                                "allergenId": allergens[i],
                                "occurrence": "MaybePresent"
                            }
                            allergeninputs.append(allergen)

            if errors is False:
                ingredient_id = create_ingredient(name)
                # ingredient_id = "40159a64-6143-4aad-897f-905adc889bfd"
                logger.info(f"Created {name} with Ingredient ID f{ingredient_id}")

                update_food_item(ingredient_id, nutrientValues, weights)
                logger.info(f" Updated nutrients and weights on {name}")

                if supplier_id != "":
                    set_supplier_on_food(ingredient_id, supplier_id)
                    logger.info(f" Set supplier on {name} to {supplier}")

                if aliases != []:
                    update_aliases(ingredient_id, aliases)
                    logger.info(f" Updated aliases on {name}")

                if allergeninputs != []:
                    set_allergens(ingredient_id, allergeninputs)
                    logger.info(f" Updated allergens on {name}")

                # Check if we're auto-approving

                if item.get("Status", "draft").lower() == "approved":

                    # We need to verify the allergens and approve the item

                    verify_allergens(ingredient_id)
                    logger.info(f" Verified allergens on {name}")

                    approve_food(ingredient_id)
                    logger.info(f" Approved ingredient {name}")

            else:
                logger.info(f"Skipped creation of '{name}'!")
