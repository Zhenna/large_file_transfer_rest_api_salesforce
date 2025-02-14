import requests
import os
import json


SF_INSTANCE_NAME = ""
SF_API_VERSION = ""
SF_CONSUMER_KEY = ""
SF_CONSUMER_SECRET = ""
SF_USER_NAME = ""
SF_USER_PASSWORD = ""
SF_USER_ID = ""
SF_SECURITY_TOKEN = ""


def get_access_token(
        sf_instance_name: str,
        sf_consumer_key: str,
        sf_consumer_secret: str,
        sf_user_name: str,
        sf_user_password: str,
        sf_security_token: str
) -> str:
    """
    Obtain an access token from Salesforce using the client credentials flow.
    
    Parameters:
        sf_instance_name: Salesforce instance name
        sf_consumer_key: Salesforce consumer key
        sf_consumer_secret: Salesforce consumer secret
        sf_user_name: Salesforce username
        sf_user_password: Salesforce password
        sf_security_token: Salesforce security token

    Returns:
        Access token
    """

    token_url = f"https://{sf_instance_name}/services/oauth2/token"

    credentials = {
        'grant_type': 'password',
        'client_id': sf_consumer_key,
        'client_secret': sf_consumer_secret,
        'username': sf_user_name,
        'password': sf_user_password + sf_security_token
    }

    try:
        response = requests.post(token_url, data=credentials)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        print(f"Response data: {response.json()}")

        if "access_token" in response.json():
            print("Access token obtained successfully.\n {}".format(response.json()["access_token"]))
            return response.json()["access_token"]
        else:
            error_message = response.json().get('error_description', 'Unknown error occurred')
            print(f"Failed to obtain access token: {error_message}")
            raise Exception(f"Failed to obtain access token: {error_message}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to obtain access token: {e}")
        raise Exception(f"Failed to obtain access token: {e}")
    

def upload_small_file(
        access_token: str,
        url: str,
        file_path: str,
        file_name: str,
        data: str
) -> None:
    """
    Upload a file to Salesforce using the REST API.

    Parameters:
        access_token: access token
        url: Salesforce REST API URL
        file_path: path to the file
        file_name: name of the file
        data: file data

    Returns:
        None
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    body = {
        "Title": file_name,
        "VersionData": data,
        "PathOnClient": file_path,
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=600)
        print(f"Response: {response.json()}")
        if response.status_code in [200, 201]:
            print("Upload successfully!")
        else:
            print(f"Failed to upload data to ContentVersion: {response.json()}")
            raise Exception(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload data to ContentVersion: {e}")
        raise Exception(e)


def upload_large_file(
        access_token: str,
        url: str,
        file_path: str,
        file_name: str,
        description: str = None
) -> None:
    """
    Upload large files to Salesforce using the REST API using multipart/form-data.

    Parameters:
        access_token: access token
        url: Salesforce REST API URL
        file_path: path to the file
        file_name: name of the file
        description: file description

    Returns:
        None
    """
    print("Size of file : {} bytes.".format(os.stat(file_path).st_size))

    entity_content = json.dumps({
        'Title': file_path.split('.')[0] if file_name is None else file_name,
        'Description': description,
        'PathOnClient': file_path,
    })

    files = {
        'entity_content': (None, entity_content, 'application/json'),
        'VersionData': (file_path, open(file_path, "rb"), 'application/json;charset=UTF-8') 
        #'application/octet-stream' also works
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": '*/*'
        # drop the header below to let requests set the boundary string
        # 'Content-Type': 'multipart/form-data; boundary=bbeb9489e668a93c6d9b5bfe6cc19445'
    }

    try:
        response = requests.post(url=url, headers=headers, files=files)
        print(f"Response: {response.json()}")
        if response.status_code in [200, 201]:
            print("Upload successfully!")
        else:
            print(f"Failed to upload data to ContentVersion: {response.json()}")
            raise Exception(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload data to ContentVersion: {e}")
        raise Exception(e)


if __name__ == "__main__":

    # Obtain access token
    access_token = get_access_token(
        sf_instance_name=SF_INSTANCE_NAME,
        sf_consumer_key=SF_CONSUMER_KEY,
        sf_consumer_secret=SF_CONSUMER_SECRET,
        sf_user_name=SF_USER_NAME,
        sf_user_password=SF_USER_PASSWORD,
        sf_security_token=SF_SECURITY_TOKEN
    )

    # Get salesforce instance url
    # URL = f"https://{SF_INSTANCE_NAME}/services/data/v{SF_API_VERSION}/sobjects/ContentVersion"
    
    # Upload small file
    # upload_small_file(
    #     access_token=access_token,
    #     url=URL,
    #     file_path='put_it_here.txt',
    #     file_name="Test File",
    #     data="This is my data."
    # )

    # Upload large file
    # upload_large_file(
    #     access_token=access_token,
    #     url=URL,
    #     file_path='200MB-TESTFILE.pdf',
    #     file_name="200MB TESTFILE ",
    #     description="This is a 200 MB test file."
    # )