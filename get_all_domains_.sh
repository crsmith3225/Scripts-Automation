
# --- Set these three ---
TENANT_DOMAIN="production-mi-authorization.eu.auth0.com"
MGMT_TOKEN="REDACTED"
TARGET_DOMAIN="pernod-ricard.com"   # or just "pernod" to be looser


# 1. Get *all* pages of connections and extract only SAML IDs
connection_ids=$(curl -sS \
  --url "https://${TENANT_DOMAIN}/api/v2/connections?per_page=100&page=0&include_totals=true" \
  --header "Authorization: Bearer $MGMT_TOKEN" \
  | jq -r '.connections[].id')

# 2. Loop through ALL SAML connections and check their domains
for id in $connection_ids; do
  conn=$(curl -sS \
    --url "https://${TENANT_DOMAIN}/api/v2/connections/${id}" \
    --header "Authorization: Bearer $MGMT_TOKEN")

  strategy=$(echo "$conn" | jq -r '.strategy')

  # Only process SAML connections
  if [[ "$strategy" == "samlp" || "$strategy" == "saml" ]]; then
    echo "$conn" | grep -qi "$TARGET_DOMAIN" && {
      echo "========================================"
      echo "MATCH FOUND in connection:"
      echo "$conn" | jq -r '"Name: \(.name)\nID: \(.id)\nDomains: \(.options.domains // [])\nAliases: \(.options.domain_aliases // [])"'
      echo "========================================"
    }
  fi
done
