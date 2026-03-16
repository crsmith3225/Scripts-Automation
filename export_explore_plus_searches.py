import requests
import json
import csv
import time
import random

# === Configuration  ===
AUTH_TOKEN = 'Bearer REDACTED'
ACCOUNT_ID = '5d6d192c496948001656e623'


BASE_URL = f'https://r4dar-darlyng-prod.meltwater.io/1.0/accounts/{ACCOUNT_ID}'
SEARCH_LIST_URL = f'{BASE_URL}/search-queries-groups/search'
QUERY_DETAIL_URL = f'{BASE_URL}/queries/'
WORKSPACE_GRAPHQL_URL = "https://mw-graph.meltwater.io/graphql"

HEADERS = {
    'authorization': AUTH_TOKEN,
    'content-type': 'application/json'
}

# === Getting the workspaces ===

def get_workspaces_data():
    """
    Pull all workspaces from the account using GraphQL.
    """
    payload = {
        "query": """
        query GetWorkspace {
            viewer {
                company {
                    workspaces {
                        _id
                        name
                        description
                        created
                        users { _id }
                    }
                } 
            }
        }
        """,
        "variables": {}
    }
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'ApolloGraphql-Client-Name': 'mi-web-app',
        'Connection': 'keep-alive',
        'authorization': AUTH_TOKEN,
        'Content-Type': 'application/json'
    }

    response = requests.post(WORKSPACE_GRAPHQL_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    workspaces = data['data']['viewer']['company']['workspaces']
    return [{"id": ws["_id"], "name": ws["name"], "description": ws["description"]} for ws in workspaces]

# === Getting the Searches ===

def get_all_search_ids(workspace_id=None, group_id=None):
    offset = 0
    count = 100
    all_items = []
    url = SEARCH_LIST_URL  

    print(f"\n🔎 Fetching searches from the {'Admin Workspace' if not workspace_id else 'workspace ' + workspace_id}")
    # print(f"   → Using URL: {url}")

    while True:
        payload = {
            "showHidden": True,
            "textSearch": "",
            "pagination": {
                "count": count,
                "offset": offset,
                "sortOrder": "asc",
                "sortBy": "label"
            },
            "type": "Query",
            "rootOnly": False,
            "additionalFields": ["groupPath"]
        }

        # workspace/group filtering
        if workspace_id:
            payload["workspaceId"] = workspace_id
        if group_id:
            payload["groupId"] = group_id

        #print(f"   → Sending request with offset={offset}, workspaceId={workspace_id}, groupId={group_id}")
        response = requests.post(url, headers=HEADERS, data=json.dumps(payload), timeout=60)

        try:
            response.raise_for_status()
        except Exception as e:
            print(f"   ⚠️ Request failed: {e}")
            print(f"   Response text: {response.text[:500]}")
            raise

        data = response.json()
        total = data.get('total', 0)
        items = data.get('data', [])
        #print(f"   → Received {len(items)} items (total={total})")

        for item in items:
            group_path = item.get("groupPath", [])
            gp_id = group_path[0].get("id") if group_path else ""
            gp_label = group_path[0].get("label") if group_path else ""

            all_items.append({
                "id": item.get("id"),
                "label": item.get("label"),
                "description": item.get("description"),
                "updated": item.get("updated"),
                "parentLabel": item.get("parentLabel", ""),
                "groupPath_id": gp_id,
                "groupPath_label": gp_label
            })

        offset += count
        if offset >= total:
            break

    print(f"   ✅ Collected {len(all_items)} searches from {'Admin Workspace' if not workspace_id else workspace_id}\n")
    return all_items


# ==== Getting the query details ====

def get_query_details(query_id, workspace_id=None, retries=3):
    if workspace_id:
        url = f"{BASE_URL}/workspaces/{workspace_id}/queries/{query_id}"
    else:
        url = f"{QUERY_DETAIL_URL}{query_id}"

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            if response.status_code == 504 and attempt < retries:
                wait = 2 ** attempt + random.uniform(0, 1)
                print(f"   ⚠️ 504 Timeout for {query_id}. Retrying in {wait:.1f}s...")
                time.sleep(wait)
                continue
            else:
                raise
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Request error for {query_id}: {e}")
            raise

def extract_combined_queries_labels(details):
    combined_ids = ""
    combined_labels = ""

    if details.get("kind") == "Combined":
        references = details.get("references", {})
        query_ids = references.get("queries", [])
        combined_ids = ", ".join(str(qid) for qid in query_ids)

        label_map = {}
        combined_info = details.get("combined", {})
        must_queries = combined_info.get("must", [])
        must_not_queries = combined_info.get("mustNot", [])
        should_queries = combined_info.get("should", [])

        for q in must_queries + must_not_queries + should_queries:
            qid = q.get("id")
            label = q.get("label")
            label_map[qid] = label

        combined_labels_list = [label_map.get(qid, "Unknown") for qid in query_ids]
        combined_labels = ", ".join(combined_labels_list)

    return combined_ids, combined_labels

# ==== Clause Parsing ===

def parse_search_clause(clause):
    output = {
        "query_string": "",
        "spam_type": "",
        "countries": "",
        "followers_gt": "",
        "followers_lt": "",
        "profile_type": "",
        "languages": "",
        "tones": "",
        "platforms": ""
    }

    def extract_from_dict(item):
        if "meltwaterBoolean" in item:
            output["query_string"] = item["meltwaterBoolean"].get("query", "")
        if "spam-type" in item:
            output["spam_type"] = ", ".join(item["spam-type"])
        if "countries" in item:
            output["countries"] = ", ".join(item["countries"])
        if "followers" in item:
            followers = item["followers"]
            output["followers_gt"] = str(followers.get("gt", ""))
            output["followers_lt"] = str(followers.get("lt", ""))
        if "profileType" in item:
            output["profile_type"] = ", ".join(item["profileType"])
        if "languages" in item:
            output["languages"] = ", ".join(item["languages"])
        if "tones" in item:
            output["tones"] = ", ".join(item["tones"])
        if "platforms" in item:
            output["platforms"] = ", ".join(item["platforms"])

    if isinstance(clause, str):
        try:
            clause = json.loads(clause)
        except json.JSONDecodeError:
            output["query_string"] = clause
            return output

    if isinstance(clause, dict):
        stack = [clause]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                extract_from_dict(current)
                for value in current.values():
                    if isinstance(value, list):
                        stack.extend(value)
                    elif isinstance(value, dict):
                        stack.append(value)
            elif isinstance(current, list):
                stack.extend(current)

    return output

# === Exporting Docs ===

def export_to_csv(data, filename='FIFA-search_export.csv'):
    if not data:
        print("No data to export.")
        return

    keys = list(data[0].keys())

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Exported {len(data)} to '{filename}'")

# === Main function ===

def main():
    print("\n🔎 Fetching Workspace lists for the account")
    workspaces = get_workspaces_data()
    print(f"   ✅ {len(workspaces)} workspaces were found\n")

    results = []

    # Fetch searches from the Admin Workspace default
    search_items = get_all_search_ids()
    print(f"🔎 Fetching the details of the {len(search_items)} searches in the Admin Workspace.")

    for idx, item in enumerate(search_items, 1):
        search_id = item["id"]
        print(f"   ✅[Admin Workspace {idx}/{len(search_items)}] Fetching details for Search ID: {search_id}")
        try:
            details = get_query_details(search_id)
            combined_ids, combined_labels = extract_combined_queries_labels(details)

            search_clause = details.get("filter", {}).get("searchClause")
            parsed = parse_search_clause(search_clause)

            results.append({
                "id": details.get("id"),
                "label": item.get("label"),
                "description": item.get("description"),
                "created": details.get("created"),
                "updated": item.get("updated"),
                "parentLabel": item.get("parentLabel"),
                "groupPath_id": item.get("groupPath_id"),
                "groupPath_label": item.get("groupPath_label"),
                "kind": details.get("kind"),
                "queryLength": details.get("queryLength"),
                "query_string": parsed["query_string"],
                "spam_type": parsed["spam_type"],
                "countries": parsed["countries"],
                "followers_gt": parsed["followers_gt"],
                "followers_lt": parsed["followers_lt"],
                "profile_type": parsed["profile_type"],
                "languages": parsed["languages"],
                "tones": parsed["tones"],
                "platforms": parsed["platforms"],
                "combined_ids": combined_ids,
                "combined_labels": combined_labels,
                "workspace": "Admin Workspace",
                "workspace_name": "Admin Workspace"
            })
        except Exception as e:
            print(f"⚠️ Failed to fetch details for Search ID {search_id} (Admin Workspace): {e}")

        time.sleep(random.uniform(0.5, 1.5))  # Rate limit

    # Fetch searches from each workspace
    for ws in workspaces:
        ws_id = ws["id"]
        #print(f"\n�� Fetching searches from the workspace: {ws['name']} ({ws_id})")
        ws_items = get_all_search_ids(workspace_id=ws_id)
        print(f"🔎 Fetching details of the {len(ws_items)} assets in {ws['name']} ({ws_id})")

        for idx, item in enumerate(ws_items, 1):
            search_id = item["id"]
            print(f"   ✅[{ws['name']} ({ws_id}) {idx}/{len(ws_items)}] Fetching details for Search ID: {search_id}")
            try:
                details = get_query_details(search_id, workspace_id=ws_id)
                combined_ids, combined_labels = extract_combined_queries_labels(details)

                search_clause = details.get("filter", {}).get("searchClause")
                parsed = parse_search_clause(search_clause)

                results.append({
                    "id": details.get("id"),
                    "label": item.get("label"),
                    "description": item.get("description"),
                    "created": details.get("created"),
                    "updated": item.get("updated"),
                    "parentLabel": item.get("parentLabel"),
                    "groupPath_id": item.get("groupPath_id"),
                    "groupPath_label": item.get("groupPath_label"),
                    "kind": details.get("kind"),
                    "queryLength": details.get("queryLength"),
                    "query_string": parsed["query_string"],
                    "spam_type": parsed["spam_type"],
                    "countries": parsed["countries"],
                    "followers_gt": parsed["followers_gt"],
                    "followers_lt": parsed["followers_lt"],
                    "profile_type": parsed["profile_type"],
                    "languages": parsed["languages"],
                    "tones": parsed["tones"],
                    "platforms": parsed["platforms"],
                    "combined_ids": combined_ids,
                    "combined_labels": combined_labels,
                    "workspace": ws_id,
                    "workspace_name": ws["name"]
                })
            except Exception as e:
                print(f"⚠️ Failed to fetch details for ID {search_id} (workspace {ws['name']} ({ws_id})): {e}")

            time.sleep(random.uniform(0.5, 1.5))  # Rate limit

    export_to_csv(results)


if __name__ == "__main__":
    main()
