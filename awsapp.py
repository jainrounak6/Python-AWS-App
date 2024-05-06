import os
from flask import Flask, jsonify, request
import boto3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set AWS credentials and region from environment variables
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID' )
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY' )
AWS_REGION = os.environ.get('AWS_REGION')  # Default to us-east-1 if not specified

@app.route('/account-details')
def get_account_details():
    # Initialize Boto3 client
    client = boto3.client('sts',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_REGION)

    # Fetch account details
    account_id = client.get_caller_identity()['Account']

    return jsonify({'account_id': account_id, 'region': AWS_REGION})

@app.route('/ec2-instances')
def list_ec2_instances():
    # Initialize Boto3 client
    ec2_client = boto3.client('ec2',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name=AWS_REGION)

    # List EC2 instances
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance)

    # # For specific details
    # for reservation in response['Reservations']:
    #     for instance in reservation['Instances']:
    #         instance_id  = instance.get('InstanceId', 'N/A')
    #         instance_type = instance.get('InstanceType', 'N/A')
    #         state = instance.get('State', {}).get('Name', 'N/A')
    #         public_ip = instance.get('PublicIpAddress', 'N/A')
    #         instances.append({'InstanceId': instance_id, 'InstanceType': instance_type, 'State': state, 'PublicIpAddress': public_ip})

    return jsonify({'instances': instances})

@app.route('/ec2-operation', methods=['POST'])
def perform_ec2_operation():
    instance_id = request.json.get('instance_id')
    operation = request.json.get('operation')

    # Initialize Boto3 client
    ec2_client = boto3.client('ec2',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name=AWS_REGION)

    if operation == 'start':
        ec2_client.start_instances(InstanceIds=[instance_id])
    elif operation == 'stop':
        ec2_client.stop_instances(InstanceIds=[instance_id])
    elif operation == 'terminate':
        ec2_client.terminate_instances(InstanceIds=[instance_id])

    return jsonify({'success': True})

@app.route('/s3-buckets')
def list_s3_buckets():
    # Initialize Boto3 client
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_REGION)

    # List S3 buckets
    response = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]

    return jsonify({'buckets': buckets})

@app.route('/s3-bucket-policy')
def get_s3_bucket_policy():
    bucket_name = request.args.get('bucket_name')

    # Initialize Boto3 client
    s3_client = boto3.client('s3',
                             aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_REGION)

    # Get bucket policy
    try:
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = response['Policy']
    except s3_client.exceptions.NoSuchBucketPolicy:
        policy = 'No bucket policy found'

    return jsonify({'bucket_name': bucket_name, 'policy': policy})

if __name__ == '__main__':
    app.run(debug=True)
