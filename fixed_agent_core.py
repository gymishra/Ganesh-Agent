import boto3
from bedrock_agentcore_starter_toolkit import Runtime

# Fix 1: Explicit region setting
boto_session = boto3.Session()
region = boto_session.region_name or 'us-east-1'  # Default fallback

# Fix 2: Initialize runtime with proper error handling
try:
    agentcore_runtime = Runtime()
    agent_name = "strands_claude_getting_started"
    
    response = agentcore_runtime.configure(
        entrypoint="strands_claude.py",
        auto_create_execution_role=True,
        auto_create_ecr=True,
        requirements_file="requirements.txt",
        region=region,
        agent_name=agent_name
    )
    print("Configuration successful:", response)
    
except Exception as e:
    print(f"Error: {e}")
    # Common fixes:
    # 1. Install: pip install bedrock-agentcore-starter-toolkit
    # 2. Check AWS credentials: aws configure
    # 3. Ensure files exist: strands_claude.py, requirements.txt
