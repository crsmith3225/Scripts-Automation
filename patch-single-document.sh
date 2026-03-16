# script to update one or many documents
docIds=("doc_id_1" "doc_id_2" "doc_id_3")
DOCUMENT_API_KEY=REDACTED

for docId in "${docIds[@]}"
do
    echo "Updating docId ${docId}"
    echo
    curl -X PATCH "https://mi.content.fairhair.ai/v2/documents/${docId}?apikey=${DOCUMENT_API_KEY}" \
    -H 'accept: application/json' \
    -H 'content-type: application/json' \
    -d '[
    {
        "operation": "setValue",
        "fieldPath": "metaData.source.location.countryCode",
        "value": "cn"
    }
    ]'
    sleep 2
done