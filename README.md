# Cookbook for the Fewsats Platform

At [Fewsats](fewsats.com) we believe that software unlocks a world of possibilities, and automation is the key that opens this door.Guided by this belief, we are committed to building a platform that simplifies software consumption for everyone: pogrammers, non-coders and even machines.

Our platform stands as a unique ecosystem where developers have the opportunity to upload, share, and monetize their code recipes – turning their coding expertise into a valuable asset. These recipes, encompassing a wide range of functionalities, are made available to users worldwide. They can effortlessly execute these programs, utilizing them for their specific needs.

This repository is designed to provide a comprehensive understanding our platform. In it, you'll find practical examples and step-by-step guides on how to get started with Fewsats.

## How does it work

As a developer your journey begins with what we call a 'code recipe'. A code recipe is a small program o script, crafted to perform specific function with a defined list of inputs and outputs.

You can upload as many code recipes as you desire.  Each uploaded recipe is assigned a unique, static URL. That URL is the gateway for users to trigger the execution of your code recipe. Every recipe undergoes a thorough review process to ensure its safe execution. This review checks for potential risks, even though all recipes run in a sandbox environment. Our goal is to prevent any exposure of user credentials or sensitive data through the inputs of your code recipe.

An integral part of the Fewsats platform is the monetization model for your code recipes.  Each time a user wishes to execute a recipe by hitting its unique URL, a payment is required. To facilitate this, our platform supports an open standard for payments known as [L402](https://github.com/Fewsats/awesome-L402). This protocol is designed to seamlessly integrate financial transactions into the process of executing code recipes.

This means that triggering a code recipe is not limited to just members of the Fewsats platform. Anyone possessing a client that supports L402 payments can execute these recipes.


## Add a new code recipe

** We strongly recommend using the [`fewsatscli`](https://github.com/Fewsats/fewsatscli) tool. **

Currently the only runtime suppoted in our platform is `Python 3.11`.

The following snippet provides an example of a Python code recipe that accepts a single argument, `'name'`. This example includes comprehensive comments to guide you through using the platform effectively. The comments detail everything from how to read the input to the required return format for code recipes

```python
#### main.py

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
```

To upload your code recipe to the platform, you can utilize the `recipes` command within the `fewsatscli` tool. This command streamlines the process of uploading and ensures your recipe is properly integrated into the platform.

```bash
fewsatscli recipes add --path=path/to/main.py \
--name="Hello World" \
--description="hello world example test function"
```

Using the `get` command, you can retrieve the details of your uploaded code recipe. Among various fields, you will find one labeled `verified`', which is set to `false` by default. **A code recipe becomes available for execution by users only after it has successfully passed through our verification process.**

```bash
fewsatscli recipes get ${recipe_id}
```

## Trigger a code recipe execution

** We strongly recommend using the [`fewsatscli`](https://github.com/Fewsats/fewsatscli) tool. **

Once your function has passed the verification process (which you can confirm using the get command), it becomes ready for execution. To trigger the execution of a verified code recipe, you can utilize the `execute` command.

To initiate the execution of a code recipe, two key components are required: the unique ID of the recipe and a wallet capable of processing Lightning Network (LN) invoices. 

Currently, `fewsatscli` only supports the Alby wallet for this purpose. You can create an `ACCESS_TOKEN` for Alby, which is necessary for transactions, by visiting this [link](https://getalby.com/developer/access_tokens/new)

Input parameters can be provided in the format of `"key=value"` pairs using the `--data` flag. 

```
fewsatscli recipes execute --recipe_id af63c99b-87a2-49ff-9539-e675df82042f --data="name=John Doe" --alby_token=$ALBY_ACCESS_TOKEN
```


## Monetization

As of now, the Fewsats platform is in its alpha stage, where our primary focus is on developing and refining the core functionalities. In this phase, monetization features for developers are not yet available. For testing purposes, all code recipes are currently priced at a nominal rate of 1 satoshi (a small fraction of a US cent). It's important to note that during this testing phase, these collected amounts are not passed on to the recipe creators.

We are actively working towards introducing a comprehensive monetization system. In future updates, once login capabilities and user profiles are integrated, developers will have the flexibility to set the cost for each execution of their code recipes. This upcoming feature is aimed at empowering developers with control over their monetization strategies, aligning with our vision of creating a platform that not only simplifies software consumption but also facilitates a fair and rewarding ecosystem for creators.