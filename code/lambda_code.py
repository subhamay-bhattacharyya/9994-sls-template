# # -*- coding: utf-8 -*-
# """
# Created on Wed May 31 09:19:18 2023

# @author: Subhamay Bhattacharyya
# """

import json
import logging
import boto3
import uuid
import os
import random 
import string

# # Load the exceptions for error handling
from botocore.exceptions import ClientError, ParamValidationError
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

dynamodb_client = boto3.client('dynamodb', region_name=os.environ.get("AWS_REGION"))
dynamodb_table = os.getenv("DYNAMODB_TABLE_NAME")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def python_obj_to_dynamo_obj(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def dynamodb_obj_to_python_obj(dynamodb_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    return {
        k: deserializer.deserialize(v)
        for k, v in dynamodb_obj.items()
    }
    
def dynamodb_item_exists(partitionKey):
    try:
        response = dynamodb_client.get_item(
                            TableName=dynamodb_table,
                            Key={
                                'MessageId': {'S': partitionKey}
                            }
                    )

        if not response.get('Item'):
            logger.info(f"The item {dict(MessageId=partitionKey)} does not exist.")
            return False
        else:
            dynamodb_item = dynamodb_obj_to_python_obj(response['Item'])
            logger.info(f"The item {json.dumps(dynamodb_item)} exists.")
            return True

    # An error occurred
    except ParamValidationError as e:
        logger.error(f"Parameter validation error: {e}") 
    except ClientError as e:
        logger.error(f"Client error: {e}")
        
def dynamo_db_put_item(item):

    try:
        response = dynamodb_client.put_item(
            TableName = dynamodb_table,
            Item=python_obj_to_dynamo_obj(item)
            )

        return response
    # An error occurred
    except ParamValidationError as e:
        logger.error(f"Parameter validation error: {e}")
    except ClientError as e:
        logger.error(f"Client error: {e}")
        

def lambda_handler(event, context):
    
    for _ in range(0, random.randint(0,9)):
        random_string_length = 20
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random_string_length))
        logger.info(f"random_string : {random_string}")
        response = dynamodb_item_exists(partitionKey=random_string)
        if not response:
            item = dict(MessageId=random_string, Message = str(uuid.uuid4()))
            logger.info(f"item = {json.dumps(item)}")
            response = dynamo_db_put_item(item)
            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                logger.error(f"Failed to insert item {json.dumps(item)}")
    
    return {
        "statsCode": 200,
        "response": "All items inserted successfully!"
    }
    
