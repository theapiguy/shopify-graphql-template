import requests

SHOP = "YOUR_SHOP_NAME.myshopify.com"
ADMIN_API_TOKEN = "YOUR_ADMIN_API_ACCESS_TOKEN"

def call_shopify_graphql(query, variables=None):
    url = f"https://{SHOP}/admin/api/2023-04/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": ADMIN_API_TOKEN
    }
    payload = {
        "query": query,
        "variables": variables or {}
    }
    response = requests.post(url, json=payload, headers=headers)
    try:
        resp_json = response.json()
    except Exception as e:
        raise Exception(f"Invalid JSON response: {str(e)}")

    # 1. Check for top-level GraphQL errors
    if "errors" in resp_json:
        print(f"Top-level GraphQL errors: {resp_json['errors']}")
        raise Exception(f"GraphQL errors: {resp_json['errors']}")

    # 2. Check for mutation userErrors (example for `metaobjectUpdate`)
    mutation_keys = [k for k in (resp_json.get("data") or {})]
    for key in mutation_keys:
        mutation = resp_json["data"][key]
        if isinstance(mutation, dict) and "userErrors" in mutation and mutation["userErrors"]:
            print(f"Mutation userErrors: {mutation['userErrors']}")
            raise Exception(f"Mutation userErrors: {mutation['userErrors']}")

    # 3. Also check if expected data is null (object not found)
    for key in mutation_keys:
        result = resp_json["data"][key]
        if result is None:
            print(f"Mutation result for {key} is null. Possible not found or failure.")
            raise Exception(f"Mutation result for {key} is null.")

    return resp_json["data"]

# -------------------------------------------
# Example usage for a metaobject update:
query = '''
mutation metaobjectUpdate($id: ID!, $fields: [MetaobjectFieldInput!]!) {
  metaobjectUpdate(id: $id, fields: $fields) {
    metaobject { id }
    userErrors { field message }
  }
}
'''
variables = {
    "id": "gid://shopify/Metaobject/1234567890",
    "fields": [
        { "key": "DistributorID", "value": "NEW-VALUE" }
    ]
}

try:
    data = call_shopify_graphql(query, variables)
    print("Mutation successful:", data)
except Exception as e:
    print("Error:", e)
