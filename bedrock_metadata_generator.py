#!/usr/bin/env python3

import boto3
import json
import re
from datetime import datetime
from typing import Dict, List, Any

class BedrockMetadataGenerator:
    def __init__(self, region='us-east-1'):
        self.bedrock = boto3.client('bedrock-runtime', region_name=region)
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'  # Using Claude 3 Sonnet
        
    def generate_service_metadata(self, service_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for an OData service using Bedrock
        """
        prompt = self._create_service_prompt(service_info)
        
        try:
            response = self._call_bedrock(prompt)
            metadata = self._parse_service_response(response)
            return metadata
        except Exception as e:
            print(f"Error generating metadata for service: {str(e)}")
            return self._create_fallback_metadata(service_info)
    
    def enhance_existing_metadata(self, existing_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance existing metadata with better descriptions using Bedrock
        """
        enhanced_metadata = {}
        
        for service_name, service_data in existing_metadata.items():
            if service_name.startswith('_'):  # Skip metadata fields
                enhanced_metadata[service_name] = service_data
                continue
                
            print(f"Enhancing metadata for {service_name}...")
            
            # Generate enhanced descriptions
            enhanced_service = self._enhance_service_descriptions(service_name, service_data)
            enhanced_metadata[service_name] = enhanced_service
        
        return enhanced_metadata
    
    def _create_service_prompt(self, service_info: Dict[str, Any]) -> str:
        """
        Create a prompt for generating service metadata
        """
        service_name = service_info.get('name', 'UnknownService')
        service_type = service_info.get('type', 'business')
        basic_description = service_info.get('description', '')
        entities = service_info.get('entities', [])
        
        prompt = f"""
You are an expert SAP consultant and business analyst. Generate comprehensive OData service metadata for AI model training.

Service Information:
- Service Name: {service_name}
- Service Type: {service_type}
- Basic Description: {basic_description}
- Known Entities: {', '.join(entities) if entities else 'Not specified'}

Generate a detailed JSON metadata structure with the following requirements:

1. PURPOSE: Write 2-3 sentences describing what this service does in business terms. Include:
   - Main business processes it handles
   - Types of data it manages
   - How it's used in business operations
   - Key stakeholders who would use it

2. ENTITIES: For each entity, provide:
   - Business-focused description (not technical)
   - 5-8 key fields with detailed business descriptions
   - Explain WHY each field is important, not just WHAT it contains

3. USE_CASES: Generate 12-15 realistic user questions, including:
   - Different ways users might ask for the same information
   - Various business scenarios
   - Both simple and complex queries
   - Include synonyms and alternative phrasings

4. Field descriptions should explain:
   - Business purpose and usage
   - When/why the field is populated
   - How it supports business decisions
   - Relationships to business processes

Format as valid JSON. Focus on business language that end users would understand.

Example field description format:
"CustomerID": "Unique customer identifier used for lookups, order references, and linking customer data across all business systems and processes"

Generate the metadata now:
"""
        return prompt
    
    def _enhance_service_descriptions(self, service_name: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance existing service descriptions using Bedrock
        """
        prompt = f"""
You are an expert SAP consultant. Enhance the following OData service metadata to make it more comprehensive and business-focused.

Current Service: {service_name}
Current Metadata: {json.dumps(service_data, indent=2)}

Enhance this metadata by:

1. IMPROVING PURPOSE: Make it more comprehensive and business-focused
2. ENHANCING ENTITY DESCRIPTIONS: Add more business context and usage scenarios
3. ENRICHING FIELD DESCRIPTIONS: Explain business value, usage patterns, and decision support
4. EXPANDING USE CASES: Add more realistic user questions and alternative phrasings
5. ADDING BUSINESS CONTEXT: Include workflow information and business process integration

Requirements:
- Use business language, not technical jargon
- Explain the "why" behind each field and entity
- Include real-world usage scenarios
- Add synonyms and alternative terms users might use
- Focus on business value and decision support

Return the enhanced metadata as valid JSON with the same structure but richer descriptions.
"""
        
        try:
            response = self._call_bedrock(prompt)
            enhanced_data = self._parse_enhancement_response(response, service_data)
            return enhanced_data
        except Exception as e:
            print(f"Error enhancing {service_name}: {str(e)}")
            return service_data
    
    def _call_bedrock(self, prompt: str) -> str:
        """
        Call Bedrock API with the given prompt
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _parse_service_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Bedrock response and extract JSON metadata
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                metadata = json.loads(json_str)
                return metadata
            else:
                # If no JSON found, create structured response
                return self._create_structured_metadata_from_text(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {str(e)}")
            return self._create_structured_metadata_from_text(response)
    
    def _parse_enhancement_response(self, response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse enhancement response and merge with original data
        """
        try:
            enhanced_data = self._parse_service_response(response)
            # Merge with original structure to ensure completeness
            return self._merge_metadata(original_data, enhanced_data)
        except Exception as e:
            print(f"Error parsing enhancement response: {str(e)}")
            return original_data
    
    def _merge_metadata(self, original: Dict[str, Any], enhanced: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge enhanced metadata with original, preserving structure
        """
        result = original.copy()
        
        # Update purpose if enhanced
        if 'purpose' in enhanced and enhanced['purpose']:
            result['purpose'] = enhanced['purpose']
        
        # Update entities
        if 'entities' in enhanced:
            for entity_name, entity_data in enhanced['entities'].items():
                if entity_name in result.get('entities', {}):
                    # Merge entity data
                    result['entities'][entity_name].update(entity_data)
                else:
                    # Add new entity
                    if 'entities' not in result:
                        result['entities'] = {}
                    result['entities'][entity_name] = entity_data
        
        # Update use cases
        if 'use_cases' in enhanced and enhanced['use_cases']:
            result['use_cases'] = enhanced['use_cases']
        
        return result
    
    def _create_structured_metadata_from_text(self, text: str) -> Dict[str, Any]:
        """
        Create structured metadata from text response
        """
        # This is a fallback method to extract information from text
        # In practice, Claude usually returns valid JSON
        return {
            "purpose": "Generated service description",
            "entities": {},
            "use_cases": []
        }
    
    def _create_fallback_metadata(self, service_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create basic metadata when Bedrock call fails
        """
        service_name = service_info.get('name', 'Service')
        return {
            "purpose": f"Manages {service_name.lower()} related data and business processes",
            "entities": {},
            "use_cases": [
                f"get {service_name.lower()} information",
                f"find {service_name.lower()} data",
                f"lookup {service_name.lower()} details"
            ]
        }

class ODataMetadataEnhancer:
    def __init__(self):
        self.generator = BedrockMetadataGenerator()
    
    def enhance_template_metadata(self, template_path: str, output_path: str) -> str:
        """
        Enhance the existing template metadata using Bedrock
        """
        print("🤖 Using Amazon Bedrock to enhance OData metadata...")
        print("=" * 60)
        
        # Load existing template
        try:
            with open(template_path, 'r') as f:
                template_data = json.load(f)
        except Exception as e:
            print(f"Error loading template: {str(e)}")
            return None
        
        # Remove instructions section
        if 'INSTRUCTIONS' in template_data:
            del template_data['INSTRUCTIONS']
        
        # Enhance metadata using Bedrock
        enhanced_metadata = self.generator.enhance_existing_metadata(template_data)
        
        # Add generation metadata
        enhanced_metadata['_metadata'] = {
            'generated_date': datetime.now().isoformat(),
            'generator': 'Amazon Bedrock Claude 3 Sonnet',
            'version': '1.0',
            'description': 'AI-enhanced OData service metadata for intelligent routing'
        }
        
        # Save enhanced metadata
        with open(output_path, 'w') as f:
            json.dump(enhanced_metadata, f, indent=2)
        
        print(f"✅ Enhanced metadata saved to: {output_path}")
        return output_path
    
    def generate_from_scratch(self, services_info: List[Dict[str, Any]], output_path: str) -> str:
        """
        Generate metadata from scratch for multiple services
        """
        print("🤖 Generating OData metadata from scratch using Bedrock...")
        print("=" * 60)
        
        metadata = {}
        
        for service_info in services_info:
            service_name = service_info['name']
            print(f"Generating metadata for {service_name}...")
            
            service_metadata = self.generator.generate_service_metadata(service_info)
            
            # Add OAuth2 configuration
            service_metadata['endpoint'] = service_info.get('endpoint', f"https://sap-system/odata/{service_name}")
            service_metadata['oauth2_config'] = {
                'token_endpoint': service_info.get('token_endpoint', 'https://sap-system/oauth/token'),
                'client_id': service_info.get('client_id', f"{service_name.lower()}-client"),
                'client_secret_arn': f"arn:aws:secretsmanager:us-east-1:account:secret:{service_name.lower()}-secret"
            }
            
            metadata[service_name] = service_metadata
        
        # Add generation metadata
        metadata['_metadata'] = {
            'generated_date': datetime.now().isoformat(),
            'generator': 'Amazon Bedrock Claude 3 Sonnet',
            'version': '1.0',
            'description': 'AI-generated OData service metadata for intelligent routing'
        }
        
        # Save metadata
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Generated metadata saved to: {output_path}")
        return output_path

def main():
    """
    Main function to demonstrate Bedrock metadata enhancement
    """
    enhancer = ODataMetadataEnhancer()
    
    print("🎯 Bedrock OData Metadata Generator")
    print("=" * 60)
    print("Choose an option:")
    print("1. Enhance existing template metadata")
    print("2. Generate metadata from service descriptions")
    print("3. Interactive service definition")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        # Enhance existing template
        template_path = '/home/gyanmis/odata_metadata_template.json'
        output_path = '/home/gyanmis/odata_metadata_bedrock_enhanced.json'
        
        result = enhancer.enhance_template_metadata(template_path, output_path)
        if result:
            print(f"\n🎉 Success! Enhanced metadata saved to: {result}")
            print("\nNext steps:")
            print("1. Review the enhanced metadata")
            print("2. Run: python test_local_model.py")
            print("3. Deploy with: python deploy_odata_training.py")
    
    elif choice == '2':
        # Generate from service descriptions
        services = []
        
        print("\nEnter basic information for your services:")
        num_services = int(input("How many services? (1-5): "))
        
        for i in range(num_services):
            print(f"\nService {i+1}:")
            name = input("Service name: ").strip()
            service_type = input("Service type (customer/sales/product/inventory/finance): ").strip()
            description = input("Brief description: ").strip()
            
            services.append({
                'name': name,
                'type': service_type,
                'description': description
            })
        
        output_path = '/home/gyanmis/odata_metadata_bedrock_generated.json'
        result = enhancer.generate_from_scratch(services, output_path)
        
        if result:
            print(f"\n🎉 Success! Generated metadata saved to: {result}")
    
    elif choice == '3':
        print("\nInteractive mode - coming soon!")
        print("For now, use option 1 or 2.")

if __name__ == "__main__":
    main()
