#!/usr/bin/env python3
"""
SAP HANA + AWS Bedrock Integration Examples
For GenAI for SAP Curriculum - Module 1 Enhancement

This script demonstrates practical integration between SAP HANA and AWS Bedrock
for the curriculum scenarios we identified in our previous analysis.
"""

import hdbcli.dbapi as hana_db
import boto3
import json
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SAP_HANA_Bedrock_Integration:
    def __init__(self, hana_host="98.83.112.225", hana_instance="02", hana_port=30215):
        """
        Initialize SAP HANA and AWS Bedrock connections
        
        Args:
            hana_host: SAP HANA server IP
            hana_instance: SAP HANA instance number
            hana_port: SAP HANA port (default: 3<instance>15)
        """
        self.hana_host = hana_host
        self.hana_instance = hana_instance
        self.hana_port = hana_port
        self.hana_connection = None
        self.bedrock_client = None
        
    def connect_hana(self, username, password, database="SYSTEMDB"):
        """Connect to SAP HANA database"""
        try:
            self.hana_connection = hana_db.connect(
                address=self.hana_host,
                port=self.hana_port,
                user=username,
                password=password,
                database=database
            )
            logger.info(f"Connected to SAP HANA at {self.hana_host}:{self.hana_port}")
            return True
        except Exception as e:
            logger.error(f"HANA connection failed: {e}")
            return False
    
    def connect_bedrock(self, region="us-east-1"):
        """Initialize AWS Bedrock client"""
        try:
            self.bedrock_client = boto3.client('bedrock-runtime', region_name=region)
            logger.info(f"Connected to AWS Bedrock in {region}")
            return True
        except Exception as e:
            logger.error(f"Bedrock connection failed: {e}")
            return False
    
    def get_sap_business_data(self, table_name="VBAK", limit=100):
        """
        Extract SAP business data for AI analysis
        Example: Sales order headers (VBAK table)
        """
        if not self.hana_connection:
            logger.error("No HANA connection available")
            return None
            
        try:
            cursor = self.hana_connection.cursor()
            query = f"""
            SELECT TOP {limit}
                VBELN as sales_order,
                ERDAT as creation_date,
                AUART as order_type,
                VKORG as sales_org,
                VTWEG as distribution_channel,
                SPART as division,
                NETWR as net_value,
                WAERK as currency
            FROM {table_name}
            WHERE ERDAT >= ADD_DAYS(CURRENT_DATE, -30)
            ORDER BY ERDAT DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to pandas DataFrame for easier processing
            df = pd.DataFrame(results, columns=columns)
            logger.info(f"Retrieved {len(df)} records from {table_name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error querying SAP data: {e}")
            return None
    
    def analyze_with_bedrock(self, data_text, model_id="amazon.nova-pro-v1:0"):
        """
        Send SAP data to AWS Bedrock for AI analysis
        Using Nova Pro model identified in our previous Bedrock inventory
        """
        if not self.bedrock_client:
            logger.error("No Bedrock connection available")
            return None
            
        try:
            prompt = f"""
            Analyze the following SAP business data and provide insights:
            
            {data_text}
            
            Please provide:
            1. Key trends and patterns
            2. Potential business risks or opportunities
            3. Recommendations for process optimization
            4. Data quality observations
            
            Format your response as structured JSON with clear sections.
            """
            
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.1,
                "top_p": 0.9
            })
            
            response = self.bedrock_client.invoke_model(
                body=body,
                modelId=model_id,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            analysis = response_body['content'][0]['text']
            
            logger.info("Successfully analyzed SAP data with Bedrock")
            return analysis
            
        except Exception as e:
            logger.error(f"Bedrock analysis failed: {e}")
            return None
    
    def generate_sap_insights_report(self, table_name="VBAK"):
        """
        Complete workflow: Extract SAP data → Analyze with Bedrock → Generate report
        This demonstrates the integration scenarios from our curriculum enhancement
        """
        logger.info("Starting SAP-Bedrock integration workflow...")
        
        # Step 1: Extract SAP data
        sap_data = self.get_sap_business_data(table_name)
        if sap_data is None or sap_data.empty:
            logger.error("No SAP data retrieved")
            return None
        
        # Step 2: Prepare data summary for AI analysis
        data_summary = f"""
        SAP {table_name} Data Summary:
        - Total Records: {len(sap_data)}
        - Date Range: {sap_data['CREATION_DATE'].min()} to {sap_data['CREATION_DATE'].max()}
        - Total Value: {sap_data['NET_VALUE'].sum():,.2f} {sap_data['CURRENCY'].iloc[0]}
        - Unique Order Types: {sap_data['ORDER_TYPE'].nunique()}
        - Sales Organizations: {sap_data['SALES_ORG'].nunique()}
        
        Sample Records:
        {sap_data.head(10).to_string()}
        
        Statistical Summary:
        {sap_data.describe()}
        """
        
        # Step 3: Analyze with Bedrock
        ai_insights = self.analyze_with_bedrock(data_summary)
        if not ai_insights:
            logger.error("AI analysis failed")
            return None
        
        # Step 4: Generate comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "sap_table": table_name,
            "data_summary": {
                "record_count": len(sap_data),
                "total_value": float(sap_data['NET_VALUE'].sum()),
                "currency": sap_data['CURRENCY'].iloc[0],
                "date_range": {
                    "from": str(sap_data['CREATION_DATE'].min()),
                    "to": str(sap_data['CREATION_DATE'].max())
                }
            },
            "ai_insights": ai_insights,
            "integration_metadata": {
                "hana_host": self.hana_host,
                "hana_instance": self.hana_instance,
                "bedrock_model": "amazon.nova-pro-v1:0",
                "processing_time": datetime.now().isoformat()
            }
        }
        
        return report
    
    def demonstrate_curriculum_scenarios(self):
        """
        Demonstrate the specific SAP-AI integration scenarios from our curriculum
        Based on the visual placeholders we identified in Module 1
        """
        scenarios = []
        
        # Scenario 1: Sales Order Analysis (from our curriculum enhancement)
        logger.info("Scenario 1: SAP Sales Order Intelligence")
        sales_report = self.generate_sap_insights_report("VBAK")
        if sales_report:
            scenarios.append({
                "scenario": "Sales Order Intelligence",
                "description": "AI-powered analysis of SAP sales orders",
                "report": sales_report
            })
        
        # Scenario 2: Customer Master Data Analysis
        logger.info("Scenario 2: Customer Data Intelligence")
        # This would query KNA1 table for customer master data
        
        # Scenario 3: Material Master Analysis
        logger.info("Scenario 3: Material Master Intelligence")
        # This would query MARA table for material master data
        
        return scenarios
    
    def close_connections(self):
        """Clean up database connections"""
        if self.hana_connection:
            self.hana_connection.close()
            logger.info("HANA connection closed")

# Example usage for curriculum demonstration
def main():
    """
    Main function demonstrating SAP HANA + Bedrock integration
    This supports the enhanced curriculum scenarios we developed
    """
    # Initialize integration class
    sap_ai = SAP_HANA_Bedrock_Integration()
    
    try:
        # Connect to SAP HANA (credentials would be provided securely)
        print("Connecting to SAP HANA...")
        # sap_ai.connect_hana("username", "password")
        
        # Connect to AWS Bedrock
        print("Connecting to AWS Bedrock...")
        # sap_ai.connect_bedrock()
        
        # Run curriculum demonstration scenarios
        print("Running SAP-AI integration scenarios...")
        # scenarios = sap_ai.demonstrate_curriculum_scenarios()
        
        print("Integration examples ready for curriculum use!")
        
    except Exception as e:
        logger.error(f"Main execution error: {e}")
    
    finally:
        sap_ai.close_connections()

if __name__ == "__main__":
    main()
