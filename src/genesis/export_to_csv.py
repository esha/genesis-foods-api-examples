import requests
import configparser
import json
import csv
import os
from constants import UNITS
from datetime import datetime
from logging_config import setup_logging

# Set up logging
logger = setup_logging()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Retrieve the API settings
endpoint = config.get('api', 'endpoint')
api_key = config.get('api', 'api_key')

# Retrieve the output file path from the configuration
output_file = config.get('files', 'output_file')
recipe_csv = config.get('files', 'recipe_analysis_csv')
ingredient_csv = config.get('files', 'ingredients_csv')
recipe_items_csv = config.get('files', 'recipe_items_csv')

# Retrieve options
food_type = config.get('options', 'food_type')
output_limit = int(config.get('options', 'limit', fallback=10000))

# Ensure the file is written to the local directory
file_path = os.path.join(os.getcwd(), output_file)

# Delete the file if it already exists
if os.path.exists(file_path):
    os.remove(file_path)
    logger.info(f"Existing file '{file_path}' has been deleted.")

# Define the headers
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Define a set of nutrients to include in the analysis
# nutrients_to_include = ["Saturated Fat", 
#                         "Sugar Alcohol", 
#                         "Total Sugars", 
#                         "Trans Fat", 
#                         "Protein", 
#                         "Fat", 
#                         "Carbohydrates", 
#                         "Calories From Fat", 
#                         "Calories from SatFat", 
#                         "Calories from TransFat", 
#                         "Calories", 
#                         "Cholesterol", 
#                         "Total Dietary Fiber", 
#                         "Water"]
nutrients_to_include = ["Added Sugar",
                        "Calcium",
                        "Calories",
                        "Carbohydrates",
                        "Cholesterol",
                        "Fat",
                        "Iron",
                        "Potassium",
                        "Protein",
                        "Saturated Fat",
                        "Sodium",
                        "Total Dietary Fiber",
                        "Total Sugars",
                        "Trans Fat",
                        "Vitamin C",
                        "Vitamin D",
                        "Calories from Fat"]

# Define the GraphQL query
query = """
query($input: FoodSearchInput!){
    foods{
        search(input: $input) {
            foodSearchResults{
                id
                name
            }
            totalCount
            pageInfo{
                cursor
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
}
"""

food_query = """
query($input: GetFoodInput!){
    foods{
        get(input: $input){
            food{
                amountCost { 
                    amount {
                        quantity {
                            value
                        }
                        unit {
                            name
                        }
                    }
                    cost
                }
                conversions{
                    to {
                        quantity {
                            value
                        }
                        unit {
                            name
                        }
                    }
                    from {
                        quantity {
                            value
                        }
                        unit {
                            name
                        }
                    }
                }
                customFields {
                    value
                    customField{
                        name
                    }
                }
                notes {
                    text
                }     
                created
                modified  
                ... on Recipe{
                    id
                    name
                    cookMethod
                    cookTime
                    cookTemperature
                    instructions
                    panSize
                    preparationTime
                    items {
                        food {
                            id
                            name
                        }
                        amount {
                            quantity {
                                value
                            }
                            unit {
                                name
                            }
                        }
                    }
                    unitedStates2016AllergenStatement {
                        englishStatements {
                            statement
                            voluntaryStatement
                        }
                    }
                    unitedStates2016IngredientStatement {
                        englishStatement {
                            customStatement
                            generatedStatement
                        }
                    }                    
                }
                ... on Ingredient{
                    id
                    name
                    subIngredients {
                        name
                        percentage
                    }                            
                }
            }
        }
    }
}
"""

analysis_query = """
query($input : GetAnalysisInput!){
    analysis{
        getAnalysis(input: $input){
            analysis{
                analysisType
                nutrientInfos{
                    nutrient{
                        id
                        name
                    }
                    value
                }
                amountAnalyzed{
                    quantity{
                        value
                    }
                    unit{
                        name
                    }
                }
                weight{
                   quantity{
                        value
                    }
                    unit{
                        name
                    }
                }
            }
        }
    }
}
"""

