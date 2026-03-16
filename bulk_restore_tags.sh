#!/bin/bash
tag_ids=("1120735" "1533109" "1623431" "1696506" "1731765" "1741190" "1751024" "1751026" "1751032" "1761783" "1761784" "1761785" "1761797" "1761846" "1782179" "1788457" "1790925" "1811568" "1864168" "1982654" "2125963" "2127667")

for id in "${tag_ids[@]}"
do
    echo "Restoring Tag: ${id}"

    # Construct the URL dynamically using the current tag_id, update the company ID in the URL
    url="https://document-modification-service.meltwater.io/admin/companies/5cacadff45d60fc8167e3652/tags/${id}/restore"

    # Make the curl request and capture the response    
    response=$(curl -s -X 'POST' "$url" \
        -H 'accept: */*' \
        -H 'x-api-key: 8j5kYr3XqFm5Y3b4Rhly' \
        -H 'x-client-name: Triton-Script' \
        -d '')
    
    # Echo the response
    echo "Response: $response"

    # Sleep for 2 seconds
    sleep 2
done