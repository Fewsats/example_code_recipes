# main is the entry point for the recipe
def main(event):
    # event is the input to the recipe
    # event is a dictionary with the input data for the recipe

    # default values can be set using the get method
    # here we will get the value of the key "name" and if it doesn't exist, we will use "satoshi"
    name = event.get("name", "satoshi")

    message = "Hello " + name + "!"

    # statusCode is the status code of the response that the recipe will return
    statusCode = 200

    # headers is a dictionary with the headers of the response that the recipe will return
    headers = {
        "Content-Type": "application/json",
    }


    return { 
        "statusCode": statusCode,
        "headers": headers,

        # The rest of the keys in the dictionary will be the body of the response
        "body": {
            "greetings": message,
        }
    }
