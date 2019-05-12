import json
import requests
import sys, os
API_URL = "http://localhost:5000"

def prompt_from_schema(ctrl):
    """ Function used to get inputs from the user based on the schema
        Based on the function introduced in exercise 4.
        Takes in the Mason control for POST/PUT request
    """
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

    return body

def convert_value(value, schema_props):
    """ Function used to convert user input strings to right format.
        Based on the function introduced in exercise 4
    """
     if schema_props["type"] == "number":
            try:
                value = int(value)
            except ValueError:
                value = float(value)
    if schema_props["type"] == "integer":
        value = int(value)
    return value

def submit_data(s, ctrl, data, headers):
    """ Function used for sending post and put requests.
        Based on the function introduced in exercise 4
        takes in session, mason control, data and headers
    """
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = headers)
    return resp

def mainmenu():
    """ This menu has has option to go for price action or account related part of the api """
    os.system("clear")
    print("Hello, this is the client application for Cryptotrading API")
    print("Select (1) if you want to use existing account")
    print("Select (2) if you want to make a new account")
    print("Select (3) if you want to get the most recent trade")

    while True:
        choice = input("Give your selection please: ")
        if choice == 1:
            # get accounts
            pass
        if choice == 2:
            # prompt from account schema
            pass
        if choice == 3:
            # got to price action
            pass


def priceactionmenu():
    """ This menu has option to get price action data"""
    os.system("clear")
    print("Input a trading pair to get its most recent pair or press (q) to go back to mainmenu")
    pass

def create_account():
    """ Creates account by prompting from account schema and
        submitting data, might need some parameters like session idk.
    """
    pass

def accountmenu():
    """ Option to delete account
        Options to go for orders menu or to positions menu
        Option to go to main menu (log out)
    """
    pass

def positionsmenu():
    """ get positions, give functionality to select one or to go back to accountmenu

    """
    pass

def positionmenu():
    """ Show one position, give functionality to change leverage or to go back to positionsmenu

    """
    pass

def ordersmenu():
    """ Options for adding new order and for selecting one and deleting it or back to account """
    pass

def ordermenu():
    """ Show one order, option to delete it or to go back to ordersmenu  """
    pass

def main():
    mainmenu()
    # vois mahollisesti käyttää ilma sessionia nii ois simppelimpi ehkä, emt
    with requests.Session() as s:
        resp = s.get(API_URL)
        body = resp.json()


if __name__ == '__main__':
    main()
