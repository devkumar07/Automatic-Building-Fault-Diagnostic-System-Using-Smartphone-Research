import boto3

s3 = boto3.client('s3')
s3.download_file('faultdetect','actual_result.csv', 'client_actual_result.csv')