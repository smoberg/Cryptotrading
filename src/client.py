import json
import requests
import sys, os
import time
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
            inputvalue = input(props["description"] + ":") #
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

def submit_data(s, ctrl, data, headers=None):
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
    # os.system('cls')
    print("\nThis is the main menu of the client application for Cryptotrading API")

    while True:
        try:
            print("\nSelect (1) if you want to use existing account")
            print("Select (2) if you want to make a new account")
            print("Select (3) if you want to get the most recent trade\n")
            choice = int(input("Give your selection please: "))
            if choice == 1:
                select_account()

            if choice == 2:
                create_account()

            if choice == 3:
                priceactionmenu()

        except ValueError:
            pass


def priceactionmenu():
    """ This menu has option to get price action data"""
    os.system("clear")
    print("Input a trading pair to get its most recent pair or press (q) to go back to mainmenu")
    try:
        str = input()
        if str == 'q':
            mainmenu()
        else:
            connected = True
            prev_response = {}
            while(connected == True):
                response = requests.get(API_URL + '/priceaction/', params={"symbol" : str})
                response = json.loads(response.text)

                print("PRICE: {}, SIZE: {}, SIDE: {}".format(response["price"], response["size"], response["side"]))
                time.sleep(2)
    except TypeError:
        print("")

def select_account():
    """
    Selects account to login
    """
    resp = requests.get(API_URL + "/accounts/")
    body = resp.json()
    print("Here is a list of registered accounts:")
    print("\n")
    for account in body["items"]:
        print(account["accountname"] + "\n")

    while True:
        choice = input("Select the account by entering it's name or go back with (q): ")
        for account in body["items"]:

            if choice == account["accountname"]:
                api_secret = input("Please input your account's secret apikey: ")
                accountmenu(API_URL + account["@controls"]["self"]["href"], headers={"api_secret": api_secret})

            if choice == "q":
                mainmenu()


def create_account():
    """ Creates account by prompting from account schema and
        submitting data, might need some parameters like session idk.
    """
    # os.system("cls")
    resp = requests.get(API_URL + "/accounts/")
    body = resp.json()
    postbody = prompt_from_schema(body["@controls"]["add-account"])
    resp = requests.post(API_URL + body["@controls"]["add-account"]["href"],
                         data=json.dumps(postbody),
                         headers={"Content-type": "application/json"})

    if resp.status_code == 201:
        print("Account created, logging in to account")
        location = resp.headers["Location"]
        headers = {"api_secret": postbody["api_secret"]}
        accountmenu(location, headers)

    # print error and call create account again?
    if resp.status_code == 415:
        pass
    if resp.status_code == 400:
        pass
    if resp.status_code == 409:
        body = resp.json()
        print(body["@error"]["@message"])
        print(body["@error"]["@messages"])

def accountmenu(url, headers):
    """ Option to delete account
        Options to go for orders menu or to positions menu
        Option to go to main menu (log out)
    """
    resp = requests.get(url, headers=headers)
    body = resp.json()
    if resp.status_code == 401:
        print(body["@error"]["@message"])
        print(body["@error"]["@messages"])
        mainmenu()

    print("\nSelect (o) if you want go to orders")
    print("Select (p) if you want to positions")
    print("Select (d) if you want to delete the account")
    print("Select (q) if you want to go to main menu\n")

    while True:
        try:
            choice = input("Enter your choice: ")
            choice = choice.lower()
            if choice == "o":
                ordersmenu(body["@controls"]["orders-all"]["href"], headers)
            if choice == "p":
                positionsmenu(body["@controls"]["orders-all"]["href"], headers)
            if choice == "d":
                resp = requests.delete(API_URL + body["@controls"]["delete"]["href"], headers=headers)
                if resp.status_code == 204:
                    print("deletion was successful")
                    mainmenu()
            if choice == "q":
                mainmenu()
        except AttributeError:
            print("not a valid choice")
            pass



