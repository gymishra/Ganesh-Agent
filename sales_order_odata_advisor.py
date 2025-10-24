#!/usr/bin/env python3

import json
import re
from datetime import datetime

class SalesOrderODataAdvisor:
    """Practical advisor for OData services related to sales order creation"""
    
    def __init__(self):
        self.load_odata_metadata()
        
    def load_odata_metadata(self):
        """Load the OData metadata we have"""
        try:
            with open('/home/gyanmis/odata_metadata_optimized.json', 'r') as f:
                self.metadata = json.load(f)
            print(f"✅ Loaded metadata for {len(self.metadata)} OData services")
        except Exception as e:
            print(f"⚠️ Could not load metadata: {str(e)}")
            self.metadata = {}
    
    def find_sales_order_services(self):
        """Find OData services most relevant for sales order creation"""
        
        print("🔍 Analyzing OData Services for Sales Order Creation")
        print("=" * 60)
        
        # Keywords that indicate sales order relevance
        sales_keywords = [
            'sales', 'order', 'document', 'transaction', 'purchase',
            'quotation', 'contract', 'delivery', 'billing', 'invoice'
        ]
        
        order_keywords = [
            'order', 'document', 'header', 'item', 'line', 'create',
            'process', 'manage', 'workflow'
        ]
        
        customer_keywords = [
            'customer', 'business', 'partner', 'account', 'contact'
        ]
        
        product_keywords = [
            'product', 'material', 'item', 'inventory', 'catalog'
        ]
        
        recommendations = []
        
        for service_name, service_data in self.metadata.items():
            score = 0
            reasons = []
            
            # Check service name
            service_lower = service_name.lower()
            
            # High priority for direct sales/order matches
            if any(keyword in service_lower for keyword in ['sales_order', 'salesorder']):
                score += 10
                reasons.append("Direct sales order service")
            
            # Medium-high priority for sales-related services
            elif any(keyword in service_lower for keyword in sales_keywords):
                score += 7
                reasons.append("Sales-related service")
            
            # Medium priority for order-related services
            elif any(keyword in service_lower for keyword in order_keywords):
                score += 5
                reasons.append("Order management service")
            
            # Lower priority for supporting services
            elif any(keyword in service_lower for keyword in customer_keywords):
                score += 3
                reasons.append("Customer/partner data service")
            
            elif any(keyword in service_lower for keyword in product_keywords):
                score += 3
                reasons.append("Product/material data service")
            
            # Check entities if available
            if isinstance(service_data, dict) and 'entities' in service_data:
                entities = service_data['entities']
                if isinstance(entities, list):
                    for entity in entities:
                        entity_lower = str(entity).lower()
                        if any(keyword in entity_lower for keyword in sales_keywords + order_keywords):
                            score += 2
                            reasons.append(f"Contains relevant entity: {entity}")
                            break
            
            if score > 0:
                recommendations.append({
                    'service': service_name,
                    'score': score,
                    'reasons': reasons,
                    'data': service_data
                })
        
        # Sort by score (highest first)
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations
    
    def display_recommendations(self, recommendations):
        """Display the recommendations in a user-friendly format"""
        
        if not recommendations:
            print("❌ No specific sales order services found in the metadata")
            return
        
        print(f"\n🎯 TOP RECOMMENDATIONS FOR SALES ORDER CREATION")
        print("=" * 70)
        
        # Top recommendations
        top_recommendations = recommendations[:5]
        
        for i, rec in enumerate(top_recommendations, 1):
            service = rec['service']
            score = rec['score']
            reasons = rec['reasons']
            
            print(f"\n{i}. 🏆 {service}")
            print(f"   📊 Relevance Score: {score}/10")
            print(f"   💡 Why recommended:")
            for reason in reasons:
                print(f"      • {reason}")
            
            # Show additional details if available
            if isinstance(rec['data'], dict):
                if 'description' in rec['data']:
                    print(f"   📝 Description: {rec['data']['description']}")
                if 'entities' in rec['data'] and isinstance(rec['data']['entities'], list):
                    entities = rec['data']['entities'][:3]  # Show first 3 entities
                    print(f"   📋 Key Entities: {', '.join(map(str, entities))}")
        
        # Supporting services
        if len(recommendations) > 5:
            print(f"\n🔧 SUPPORTING SERVICES (may be needed for complete sales order process):")
            print("-" * 70)
            
            supporting = recommendations[5:10]  # Next 5
            for rec in supporting:
                service = rec['service']
                score = rec['score']
                main_reason = rec['reasons'][0] if rec['reasons'] else "Supporting service"
                print(f"   • {service} (Score: {score}) - {main_reason}")
    
    def provide_implementation_guidance(self):
        """Provide practical guidance for implementing sales order creation"""
        
        print(f"\n📋 IMPLEMENTATION GUIDANCE FOR SALES ORDER CREATION")
        print("=" * 70)
        
        guidance = [
            {
                'step': '1. Primary Sales Order Service',
                'description': 'Look for API_SALES_ORDER_SRV or similar direct sales order APIs',
                'example': 'POST /sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder'
            },
            {
                'step': '2. Customer/Business Partner Data',
                'description': 'Retrieve customer information for order header',
                'example': 'GET /sap/opu/odata/sap/API_BUSINESS_PARTNER/A_Customer'
            },
            {
                'step': '3. Product/Material Information',
                'description': 'Get product details for order line items',
                'example': 'GET /sap/opu/odata/sap/API_PRODUCT_SRV/A_Product'
            },
            {
                'step': '4. Pricing Information',
                'description': 'Calculate prices and conditions',
                'example': 'GET /sap/opu/odata/sap/API_PRICING_SRV/A_PricingCondition'
            },
            {
                'step': '5. Order Validation',
                'description': 'Validate order before final creation',
                'example': 'POST /sap/opu/odata/sap/API_SALES_ORDER_SRV/ValidateOrder'
            }
        ]
        
        for guide in guidance:
            print(f"\n{guide['step']}:")
            print(f"   📝 {guide['description']}")
            print(f"   💻 Example: {guide['example']}")
    
    def answer_specific_question(self, question):
        """Answer the specific question about sales order OData services"""
        
        print(f"❓ QUESTION: {question}")
        print("=" * 70)
        
        # Find recommendations
        recommendations = self.find_sales_order_services()
        
        if recommendations:
            # Get the top recommendation
            top_service = recommendations[0]
            
            print(f"✅ ANSWER:")
            print(f"   The most relevant OData service for sales order creation is:")
            print(f"   🎯 {top_service['service']}")
            print(f"   📊 Confidence: {top_service['score']}/10")
            print(f"   💡 Reasons: {', '.join(top_service['reasons'])}")
            
            # Show all recommendations
            self.display_recommendations(recommendations)
            
        else:
            print(f"❌ No specific sales order services found in current metadata.")
            print(f"💡 Common SAP OData services for sales orders include:")
            print(f"   • API_SALES_ORDER_SRV - Primary sales order API")
            print(f"   • API_SALES_QUOTATION_SRV - For quotation to order conversion")
            print(f"   • API_CUSTOMER_MASTER_SRV - Customer data")
            print(f"   • API_PRODUCT_SRV - Product information")
        
        # Always provide implementation guidance
        self.provide_implementation_guidance()

def main():
    """Main function"""
    
    print("🚀 Sales Order OData Service Advisor")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    advisor = SalesOrderODataAdvisor()
    
    # Answer the specific question
    question = "Which OData service is useful to create sales order?"
    advisor.answer_specific_question(question)
    
    print(f"\n" + "="*70)
    print("✅ Analysis Complete!")
    print("💡 Use this information to identify the right OData services for your sales order implementation.")

if __name__ == "__main__":
    main()
