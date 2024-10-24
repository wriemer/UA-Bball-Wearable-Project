import requests
import json

def main():
    access_url = "https://auth.synergysportstech.com/connect/token"

    # FYI you must create a config.json file with the client_id & client_secret fields
    with open('config.json') as config_file:
        config = json.load(config_file)

    client_id = config['client_id']
    client_secret = config['client_secret']

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'api.basketball.external'
    }

    access_response = requests.post(access_url, data=data)
    access_token = access_response.json().get('access_token')

    print("Response: ", access_response.json())
    print("Access Token: ", access_token)

    # Set the headers with the Bearer token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # url for requesting all leagues
    req_url = "https://basketball.synergysportstech.com/external/api/leagues"

    req_response = requests.get(req_url, headers=headers)

    print("Response: ", req_response.json())



if __name__ == '__main__':
    main()


# Returned Access Token:
# Access Token: eyJhbGciOiJSUzI1NiIsImtpZCI6IjhDRjI4QTUzNTUzOURFMDU3ODFEOEFCRkQ5QUY4QUY1IiwidHlwIjoiYXQrand0In0.eyJpc3MiOiJodHRwczovL2F1dGguc3luZXJneXNwb3J0c3RlY2guY29tIiwibmJmIjoxNzI5NzI0NzU5LCJpYXQiOjE3Mjk3MjQ3NTksImV4cCI6MTcyOTcyODM1OSwiYXVkIjpbImFwaS5iYXNrZXRiYWxsLmV4dGVybmFsIiwiaHR0cHM6Ly9hdXRoLnN5bmVyZ3lzcG9ydHN0ZWNoLmNvbS9yZXNvdXJjZXMiXSwic2NvcGUiOlsiYXBpLmJhc2tldGJhbGwuZXh0ZXJuYWwiXSwiY2xpZW50X2lkIjoiY2xpZW50LmJhc2tldGJhbGwuYWxhYmFtYW1iYiIsImp0aSI6IkQ1RDI2Mjk1ODA2NkNCNDBCRjJEMEJGNjRBMTNGODU3In0.WAKh7Gw-7N-kklisI6Ilt5U_HcDUin8qa6M6PMOc4STEE0iGcH54YAze8NuADejX7nLtk0HWhS8ZxqqWStvZ7xz4fNjFCRZqAZtPZ5jlzg7Y3yIf1_bEp3xrJU-vN4RQOjGAz2KlczA1JJZxtxk2iDbUKaIixuSMyiT2dzX7RDv5XOvRy50zYJ8O6xbTzrJkVfha-BnsBxpK53vLiXXUwfGp1ggidN9bgrnhh61Amq7qoCPSPlmnDPgG4PrTHPrunIeps7ZlwPEsDF-ZjdDl2dKbmV09tJ-a39o5AGS1NtHjgR6dm73-dxspT2GMsoS8ZQRD2NfDhatcLgi2Mo_E1A