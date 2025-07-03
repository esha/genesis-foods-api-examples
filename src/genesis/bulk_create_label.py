import configparser
import os
from datetime import datetime
import requests
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
output_csv = config.get('files', 'output_csv')

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

search_query = """
    query ($input: FoodSearchInput!){
        foods {
            search(input: $input) {
                foodSearchResults{
                    id
                    name
                    modified
                    created
                    versionName
                    eshaCode
                    foodType
                    product
                    supplier
                    versionHistoryId
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

create_us2016_label_mutation = """
    mutation ($input: CreateUnitedStates2016LabelInput!){
        label {
            unitedStates2016 {
                create (input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

create_ca2016_label_mutation = """
    mutation ($input: CreateCanada2016LabelInput!){
        label {
            canada2016 {
                create (input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

create_eu2011_label_mutation = """
    mutation ($input: CreateEuropeanUnion2011LabelInput!){
        label {
            europeanUnion2011 {
                create (input: $input) {
                    label {
                        id  
                        name
                    }
                }
            }
        }
    }
"""

create_mx2020_label_mutation = """
    mutation ($input: CreateMexico2020LabelInput!){
        label {
            mexico2020 {
                create (input: $input) {
                    label {
                        id  
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_us2016_label_mutation = """
    mutation ($input: SetUnitedStates2016LabelItemsInput!){
        label {
            unitedStates2016 {
                setLabelItems(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_ca2016_label_mutation = """
    mutation ($input: SetCanada2016LabelItemsInput!){
        label {
            canada2016 {
                setLabelItems(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_eu2011_label_mutation = """
    mutation ($input: SetEuropeanUnion2011LabelItemInput!){
        label {
            europeanUnion2011 {
                setLabelItem(input: $input) {
                    label {
                        id
                        name
                    }
                }
            }
        }
    }
"""

add_recipe_to_mx2020_label_mutation = """
    mutation ($input: SetMexico2020LabelItemInput!){
        label {
            mexico2020 {
                setLabelItem(input: $input) {
                    label {
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

def create_us2016_label(graphql_query, food_name):
    label_name = f"{food_name} - US 2016 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical",
            "recommendationProfile": "Adult"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("unitedStates2016", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create US 2016 label for {food_name}")
        return None
    
def create_ca2016_label(graphql_query, food_name):
    label_name = f"{food_name} - CA 2016 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("canada2016", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create CA 2016 label for {food_name}")
        return None
    
def create_eu2011_label(graphql_query, food_name):
    label_name = f"{food_name} - EU 2011 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("europeanUnion2011", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create EU 2011 label for {food_name}")
        return None    
    
def create_mx2020_label(graphql_query, food_name):
    label_name = f"{food_name} - MX 2020 - Generated on " + datetime.now().strftime("%Y-%m-%d")
    variables = {
        "input": {
            "name": label_name,
            "labelStyle": "StandardVertical"
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("mexico2020", {}).get("create", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to create MX 2020 label for {food_name}")
        return None

def add_recipes_to_label(graphql_query, food_ids, label_id):
    variables = {
        "input": {
            "foodIds": food_ids,
            "labelId": label_id
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("unitedStates2016", {}).get("setItem", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to add recipe to label for {food_id}")
        return None
    
def add_single_recipe_to_label(graphql_query, food_id, label_id):
    variables = {
        "input": {
            "foodId": food_id,
            "labelId": label_id
        }
    }
    result = run_query(graphql_query, variables)
    if result:
        return result.get("data", {}).get("label", {}).get("europeanUnion2011", {}).get("setLabelItem", {}).get("label", {}).get("id", "")
    else:
        logger.error(f"Failed to add recipe to EU 2011 label for {food_id}")
        return None

if __name__ == "__main__":
    logger.info(f"Starting bulk create label process...")
    
    search_result = search(search_query, food_type)  # Food type from config
    if search_result is None:
        logger.error(f"No results found. Exiting.")
        exit(0)

    # Get the total count of search results
    total_count = search_result.get("data", {}).get("foods", {}).get("search", {}).get("totalCount", 0)
    logger.info(f"Found {total_count} {food_type} items to process.")
    
    # Ask user about label types after search results are known
    print(f"\nFound {total_count} {food_type} items.")
    print("Available label types:")
    print("1. US 2016")
    print("2. CA 2016") 
    print("3. EU 2011")
    print("4. MX 2020")
    print("5. All label types")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            break
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    # Define which label types to create based on user choice
    label_types_to_create = []
    if choice == '1':
        label_types_to_create = ['US2016']
    elif choice == '2':
        label_types_to_create = ['CA2016']
    elif choice == '3':
        label_types_to_create = ['EU2011']
    elif choice == '4':
        label_types_to_create = ['MX2020']
    elif choice == '5':
        label_types_to_create = ['US2016', 'CA2016', 'EU2011', 'MX2020']
    
    logger.info(f"Selected label types: {', '.join(label_types_to_create)}")

    # Create labels and add recipes to them
    for food in search_result.get("data", {}).get("foods", {}).get("search", {}).get("foodSearchResults", []):
        food_name = food.get("name", "")
        food_id = food.get("id", "")
        
        # Create labels based on user selection
        if 'US2016' in label_types_to_create:
            us2016_label_id = create_us2016_label(create_us2016_label_mutation, food_name)
            if us2016_label_id:
                add_recipes_to_label(add_recipe_to_us2016_label_mutation, [food_id], us2016_label_id)
        
        if 'CA2016' in label_types_to_create:
            ca2016_label_id = create_ca2016_label(create_ca2016_label_mutation, food_name)
            if ca2016_label_id:
                add_recipes_to_label(add_recipe_to_ca2016_label_mutation, [food_id], ca2016_label_id)
        
        if 'EU2011' in label_types_to_create:
            eu2011_label_id = create_eu2011_label(create_eu2011_label_mutation, food_name)
            if eu2011_label_id:
                add_single_recipe_to_label(add_recipe_to_eu2011_label_mutation, food_id, eu2011_label_id)
        
        if 'MX2020' in label_types_to_create:
            mx2020_label_id = create_mx2020_label(create_mx2020_label_mutation, food_name)
            if mx2020_label_id:
                add_single_recipe_to_label(add_recipe_to_mx2020_label_mutation, food_id, mx2020_label_id)

    logger.info(f"Bulk create label process completed.")    

    
    
