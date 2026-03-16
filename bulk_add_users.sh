# script to update one or many documents
users=()
JWT_Token="REDACTED"

for user in "${users[@]}"
do
    echo "Adding user ${user}"
    echo
    curl -X 'POST' \
      'https://tritonserver-staging.meltwater.io/admin/addUser' \
      -H 'accept: */*' \
      -H 'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNocmlzdG9waGVyLnNtaXRoIiwicGVybWlzc2lvbnMiOlsicmVhZCIsIndyaXRlIiwiYWRtaW4iXSwic2VuZGdyaWRwZXJtaXNzaW9ucyI6WyJyZWFkIiwid3JpdGUiLCJhZG1pbiJdLCJkYXNoYm9hcmRwZXJtaXNzaW9ucyI6WyJyZWFkIiwid3JpdGUiLCJhZG1pbiJdLCJ0d2l0dGVyeHBlcm1pc3Npb25zIjpbInJlYWQiXSwiaWF0IjoxNzAxMTkwMTQ2LCJleHAiOjE3MDEyNzY1NDZ9.AER4YvMHj76a_AAu8J3bLVtedD9DHIxK-ZEwanihI2ljVrTi-N31vdtHxCMl9tkYCg0h3RXgKnNHZYsCy4fdlSAjT1hYDdK5CqqrIgxXz1Qdmi2nIntOWhgz87bRYseYSkIUoGD0Wo9Qd3HUMh1qtCRm0_XkemGAsVYzttCuQAYfl516DlVax9WVzuuPobLnXAjRrkpsp2ObzA0NgJwc9bSSbbLxRyQgQwytMMhCzsrkvSdFDKCf43EmJOCIt9NtnCn3ftAgHtoRH7DbJc4zHd8GFecZcqrl5XVF9njte94FvViYtEd9C-LjpYt3vdz5SjMHJWVn2I4EhWIKDXeeFZ05K30Tkoh18E0Chq_7Mm8shG31i5NhlFY7DskK2O9MEvDgUxr549btY7g0AQv3nYK0guL-yoz_yQJYfkWL3ZFpEvbOr4felzaLuYA3PGUydUzhfmY_AlaX4RVNdOVwcde31ci-P4kRf0rKeXwxJ9yig8QUQpsFVHJzPCEq-8DJhii4cXMnBJZSwRvz4PvbIFIgsqShisGZ4gPB4XCoUTPPnbPuSe-ittBnYOc4-nyCdWYIu_N_64hx9AUsJFSHtnoLqOFihhMbAcMacroSRXCHOtKvna8hGuUz4yDmxc_I3Wy6LpX7DETsY2d4IPBRgo3fByKeyhOJxPIzpGI2tgE' \
      -H 'Content-Type: application/json' \
      -d '{
      "email": "warren.lynch@meltwater.com",
      "permissions": [
        "read",
        "write",
        "admin"
      ],
     "sendgridpermissions": [
            "read",
            "write",
            "admin"
        ],
     "dashboardpermissions": [
            "read",
            "write",
            "admin"
        ]
        }'
    sleep 3
done