import io
import uuid
import secrets
from http import HTTPStatus

import boto3
import requests
import pdfplumber
from openai import OpenAI

# This code recipe returns the summary of the provided PDF file.
#
# 1) Files are passed in the input and returned in the output as URLs to 
# object storage services like Amazon S3, Google Cloud Storage, or Azure Blob Storage.
#
# 2) The recipes do not have access to the filesystem, so files need to be stored in 
# memory (ex: io.ByteIO).
#
# 3) ENVIRONMENT VARIABLES cannot be configured in the recipes (yet), so credentials
# need to be defined in the code or passed as input variables.


# OPENAI_API_KEY is a helper variable to store the OpenAI API key
OPENAI_API_KEY = ""

# AWS_S3 is a helper dictionary to store the S3 bucket name and API key
AWS_S3 = {
    "BUCKET_NAME": "",
    "ACCESS_KEY": "",
    "ACCESS_KEY_SECRET": "",
}

# JSON_RESPONSE_HEADERS is a helper dictionary to set the response headers
JSON_RESPONSE_HEADERS = {
    "Content-Type": "application/json",
}

# recipe_response is a helper function to format the response
def recipe_response(statusCode, headers, body):
    return {
        "statusCode": statusCode,
        "headers": headers,
        "body": body
    }

# Download the PDF file from the given URL
def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        return None

# Check if the file is a PDF, I know I know, we could to better than this
# but worst case scenario we will just fail later on the recipe :)
def is_pdf(file_stream):
    file_stream.seek(0)
    header = file_stream.read(5)
    file_stream.seek(0)

    return header == b'%PDF-'

# Extract the text from the PDF
def pdf_to_text(file_stream):
    text = ""

    with pdfplumber.open(file_stream) as pdf:
        n_pages = len(pdf.pages)

        if n_pages > 10:
            raise ValueError("The PDF is too long, the maximum number of pages is 10")

        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

# Summarize the text using OpenAI's GPT-3.5 16k model
def summarize_text(text):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )

    system_prompt = """
    You are a helpful assistant. 
    Your task is to provide a concise and accurate summary of the following text. 
    Please ensure the summary captures the key points, themes, or arguments presented, omitting less critical details and examples. 
    DO NOT INCLUDE ANY EXTRA TEXT THAN THE SUMMARY ITSELF.
    """

    user_prompt = text
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    return response.choices[0].message.content
    

# Store the file in S3
def store_in_s3(file_name, data):
    bucket_name = AWS_S3["BUCKET_NAME"]

    session = boto3.Session(
        aws_access_key_id=AWS_S3["ACCESS_KEY"],
        aws_secret_access_key=AWS_S3["ACCESS_KEY_SECRET"]
    )
    s3 = session.resource('s3')
    s3.Bucket(bucket_name).put_object(Key=file_name, Body=data)

    # Generate the URL to get 'file_name' from 'bucket_name'
    url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
    return url


# main is the entry point for the recipe
def main(event):
    # event is a dictionary with the input data for the recipe
    file_url = event.get("file_url", None)

    # File URL is required, we fail if it is not provided
    if not file_url:
        return recipe_response(
            HTTPStatus.BAD_REQUEST, 
            JSON_RESPONSE_HEADERS, 
            {"error": "file_url is required"},
        )

    # Summary file name is optional, we generate a random name if it is 
    # not provided
    summary_file_name = event.get("summary_file_name", None)

    # Append a random string to the file name to avoid conflicts in S3 bucket
    if summary_file_name:
        summary_file_name = f"{summary_file_name}-{secrets.token_hex(4)}.txt"
    
    # If the file name is not provided, we generate a random name
    if not summary_file_name:
        summary_file_name = f"{uuid.uuid4()}.txt"

    # Main logic of the recipe
    try:
        # Download the file in memory
        pdf_stream = download_pdf(file_url)

        # if it is not a PDF we return an error
        if not is_pdf(pdf_stream):
            return recipe_response(
                HTTPStatus.BAD_REQUEST, 
                JSON_RESPONSE_HEADERS, 
                {"error": "The file is not a PDF"},
            )
        
        # Extract the text from the PDF
        text = pdf_to_text(pdf_stream)

        # Summarize the text
        summary = summarize_text(text)

        # Store the summary in S3
        download_url = store_in_s3(summary_file_name, summary)

        # Return the URL to the summary file
        return recipe_response(
            HTTPStatus.OK, 
            JSON_RESPONSE_HEADERS, 
            {"summary_url": download_url},
        )

    except Exception as e:
        return recipe_response(
            HTTPStatus.INTERNAL_SERVER_ERROR, 
            JSON_RESPONSE_HEADERS, 
            {"error": str(e)},
        )
