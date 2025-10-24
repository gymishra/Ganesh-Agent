import json

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        passkey = body.get('passkey')
        
        if passkey == '2025':
            message = "Welcome Sir, How are you. How can I help you ?"
        else:
            message = "Please say your Passkey."
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': message})
        }
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Please say your Passkey.'})
        }
