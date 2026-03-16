import requests

# Auth0 Configuration
TENANT_DOMAIN = "production-mi-authorization.eu.auth0.com"
MANAGEMENT_API_TOKEN = "POST_API_TOKEN_HERE"
TARGET_APP_CLIENT_ID = "RSJ60SWn1aIAVTbHFDvhjwvutzZaZZSx"


# Get All Connection Details
def get_all_saml_connections(token):
    all_connections = []
    page = 0
    per_page = 20  # matches Auth0 Dashboard UI

    headers = {"Authorization": f"Bearer {token}"}

    while True:
        url = f"https://{TENANT_DOMAIN}/api/v2/connections"
        params = {
            "strategy": "samlp",
            "page": page,
            "per_page": per_page
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        batch = response.json()

        if not batch:
            break  # no more pages

        all_connections.extend(batch)
        page += 1

    return all_connections


# Update Connection if missing Insided Application
def update_connection_if_missing(token, connection):
    connection_id = connection["id"]
    name = connection["name"]
    enabled_clients = connection.get("enabled_clients", [])

    if TARGET_APP_CLIENT_ID in enabled_clients:
        print(f"- {name}: already contains target client ID")
        return False  # no update needed

    updated_clients = enabled_clients + [TARGET_APP_CLIENT_ID]

    url = f"https://{TENANT_DOMAIN}/api/v2/connections/{connection_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {"enabled_clients": updated_clients}

    response = requests.patch(url, headers=headers, json=payload)
    response.raise_for_status()

    print(f"+ Updated: {name}")
    return True

#Main Function
def main():
    token = MANAGEMENT_API_TOKEN

    print("Fetching ALL SAML connections (paginated)...")
    connections = get_all_saml_connections(token)

    print(f"Found {len(connections)} SAML connections.\n")

    updates = 0
    for conn in connections:
        changed = update_connection_if_missing(token, conn)
        if changed:
            updates += 1

    print("\n==============================")
    print(f"Completed. Updated {updates} connections.")
    print("==============================")

if __name__ == "__main__":
    main()