def positionsmenu(apikey):
    """ get positions, give functionality to select one or to go back to accountmenu

    """
    os.system("clear")
    response = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/positions/",
                            headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

    positions = response["items"]
    for position in positions:
        if position["leverage"] == 0:
            leverage = "Cross"
        else:
            leverage = position["leverage"]
        print("Symbol: {}, Size {}, Leverage: {}, Entry price: {}, Liquidation price : {}".format(position["symbol"],
                                                                                                    position["size"],
                                                                                                    leverage,
                                                                                                    position["avgEntryPrice"],
                                                                                                    position["liquidationPrice"]))

    print("Select position to modify by entering position symbol or enter(q) to return:")
    str = input()
    if str == 'q':
        mainmenu()
    positionmenu(str, apikey)

    pass

def positionmenu(symbol, apikey):
    """ Show one position, give functionality to change leverage or to go back to positionsmenu

    """
    response = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/positions/" + symbol + "/",
                            headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

    if response["leverage"] == 0:
        leverage = "Cross"
    else:
        leverage = response["leverage"]
    print("Symbol: {}, Size {}, Leverage: {}, Entry price: {}, Liquidation price : {}".format(response["symbol"],
                                                                                                response["size"],
                                                                                                leverage,
                                                                                                response["avgEntryPrice"],
                                                                                                response["liquidationPrice"]))
    print("Input desired leverage for the position:")
    try:
        float_leverage = 0.0
        leverage = input()
        if leverage == 'Cross':
            float_leverage = 0.0
        else:
            float_leverage = float(leverage)

        response = requests.patch(API_URL + "/accounts/" + apikey + "/positions/" + symbol + "/",
                                    headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"},
                                    json={"leverage": float_leverage})

    except ValueError:
        print("Invalid type: leverage must be a float or 'Cross'")

def ordersmenu(url, headers):
    """ Options for adding new order and for selecting one and deleting it or back to account """

    resp = requests.get(API_URL + url, headers=headers)
    body = resp.json()
    print("\nYour Orders:\n")
    if len(body["items"]) > 0:
        for order in body["items"]:
            print("Order ID: {}\nSymbol: {}\nPrice: {}\nSize: {}\nSide: {}\n".format(order["id"],
                                                                                            order["symbol"],
                                                                                            order["price"],
                                                                                            order["size"],
                                                                                            order["side"]))
    while True:
        try:
            print("\nSelect order by entering the order ID, create a new order by entering(c) or enter(q) to return:")

            choice = input("Enter your selection: ")

            if choice == 'q':
                accountmenu(API_URL + body["@controls"]["account"]["href"], headers=headers)

            if choice == 'c':
                createorder(body["@controls"]["add-order"], headers)

            if next((order for order in body["items"] if order['id'] == choice), None) and choice != 'c':
                ordermenu(order["@controls"]["self"]["href"], headers)

            elif str != 'c':
                print("\nInvalid Order ID given\n")

        except AttributeError:
            pass



def ordermenu(url, headers):
    """ Show one order, option to delete it or to go back to ordersmenu  """

    resp = requests.get(API_URL + url, headers=headers)
    body = resp.json()

    print("Symbol: {}\n Price: {}\n Size: {}\n Side: {}\n".format(body["symbol"], body["price"], body["size"], body["side"]))

    print("Enter (d) to delete, or (q) to return:")
    while True:
        str = input("Enter your selection: ")
        if str == 'q':
            ordersmenu(body["@controls"]["orders-all"]["href"], headers)
        if str == 'd':
            resp = requests.delete(API_URL + body["@controls"]["delete"]["href"], headers=headers)
            if resp.status_code == 204:
                print("deletion was successful")
                ordersmenu(body["@controls"]["orders-all"]["href"], headers)

def createorder(ctrl, headers):
    """ creates order """
    postbody = prompt_from_schema(ctrl)
    # print(postbody)
    response = requests.post(API_URL + ctrl["href"], json=postbody, headers=headers)

    if response.status_code == 201:
        print("Order created")
        ordersmenu(ctrl["href"], headers)

    else:
        body = response.json()
        print(body["@error"]["@message"])
        print(body["@error"]["@messages"])
        ordersmenu(ctrl["href"], headers)

def main():
    mainmenu()
    # vois mahollisesti käyttää ilma sessionia nii ois simppelimpi ehkä, emt



if __name__ == '__main__':
    main()
