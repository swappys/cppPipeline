import logging
import boto3
from botocore.exceptions import ClientError

''' a simple class to demonstrate how to publish messages using the SNS service'''

class Publisher:
    

    '''
        SNS demo: application-to-application communication
        
         publish a message to a given SNS topic
        
        :param my_message: the message to be sent
        :param mobile: the phone number to which you want to deliver an SMS message.
    '''
    def publish_message(self, topic_name, my_message):
        
        try:
           sns_client = boto3.client('sns',region_name='us-east-1')
           print('\npublishing the message {} to the SNS topic {}...\n'.format(my_message, topic_name))
           # recall that if the topic already exists, the create_topic() method returns that topic's ARN
           response = sns_client.create_topic(Name=topic_name)
           topic_arn = response['TopicArn']
           
           response = sns_client.publish(TopicArn=topic_arn, Message=my_message)    
           print(response)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True
        
        
    '''
        SNS demo: application-to-person communication
        
        send an SMS message to a given mobile
        
        :param my_message: the message to be sent
        :param mobile: the phone number to which you want to deliver an SMS message.
    '''
    def send_SMS_message(self, mobile, my_message):
        
        try:
            sns_client = boto3.client('sns',region_name='us-east-1')
            print('\ndelivering the message {} to {}...\n'.format(my_message, mobile))
            # use the method publish() of the SNS Client API to deliver a message to a specified phone
            sns_client.publish(PhoneNumber=mobile, Message=my_message)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True
        
        