label_query = """
query($input: GetLabelsForFoodInput!){
    labels{
        getLabelsForFood(input: $input){
            labels{
                id
                regulation {
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
        logger.error(f"Request failed with status code {response.status_code}")
        logger.error(response.text)
        logger.error(f"Endpoint: {endpoint}")
        logger.error(f"Query: {graphql_query} \r\n Variables: {variables}")
        return None


def get_analysis_at_100g(graphql_query, food_id):
    nutrients = {}

    variables = {
        "input": {
            "foodId": food_id,
            "analysisInput": {
                "analysisType": "Net",
                "amount": {
                    "quantity": "100",
                    "unitId": UNITS["Gram"]
                }
            }
        }
    }

    result = run_query(graphql_query, variables)
    if result:
        nutrients = result.get("data", {}).get("analysis", {}).get("getAnalysis", {}).get("analysis", {}).get("nutrientInfos", [])
        if len(nutrients) == 0:
            logger.warning(f"Unable to get nutrient information for {food_id}")

    return nutrients

# Get Net analysis at 1 serving. 
def get_analysis_at_1serving(graphql_query, food_id):
    nutrients = {}

    variables = {
        "input": {
            "foodId": food_id,
            "analysisInput": {
                "analysisType": "Net",
                "amount": {
                    "quantity": "1",
                    "unitId": UNITS["Serving"]
                }
            }
        }
    }

    result = run_query(graphql_query, variables)
    if result:
        nutrients = result.get("data", {}).get("analysis", {}).get("getAnalysis", {}).get("analysis", {}).get("nutrientInfos", [])
        if len(nutrients) == 0:
            logger.warning(f"Unable to get nutrient information for {food_id}")

    return nutrients

# Get LabelRounded analysis at 1 serving. 
def get_analysis_labelrounded(graphql_query, food_id, label_id):
    nutrients = {}

    variables = {
        "input": {
            "foodId": food_id,
            "analysisInput": {
                "analysisType": "LabelRounded",
                "amount": {
                    "quantity": "1",
                    "unitId": UNITS["Serving"]
                },
                "labelId": label_id
            }
        }
    }

    result = run_query(graphql_query, variables)
    if result:
        nutrients = result.get("data", {}).get("analysis", {}).get("getAnalysis", {}).get("analysis", {}).get("nutrientInfos", [])
        if len(nutrients) == 0:
            logger.warning(f"Unable to get nutrient information for {food_id}")

    return nutrients


def search(graphql_query, food_type):
    variables = {
        "input": {
            "searchText": '',
            "foodTypes": [food_type],
            "itemSourceFilter": "Customer",
            "archiveFilter": "Unarchived",
            "versionFilter": "Latest",
            "first": output_limit,
            "after": 0
        }
    }

    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} results.")

    return result

def search_by_modified_date(graphql_query, food_type, modified_after, modified_before):
    variables = {
        "input": {
            "searchText": '',
            "foodTypes": [food_type],
            "itemSourceFilter": "Customer",
            "archiveFilter": "Unarchived",
            "versionFilter": "Latest",
            "modifiedAfter": modified_after.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "modifiedBefore": modified_before.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "first": output_limit,
            "after": 0
        }
    }

    logger.info(f"Running query...")
    result = run_query(graphql_query, variables)
    if result:
        total_count = result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
        logger.info(f"Found {total_count} results.")

    return result

def get_recipe_items(recipe_id):
    variables = {
        "input": {
            "id": recipe_id
        }
    }
    
    logger.info(f"Running query to get recipe items for {recipe_id} ...")
    result = run_query(food_query, variables)
    if result:
        return result.get("data", {}).get("foods", {}).get("get", {}).get("food", {}).get("items", [])
    else:
        return []
    
def get_food_details(food_id):
    variables = {
        "input": {
            "id": food_id
        }
    }
    
    logger.info(f"Running query to get item details for {food_id} ...")
    result = run_query(food_query, variables)
    if result:
        return result.get("data", {}).get("foods", {}).get("get", {}).get("food", {})
    else:
        logger.error(f"Failed to get details for {food_id}")
        return {}

def get_label_id(graphql_query, food_id):
    variables = {
        "input": {
            "foodId": food_id
        }
    }

    logger.info(f"Running query to get label id for {food_id} ...")
    result = run_query(graphql_query, variables)
    if result:
        # This assumes you only have one label for each food. If you have multiple labels, you will 
        # need to modify this. This also is regulation agnostic, it will return the first label id it finds regardless of regulation.
        labels = result.get("data", {}).get("labels", {}).get("getLabelsForFood", {}).get("labels", [])
        logger.info(f"Found {len(labels)} labels for {food_id}")
        return labels[0].get("id", "") if labels else ""
    else:
        logger.warning(f"No labels found for {food_id}")
        logger.error(f"Failed to get label id for {food_id}")
        return ""

def export_to_json(result):
    first_entry = True

    """Iterate through each character and update the searchText."""
    with open(file_path, "a") as file:

        file.write("[\n")  # Write the opening bracket for the JSON array
        if not first_entry:
            file.write(",\n")  # Add a comma before each entry - except first

        json.dump(result, file, indent=4)  # Append the JSON to the file
        first_entry = False

        file.write("\n]")  # Write the closing bracket for the JSON array


def json_to_csv(food_results, csv_file):
    """ Convert a JSON array to CSV format.
        Expectation that this will be the foodSearchResult element of the array
    """

    # Delete the file if it already exists
    if os.path.exists(csv_file):
        os.remove(csv_file)
        logger.info(f"Existing file '{csv_file}' has been deleted.")

    # Different results may have different fields; handle
    fieldnames = []
    for r in food_results:
        for key in r.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    # Write JSON data to CSV
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        # Use the keys of the first item as the header
        # fieldnames = food_results[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write header and rows
        writer.writeheader()
        writer.writerows(food_results)

def filter_and_assign_nutrients(item, nutrients, desired_nutrients=None):
    """
    Filter nutrients and assign them to the item dictionary.
    Args:
        item: The food item dictionary to update
        nutrients: List of nutrient dictionaries with name and value
        desired_nutrients: Optional list of nutrient names to include. If None, include all.
    """
    for n in nutrients:
        nutrient_name = n['nutrient']['name']
        if desired_nutrients is None or nutrient_name in desired_nutrients:
            item[nutrient_name] = n['value']

def process_recipe_items(search_result):
    export_to_json(search_result)
    
    logger.info(f"Processing recipe items...")
    recipes = search_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", [])
    
    # Create list to store all recipe items
    all_recipe_items = []
    
    # Iterate through each recipe
    for recipe in recipes:
        recipe_id = recipe.get("id")
        
        # Get recipe items using food_query
        recipe_data = get_recipe_items(recipe_id)
        
        if recipe_data:
            
            # Extract item details
            for item in recipe_data:
                food = item.get("food", {})
                amount = item.get("amount", {})
                customFields = food.get('customFields', [])
                item_details = {
                    "recipe_id": recipe_id,
                    "item_id": food.get("id"),
                    "item_usercode": next((cf['value'] for cf in customFields if cf.get('customField', {}).get('name') == 'User Code'), ""),
                    "item_name": food.get("name"),
                    "item_amount_measure": amount.get("unit", {}).get("name"),
                    "item_amount_quantity": amount.get("quantity", {}).get("value")
                }
                
                all_recipe_items.append(item_details)
        else:
            logger.error(f"Failed to get details for recipe {recipe_id}")
            
    # Export to CSV
    if all_recipe_items:        
        fieldnames = ["recipe_id", "item_usercode", "item_id", "item_name", "item_amount_measure", "item_amount_quantity"]
        
        with open(recipe_items_csv, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_recipe_items)
            
        logger.info(f"Recipe items exported to {recipe_items_csv}")
    else:
        logger.info("No recipe items found to export")    

def process_ingredients(ingredient_result):
    export_to_json(ingredient_result)
    # Process ingredients
    logger.info(f"Processing ingredients...")
    if ingredient_result:
        ingredient_items = ingredient_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", [])
        for item in ingredient_items:
            nutrients = get_analysis_at_100g(analysis_query, item['id'])            
            ingredient_info = get_food_details(item['id'])
            amountCost = ingredient_info.get('amountCost', {})
            conversions = ingredient_info.get('conversions', {})
            customFields = ingredient_info.get('customFields', [])
            subIngredients = ingredient_info.get('subIngredients', [])
            item['usercode'] = next((cf['value'] for cf in customFields if cf.get('customField', {}).get('name') == 'User Code'), "")

            # Extract cost and amount information from amountCost
            if amountCost:
                item['cost'] = amountCost.get('cost', '')
                # Combine amount value and unit into single column
                amount_value = amountCost.get('amount', {}).get('quantity', {}).get('value', '')
                amount_unit = amountCost.get('amount', {}).get('unit', {}).get('name', '')
                item['amount'] = f"{amount_value} {amount_unit}".strip()
            else:
                item['cost'] = ''
                item['amount'] = ''

            # Sub Ingredients
            item['subIngredients'] = ','.join(subIngredient.get('name', '') for subIngredient in subIngredients)

            filter_and_assign_nutrients(item, nutrients, nutrients_to_include)
        json_to_csv(ingredient_items, ingredient_csv)
    logger.info(f"Ingredients exported to {ingredient_csv}")

# Process recipe analysis
def process_recipes(recipe_result):
    export_to_json(recipe_result)

    logger.info(f"Processing recipes...")
    
    # Process recipes
    if recipe_result:
        recipe_items = recipe_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", [])
        for item in recipe_items:
            # If you want to get LabelRounded analysis, you must insert code here to call the label_query to get the 
            # label_id for this food, then call the get_analysis_labelrounded function.
            # Example:
            label_id = get_label_id(label_query, item['id'])
            if label_id:
                nutrients = get_analysis_labelrounded(analysis_query, item['id'], label_id)
            else:
                nutrients = get_analysis_at_1serving(analysis_query, item['id'])
            
            recipe_info = get_food_details(item['id'])                
            amountCost = recipe_info.get('amountCost', {})
            conversions = recipe_info.get('conversions', {})
            customFields = recipe_info.get('customFields', [])

            # Cook Method
            item['cookMethod'] = recipe_info.get('cookMethod', '')
            # Cook Time
            item['cookTime'] = recipe_info.get('cookTime', '')
            # Cook Temperature
            item['cookTemperature'] = recipe_info.get('cookTemperature', '')
            # Instructions
            item['instructions'] = recipe_info.get('instructions', '')
            # Pan Size
            item['panSize'] = recipe_info.get('panSize', '')
            # Preparation Time
            item['preparationTime'] = recipe_info.get('preparationTime', '')
            # Ingredient Statement
            ingredientStatement = recipe_info.get('unitedStates2016IngredientStatement', {}).get('englishStatement', {}).get('generatedStatement', {})
            item['ingredientStatement'] = ingredientStatement
            # Allergen Statement
            allergenStatement = recipe_info.get('unitedStates2016AllergenStatement', {}).get('englishStatements', {}).get('statement', {})
            voluntaryStatement = recipe_info.get('unitedStates2016AllergenStatement', {}).get('englishStatements', {}).get('voluntaryStatement', {})
            item['allergenStatement'] = allergenStatement
            item['voluntaryStatement'] = voluntaryStatement
            # Notes
            notes = recipe_info.get('notes', [])
            item['notes'] = '|'.join(note.get('text', '') for note in notes)

            # User Code
            item['usercode'] = next((cf['value'] for cf in customFields if cf.get('customField', {}).get('name') == 'User Code'), "")                
            filter_and_assign_nutrients(item, nutrients, nutrients_to_include)

            # Extract cost and amount information from amountCost
            if amountCost:
                item['cost'] = amountCost.get('cost', '')
                # Combine amount value and unit into single column
                amount_value = amountCost.get('amount', {}).get('quantity', {}).get('value', '')
                amount_unit = amountCost.get('amount', {}).get('unit', {}).get('name', '')
                item['amount'] = f"{amount_value} {amount_unit}".strip()
            else:
                item['cost'] = ''
                item['amount'] = ''
        
        json_to_csv(recipe_items, recipe_csv)
    logger.info(f"Recipes exported to {recipe_csv}")

# Run the playground script
if __name__ == "__main__":
    start_time = datetime.now()

    # Get modified date input from user
    date_input_after = input("Enter modified after date (e.g. 2023-12-31 or 12/31/2023) or press Enter to skip: ")
    
    date_input_before = ""
    if date_input_after.strip():
        date_input_before = input("Enter modified before date(e.g. 2023-12-31 or 12/31/2023) or press Enter to skip: ")

    # Ask the user if they want Ingredients, Recipe Analysis, Recipe Items, or All, then proceed accordingly.
    choice = input("Do you want to export Ingredients, Recipe Analysis, Recipe Items, or All? (i/r/ri/a): ")
    if choice.lower() not in ['i', 'r', 'ri', 'a']:
        logger.error("Invalid choice. Exiting.")
        exit(0)

    if not date_input_after.strip() and not date_input_before.strip():
        proceed = input("No dates entered. Do you want to proceed with a regular search? (y/n): ")
        if proceed.lower() != 'y':
            logger.info("Exiting as per user request")
            exit(0)
        
        logger.info(f"Starting export process...")
        
        # Search for ingredients if needed
        ingredient_result = None
        if choice.lower() in ['i', 'a']:
            ingredient_result = search(query, "Ingredient")
            if ingredient_result is None:
                logger.error(f"No ingredient results found. Exiting.")
                exit(0)
            # Process ingredients
            process_ingredients(ingredient_result)

        # Search for recipes if needed
        recipe_result = None
        if choice.lower() in ['r', 'ri', 'a']:
            recipe_result = search(query, "Recipe")
            if recipe_result is None:
                logger.error(f"No recipe results found. Exiting.")
                exit(0)
            # Process recipes
            if choice.lower() in ['r', 'a']:
                process_recipes(recipe_result)
            # Process recipe items if needed
            if choice.lower() in ['ri', 'a']:
                process_recipe_items(recipe_result)
    else:
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",  # 2023-12-31
            "%m/%d/%Y",  # 12/31/2023
            "%d/%m/%Y",  # 31/12/2023
            "%Y/%m/%d"   # 2023/12/31
        ]

        modified_after_date = None
        modified_before_date = None
        for fmt in date_formats:
            try:
                modified_after_date = datetime.strptime(date_input_after, fmt)
                modified_before_date = datetime.strptime(date_input_before, fmt)
                break
            except ValueError:
                continue

        if modified_after_date is None or modified_before_date is None:
            logger.error("Invalid date format provided. Please use YYYY-MM-DD or MM/DD/YYYY")
            exit(1)

        logger.info(f"Using modified date after: {modified_after_date.strftime('%Y-%m-%d')}")
        logger.info(f"Using modified date before: {modified_before_date.strftime('%Y-%m-%d')}")
        logger.info(f"Starting export process...")
        
        # Search for ingredients if needed
        ingredient_result = None
        if choice.lower() in ['i', 'a']:
            logger.info(f"Searching for ingredients...")
            ingredient_result = search_by_modified_date(query, "Ingredient", modified_after_date, modified_before_date) 

            if ingredient_result is None:
                logger.error(f"No ingredient results found. Exiting.")
                exit(0)

            # Process ingredients
            process_ingredients(ingredient_result)
         
        # Search for recipes if needed
        recipe_result = None
        if choice.lower() in ['r', 'ri', 'a']:
            logger.info(f"Searching for recipes...")
            recipe_result = search_by_modified_date(query, "Recipe", modified_after_date, modified_before_date)

            if recipe_result is None:
                logger.error(f"No recipe results found. Exiting.")
                exit(0)

            # Process recipes
            if choice.lower() in ['r', 'a']:
                process_recipes(recipe_result)
            # Process recipe items if needed
            if choice.lower() in ['ri', 'a']:
                process_recipe_items(recipe_result)
 
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    logger.info(f"Exporting complete.")
    logger.info(f"Total elapsed time: {elapsed_time}")
