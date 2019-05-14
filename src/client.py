import json
import requests
import sys, os
import time
# URL of the API
API_URL = "http://localhost:5000"

def prompt_from_schema(ctrl):
    """ Function used to get inputs from the user based on the schema
        Based on the function introduced in exercise 4.
        Takes in the Mason control for POST/PATCH request
        Returns valid json body according to schema
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
    """ Helpper function used to convert user input strings to right format.
        Based on the function introduced in exercise 4.
    """
    if schema_props["type"] == "number":
            try:
                value = int(value)
            except ValueError:
                value = float(value)
    if schema_props["type"] == "integer":
        value = int(value)
    return value


def mainmenu():
    """ Main menu of the client, jumps to different menus based on the user input.
    """
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
    """ Menu function for price action data. Asks the user for trading pair
        and queries price action data with that symbol every 2 seconds.
    """
    print("Input a trading pair to get its most recent pair or press (q) to go back to mainmenu:")

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
        print("not a valid symbol")

def select_account():
    """
    Shows user the accounts registered to the API. User has option to login to account
    or go back to main menu.
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
    """ Creates account by using prompt from schema function and
        submits the data. After creating an account logins to that account.
        If creation fails. Goes back to mainmenu
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
    """ Takes in URL for the account resource and headers containing
        the api_secret that user has submitted. Has options to go to orders,
        positions, main menu and to delete the account.
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
                positionsmenu(body["@controls"]["positions-all"]["href"], headers)
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



def positionsmenu(url, headers):
    """ Takes in url for the resouce and the headers containing api_secret.
        Shows the active positions to the user. Gives option to select a position
        or go back to main menu.

    """
    response = requests.get(API_URL + url, headers=headers)
    body = response.json()

    print("\nYour Positions:\n")
    if len(body["items"]) > 0:
        for position in body["items"]:
            # print(position)
            if position["leverage"] == 0:
                leverage = "Cross"
            else:
                leverage = position["leverage"]
            print("\nSymbol: {}\nSize {}\nLeverage: {}\nEntry price: {}\nLiquidation price: {}".format(position["symbol"],
                                                                                                        position["size"],
                                                                                                        leverage,
                                                                                                        position["avgEntryPrice"],
                                                                                                        position["liquidationPrice"]))
    while True:
        try:
            print("\nSelect position to modify by entering position symbol or enter(q) to return:")
            choice = input("Enter your selection: ")
            if choice == 'q':
                accountmenu(API_URL + body["@controls"]["account"]["href"], headers)
            else:
                for position in body["items"]:
                    if position["symbol"] == choice:
                        positionmenu(position["@controls"]["self"]["href"], headers)

        except AttributeError:
            print("\nInvalid Selection\n")
            pass

def positionmenu(url, headers):
    """ Takes in url for the resouce and the headers containing api_secret.
        Shows selected position to user and has the option to edit the leverage
        or go back to accountmenu. Body for leverage change is generated with prompt_from_schema
        upon successful editing goes back to positionsmenu, else prints the error message

    """
    response = requests.get(API_URL + url, headers=headers)
    body = response.json()

    if body["leverage"] == 0:
        leverage = "Cross"
    else:
        leverage = body["leverage"]
    print("\nSelected position:\n")
    print("Symbol: {}\nSize {}\nLeverage: {}\nEntry price: {}\nLiquidation price: {}\n".format(body["symbol"],
                                                                                                body["size"],
                                                                                                leverage,
                                                                                                body["avgEntryPrice"],
                                                                                                body["liquidationPrice"]))
    print("Change leverage of the position with (c) or go back with (q)")
    while True:
        try:

            leverage = input("Enter your selection: ")
            if leverage == "q":
                positionsmenu(body["@controls"]["positions-all"]["href"], headers)

            if leverage == "c":
                postbody = prompt_from_schema(body["@controls"]["edit"])
                response = requests.patch(API_URL + url, json=postbody, headers=headers)

                if response.status_code == 204:
                    print("Leverage change successful\n")
                    positionsmenu(body["@controls"]["positions-all"]["href"], headers)
                else:
                    body = response.json()
                    print(body["@error"]["@message"])
                    print(body["@error"]["@messages"])
            else:
                print("Invalid selection\n")
        except AttributeError:
            print("Invalid selection\n")
            pass

def ordersmenu(url, headers):
    """ Takes in url for the resouce and the headers containing api_secret.
        Shows the user their active orders. Has option to create new order,
        select existing order or to go back to accountmenu.

    """

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

            else:
                for order in body["items"]:
                    if choice == order["id"]:
                        ordermenu(order["@controls"]["self"]["href"], headers)

        except AttributeError:
            print("\nInvalid Order ID given\n")
            pass



def ordermenu(url, headers):
    """  Takes in url for the resouce and the headers containing api_secret.
         Shows the selected order and gives option to delete it or to go back
         to ordersmenu. Upon succesful deletion goes back to ordersmenu

    """

    resp = requests.get(API_URL + url, headers=headers)
    body = resp.json()

    print("\nOrder ID: {}\nSymbol: {}\nPrice: {}\nSize: {}\nSide: {}\n".format(body["id"], body["symbol"], body["price"], body["size"], body["side"]))

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
    """ Takes in url for the resouce and the headers containing api_secret.
        Creates valid order body using prompt_from_schema and posts the body.
        Upon succesful creation, goes back to ordersmenu. Upon unsuccesful creation,
        prints error messages and goes back to ordersmenu.
    """
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




if __name__ == '__main__':
    main()
