import boto3
import botocore.config
from botocore.exceptions import ClientError
import json

def blog_generate_using_bedrock(blogtopic: str) -> str:
    config = botocore.config.Config(read_timeout=300, retries={"max_attempts": 3})
    client = boto3.client("bedrock-runtime", region_name="us-east-1", config=config)

    model_id = "meta.llama3-8b-instruct-v1:0"

    user_message = f"""
    You are an expert blog writer. Write a detailed and engaging blog post about the following topic.
    The blog post should include an engaging introduction, a few main points with explanations,
    and a concluding summary. Ensure the tone is informative and accessible to a general audience.

    Blog Topic: {blogtopic}

    Please write the complete blog post now.
    """

    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]

    try:
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 256, "temperature": 0.7, "topP": 0.9},
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        return response_text

    except (ClientError, Exception) as e:
        error_message = f"ERROR: Can't invoke '{model_id}' for topic '{blogtopic}'. Reason: {e}"
        print(error_message)
        return error_message

def lambda_handler(event, context):
    try:
        if 'body' in event:
            event_body = json.loads(event['body'])
            blog_topic = event_body.get('blog_topic')
        else:
            blog_topic = event.get('blog_topic')

        if not blog_topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing blog_topic in event payload.'})
            }

        print(f"Received request to generate blog for topic: {blog_topic}")
        generated_blog_content = blog_generate_using_bedrock(blog_topic)

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'blog_topic': blog_topic,
                'generated_content': generated_blog_content
            })
        }

    except Exception as e:
        print(f"An unexpected error occurred in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'An internal server error occurred: {str(e)}'})
        }

if __name__ == "__main__":
    print("--- Local Testing using blog_generate_using_bedrock function ---")
    print("Generating blog post about 'The Future of AI in Healthcare'...")
    blog_content = blog_generate_using_bedrock("The Future of AI in Healthcare")
    print("\n--- Generated Blog Post ---\n")
    print(blog_content)
    print("\n---------------------------\n")

    print("\n--- Local Testing using lambda_handler function ---")
    test_event = {
        "blog_topic": "The Ethics of Generative AI"
    }
    mock_context = {}
    lambda_response = lambda_handler(test_event, mock_context)
    print("\n--- Lambda Handler Response (JSON format) ---\n")
    print(json.dumps(lambda_response, indent=2))
    print("\n---------------------------\n")

    test_event_api_gateway = {
        "body": "{\"blog_topic\": \"The Importance of Cybersecurity in the Cloud\"}",
        "headers": {"Content-Type": "application/json"},
        "httpMethod": "POST",
        "isBase64Encoded": False,
        "path": "/generate-blog",
        "queryStringParameters": None,
        "requestContext": {},
        "resource": "/generate-blog",
        "stageVariables": None
    }
    lambda_response_api_gateway = lambda_handler(test_event_api_gateway, mock_context)
    print("\n--- Lambda Handler Response (API Gateway style) ---\n")
    print(json.dumps(lambda_response_api_gateway, indent=2))
    print("\n---------------------------\n")
