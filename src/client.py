import json
import requests
import sys, os
API_URL = "http://localhost:5000"

def prompt_from_schema(s, ctrl):
    """ Function used to get inputs from the user based on the schema """
    """ Based on the function introduced in exercise 4. """
    """ Takes in session attribute and the Mason control for POST/PUT request """
    body = {}
    if "schema" in ctrl:
        schema = ctrl["schema"]
    required = schema["required"]
    # field is the variable, props is the object under it which contains description and type.
    for field, props in schema["properties"].items():
        if field in required:
            inputvalue = input(props["description" + ":"]) #
            if inputvalue is not None:
                inputvalue = convert_value(inputvalue, props)
            body[field] = inputvalue
    return submit_data(s, ctrl, body)


def convert_value(value, schema_props):
    """ Function used to convert user input strings to right format. """
    """ Based on the function introduced in exercise 4 """
     if schema_props["type"] == "number":
            try:
                value = int(value)
            except ValueError:
                value = float(value)
    if schema_props["type"] == "integer":
        value = int(value)
    return value

def submit_data(s, ctrl, data, headers):
    """ Function used for sending post and put requests. """
    """ Based on the function introduced in exercise 4 """
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = headers) # after logging in to account we need to change headers to contain secret apikey
    return resp

def mainmenu():
    """ This menu has has option to go for price action or account related part of the api """
    os.system("clear")
    print("Hello, this is the client application for Cryptotrading API")
    print("Select (1) if you want to use existing account")
    print("Select (2) if you want to make a new account")
    print("Select (3) if you want to get the most recent trade")

    pass

def priceactionmenu():
    """ This menu has option to get price action data and do something with it """
    os.system("clear")
    print("Input a trading pair to get its most recent pair or press (q) to go back to mainmenu")
    

    pass

def accountsmenu():
    """ This menu has option to add account, or login to existing account """
    """ Sends GET to accounts resource, shows list of accounts """
    """ Select account to login or add new or back to mainmenu """
    pass

def accountmenu():
    """ Option to delete account """
    """ Options to go for orders menu or to positions menu """
    pass

def positionsmenu():
    """ """
    pass

def orderssmenu():
    """ Options for adding new order and for selecting one and deleting it or back to account """
    pass

def main():

    with requests.Session() as s:
        resp = s.get(API_URL)
        body = resp.json()


if __name__ == '__main__':
    main()
