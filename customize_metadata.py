#!/usr/bin/env python3

import json
import os
from datetime import datetime

class ODataMetadataCustomizer:
    def __init__(self):
        self.services = {}
        self.template_path = '/home/gyanmis/odata_metadata_template.json'
        self.output_path = '/home/gyanmis/odata_metadata_custom.json'
    
    def welcome(self):
        print("🎯 OData Service Metadata Customization Tool")
        print("=" * 60)
        print("This tool will help you create accurate metadata for your SAP OData services.")
        print("The better your descriptions, the more accurate your AI model will be!")
        print()
        
    def get_service_info(self, service_num):
        print(f"\\n📋 Service {service_num} Configuration")
        print("-" * 40)
        
        service_name = input("Service Name (e.g., CustomerService, SalesOrderService): ").strip()
        if not service_name:
            service_name = f"Service{service_num}"
        
        endpoint = input("OData Endpoint URL: ").strip()
        if not endpoint:
            endpoint = f"https://your-sap-system/odata/{service_name}"
        
        token_endpoint = input("OAuth2 Token Endpoint: ").strip()
        if not token_endpoint:
            token_endpoint = "https://your-sap-system/oauth/token"
        
        client_id = input("OAuth2 Client ID: ").strip()
        if not client_id:
            client_id = f"{service_name.lower()}-client"
        
        print("\\n📝 Business Purpose")
        print("Describe what this service does in 2-3 sentences.")
        print("Include all major business processes it handles.")
        print("Use terms your end users would understand.")
        print()
        
        purpose = input("Business Purpose: ").strip()
        if not purpose:
            purpose = f"Manages {service_name.lower()} related data and business processes"
        
        return {
            'name': service_name,
            'endpoint': endpoint,
            'oauth2_config': {
                'token_endpoint': token_endpoint,
                'client_id': client_id,
                'client_secret_arn': f"arn:aws:secretsmanager:us-east-1:account:secret:{service_name.lower()}-secret"
            },
            'purpose': purpose,
            'entities': {},
            'use_cases': []
        }
    
    def get_entities(self, service_name):
        print(f"\\n🏗️ Entities for {service_name}")
        print("-" * 40)
        print("List the main entities (tables/objects) this service exposes.")
        print("Examples: Customer, SalesOrder, Product, etc.")
        print()
        
        entities = {}
        entity_count = 1
        
        while True:
            entity_name = input(f"Entity {entity_count} name (or 'done' to finish): ").strip()
            if entity_name.lower() == 'done' or not entity_name:
                break
            
            print(f"\\nDescribe the {entity_name} entity:")
            print("What business information does it contain?")
            print("How is it used in business processes?")
            
            entity_desc = input(f"{entity_name} description: ").strip()
            if not entity_desc:
                entity_desc = f"{entity_name} entity containing business data"
            
            # Get fields for this entity
            fields = self.get_fields(entity_name)
            
            entities[entity_name] = {
                'description': entity_desc,
                'fields': fields
            }
            
            entity_count += 1
            
            if entity_count > 5:  # Limit to prevent too many entities
                print("\\n⚠️  Maximum 5 entities per service for initial setup.")
                break
        
        return entities
    
    def get_fields(self, entity_name):
        print(f"\\n📊 Key Fields for {entity_name}")
        print("-" * 30)
        print("List 3-6 most important fields for this entity.")
        print("Describe each field in business terms, not technical terms.")
        print()
        
        fields = {}
        field_count = 1
        
        while field_count <= 6:
            field_name = input(f"Field {field_count} name (or 'done' to finish): ").strip()
            if field_name.lower() == 'done' or not field_name:
                break
            
            print(f"Describe {field_name}:")
            print("- What business information does it contain?")
            print("- When/why is it used?")
            print("- What business decisions does it support?")
            
            field_desc = input(f"{field_name} description: ").strip()
            if not field_desc:
                field_desc = f"{field_name} field containing business data"
            
            fields[field_name] = field_desc
            field_count += 1
        
        return fields
    
    def get_use_cases(self, service_name):
        print(f"\\n💬 Use Cases for {service_name}")
        print("-" * 40)
        print("How would users naturally ask for data from this service?")
        print("Think about real questions you've heard from business users.")
        print("Examples:")
        print("- 'What is the credit limit for customer ABC?'")
        print("- 'Show me recent sales orders'")
        print("- 'Check product inventory levels'")
        print()
        
        use_cases = []
        case_count = 1
        
        while case_count <= 10:
            use_case = input(f"Use case {case_count} (or 'done' to finish): ").strip()
            if use_case.lower() == 'done' or not use_case:
                break
            
            use_cases.append(use_case)
            case_count += 1
        
        return use_cases
    
    def review_service(self, service_data):
        print("\\n📋 Service Review")
        print("=" * 50)
        print(f"Service Name: {service_data['name']}")
        print(f"Endpoint: {service_data['endpoint']}")
        print(f"Purpose: {service_data['purpose']}")
        print(f"Entities: {len(service_data['entities'])}")
        print(f"Use Cases: {len(service_data['use_cases'])}")
        print()
        
        for entity_name, entity_info in service_data['entities'].items():
            print(f"  📊 {entity_name}: {len(entity_info['fields'])} fields")
        
        print("\\nUse Cases:")
        for i, use_case in enumerate(service_data['use_cases'], 1):
            print(f"  {i}. {use_case}")
        
        confirm = input("\\nLooks good? (y/n): ").strip().lower()
        return confirm == 'y' or confirm == 'yes'
    
    def save_metadata(self):
        print("\\n💾 Saving Metadata")
        print("-" * 30)
        
        # Create final metadata structure
        metadata = {}
        for service_name, service_data in self.services.items():
            metadata[service_name] = {
                'endpoint': service_data['endpoint'],
                'oauth2_config': service_data['oauth2_config'],
                'purpose': service_data['purpose'],
                'entities': service_data['entities'],
                'use_cases': service_data['use_cases']
            }
        
        # Add metadata info
        metadata['_metadata'] = {
            'created_date': datetime.now().isoformat(),
            'version': '1.0',
            'description': 'Custom OData service metadata for AI model training'
        }
        
        # Save to file
        with open(self.output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Metadata saved to: {self.output_path}")
        return self.output_path
    
    def run(self):
        self.welcome()
        
        # Ask how many services
        while True:
            try:
                num_services = int(input("How many OData services do you want to configure? (1-5): "))
                if 1 <= num_services <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Configure each service
        for i in range(1, num_services + 1):
            print(f"\\n🔧 Configuring Service {i} of {num_services}")
            print("=" * 60)
            
            # Get basic service info
            service_info = self.get_service_info(i)
            
            # Get entities
            service_info['entities'] = self.get_entities(service_info['name'])
            
            # Get use cases
            service_info['use_cases'] = self.get_use_cases(service_info['name'])
            
            # Review and confirm
            while not self.review_service(service_info):
                print("\\nLet's revise this service...")
                # Could add revision logic here
                break
            
            self.services[service_info['name']] = service_info
        
        # Save metadata
        output_file = self.save_metadata()
        
        print("\\n🎉 Configuration Complete!")
        print("=" * 60)
        print(f"Your custom metadata has been saved to: {output_file}")
        print("\\nNext steps:")
        print("1. Review the generated file")
        print("2. Run: python test_local_model.py")
        print("3. If satisfied, run: python deploy_odata_training.py")
        
        return output_file

def main():
    customizer = ODataMetadataCustomizer()
    customizer.run()

if __name__ == "__main__":
    main()
