import requests

# Auth0 Configuration 
TENANT_DOMAIN = "production-mi-authorization.eu.auth0.com"
MANAGEMENT_API_TOKEN = "POST_API_TOKEN_HERE"
TARGET_APP_CLIENT_ID = "RSJ60SWn1aIAVTbHFDvhjwvutzZaZZSx"


# Gather all connection details
def get_all_saml_connections(token):
    all_connections = []
    page = 0
    per_page = 20  # Pull 20 connections at a time

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


# Dry run - Check which connections would be updated
def dry_run_check(connection):
    enabled_clients = connection.get("enabled_clients", [])
    name = connection["name"]

    if TARGET_APP_CLIENT_ID in enabled_clients:
        print(f"✓ {name}: already contains target client ID")
        return False

    print(f"→ {name}: would be updated (target client ID missing)")
    return True


# Main Function 
def main():
    print("Requesting Management API token...")
    token = MANAGEMENT_API_TOKEN

    print("Fetching SAML connections...")
    connections = get_all_saml_connections(token)

    print(f"Found {len(connections)} SAML connections.\n")

    missing_count = 0
    for conn in connections:
        if dry_run_check(conn):
            missing_count += 1

    print("\n==============================")
    print(f"Dry-run complete. {missing_count} connections WOULD be updated.")
    print("No changes were made.")
    print("==============================")

if __name__ == "__main__":
    main()
