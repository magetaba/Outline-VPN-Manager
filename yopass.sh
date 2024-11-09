#!/bin/bash
message=$1;
password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 20 );

GNUPGHOME=$(mktemp -d /tmp/.gnupgXXXXXX);
export GNUPGHOME;

# Encrypt message with $password and replace newlines with "\n";
message=$(echo "$message" | gpg -a --batch --passphrase "$password" -c --cipher-algo AES256 2>/dev/null | sed ':a;N;$!ba;s/\n/\\n/g');

# Ensure JSON formatting is correct by escaping quotes properly
payload=$(cat <<EOF
{
  "message": "$message",
  "expiration": 604800,
  "one_time": true
}
EOF
);

response=$(curl -k -s -XPOST https://api.yopass.se/secret -H 'Content-Type: application/json' -d "$payload")

# Check if the response is an HTML page (simple check for "DOCTYPE html")
if echo "$response" | grep -q '<!DOCTYPE html>'; then
  echo "Error: Received HTML response instead of JSON. Possible issue with the API endpoint."
  echo "Response: $response"
  exit 1
fi

# Proceed with jq parsing if the response is valid JSON
secret_id=$(echo "$response" | jq -r .message)

if [ -z "$secret_id" ]; then
  echo "Error: Unable to extract secret_id"
else
  echo "https://yopass.se/#/s/$secret_id/$password";
fi
