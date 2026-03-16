#!/bin/bash
tag_ids=("2127431" "2127432")

for id in "${tag_ids[@]}"
do
    echo "Copying Tag: ${id}"

    # Use the below URL as the endpoint to copy tags between accounts
    url="https://document-modification-service.meltwater.io/admin/copyTagsWithMetadata"

    # Set the body of the curl request payload
    payload="{
      \"tagId\": \"$id\",
      \"fromCompany\": \"61b1c358ba05840009410cc2\",
      \"toCompany\": \"63ac6668bc41a700138b6f91\",
      \"toUserId\": \"64181fd772a6e2000856ba0e\"
    }"

    # Make the curl request looping through the tagId's and updating with next in the array
    response=$(curl -s -X 'POST' "$url" \
        -H "accept: */*" \
        -H "x-api-key: 8j5kYr3XqFm5Y3b4Rhly" \
        -H "x-client-name: Triton-Script" \
        -H "Content-Type: application/json" \
        -d "$payload"

    )
    
    # Echo the response if empty, usually means successful but check in target account
    echo "Response: $response"
    echo "Done with tag ID: ${id}"

    # Sleep for 2 seconds
    sleep 2
done