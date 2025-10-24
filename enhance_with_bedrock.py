#!/usr/bin/env python3

import boto3
import json
from bedrock_metadata_generator import ODataMetadataEnhancer

def test_bedrock_access():
    """
    Test if Bedrock is accessible and Claude model is available
    """
    print("🔍 Testing Amazon Bedrock access...")
    
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Test with a simple prompt
        test_prompt = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Can you help me generate OData metadata descriptions?"
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps(test_prompt)
        )
        
        response_body = json.loads(response['body'].read())
        print("✅ Bedrock access successful!")
        print(f"Claude response: {response_body['content'][0]['text'][:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock access failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure you have AWS credentials configured")
        print("2. Check if Claude 3 Sonnet is available in your region")
        print("3. Verify IAM permissions for Bedrock")
        return False

def enhance_existing_template():
    """
    Enhance the existing OData template using Bedrock
    """
    print("\n🤖 Enhancing OData metadata with Bedrock...")
    
    enhancer = ODataMetadataEnhancer()
    
    template_path = '/home/gyanmis/odata_metadata_template.json'
    output_path = '/home/gyanmis/odata_metadata_bedrock_enhanced.json'
    
    try:
        result = enhancer.enhance_template_metadata(template_path, output_path)
        
        if result:
            print(f"\n🎉 Success! Enhanced metadata created!")
            print(f"File: {result}")
            
            # Show a preview of the enhanced metadata
            with open(result, 'r') as f:
                enhanced_data = json.load(f)
            
            print("\n📋 Preview of Enhanced Metadata:")
            print("=" * 50)
            
            for service_name, service_data in enhanced_data.items():
                if service_name.startswith('_'):
                    continue
                    
                print(f"\n🔧 {service_name}")
                print(f"Purpose: {service_data.get('purpose', 'N/A')[:100]}...")
                print(f"Entities: {len(service_data.get('entities', {}))}")
                print(f"Use Cases: {len(service_data.get('use_cases', []))}")
            
            return result
        else:
            print("❌ Enhancement failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during enhancement: {str(e)}")
        return None

def generate_from_descriptions():
    """
    Generate metadata from simple service descriptions
    """
    print("\n🚀 Generate metadata from service descriptions...")
    
    # Example service descriptions
    services = [
        {
            'name': 'CustomerMasterService',
            'type': 'customer',
            'description': 'Manages customer information, contact details, and business relationships',
            'endpoint': 'https://sap-system/odata/CustomerMasterService'
        },
        {
            'name': 'SalesOrderService', 
            'type': 'sales',
            'description': 'Handles sales orders, order tracking, and fulfillment processes',
            'endpoint': 'https://sap-system/odata/SalesOrderService'
        },
        {
            'name': 'ProductCatalogService',
            'type': 'product',
            'description': 'Manages product information, inventory levels, and pricing',
            'endpoint': 'https://sap-system/odata/ProductCatalogService'
        }
    ]
    
    enhancer = ODataMetadataEnhancer()
    output_path = '/home/gyanmis/odata_metadata_bedrock_generated.json'
    
    try:
        result = enhancer.generate_from_scratch(services, output_path)
        
        if result:
            print(f"\n🎉 Success! Generated metadata created!")
            print(f"File: {result}")
            return result
        else:
            print("❌ Generation failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        return None

def main():
    print("🤖 Bedrock OData Metadata Enhancement Tool")
    print("=" * 60)
    
    # Test Bedrock access first
    if not test_bedrock_access():
        print("\n⚠️  Cannot proceed without Bedrock access.")
        print("Please configure AWS credentials and try again.")
        return
    
    print("\nChoose enhancement method:")
    print("1. Enhance existing template (recommended)")
    print("2. Generate from service descriptions")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        result = enhance_existing_template()
        if result:
            print(f"\n✅ Next steps:")
            print(f"1. Review: {result}")
            print("2. Test: python test_local_model.py")
            print("3. Deploy: python deploy_odata_training.py")
    
    elif choice == '2':
        result = generate_from_descriptions()
        if result:
            print(f"\n✅ Next steps:")
            print(f"1. Review: {result}")
            print("2. Test: python test_local_model.py")
    
    elif choice == '3':
        print("\n🔄 Running both enhancement methods...")
        
        # Enhance template
        enhanced_result = enhance_existing_template()
        
        # Generate from scratch
        generated_result = generate_from_descriptions()
        
        if enhanced_result and generated_result:
            print(f"\n🎉 Both methods completed successfully!")
            print(f"Enhanced template: {enhanced_result}")
            print(f"Generated metadata: {generated_result}")
            print("\nCompare both files and choose the best one for your needs.")
    
    else:
        print("Invalid choice. Please run again.")

if __name__ == "__main__":
    main()
