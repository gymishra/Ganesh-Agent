#!/usr/bin/env python3
"""
Dynamic Manifest File Generator
Creates manifest files in the specified format for S3 buckets
"""

import boto3
import json
import argparse
from datetime import datetime

class ManifestGenerator:
    def __init__(self, region='us-east-1'):
        self.s3_client = boto3.client('s3', region_name=region)
        self.region = region
    
    def get_bucket_objects(self, bucket_name, prefix=''):
        """Get all objects from S3 bucket"""
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
            
            objects = []
            for page in pages:
                if 'Contents' in page:
                    objects.extend(page['Contents'])
            
            return objects
        except Exception as e:
            print(f"Error getting bucket objects: {e}")
            return []
    
    def generate_manifest(self, bucket_name, output_file='manifest.json', 
                         format_type='JSON', delimiter=',', text_qualifier="'", 
                         contains_header='true', additional_prefixes=None):
        """Generate manifest file in the specified format"""
        
        print(f"🔍 Scanning bucket: {bucket_name}")
        objects = self.get_bucket_objects(bucket_name)
        
        if not objects:
            print(f"⚠️ No objects found in bucket {bucket_name}")
            return False
        
        # Generate URIs for all objects
        uris = [f"s3://{bucket_name}/{obj['Key']}" for obj in objects]
        
        # Generate URI prefixes
        uri_prefixes = [f"s3://{bucket_name}/"]
        
        # Add additional prefixes if provided
        if additional_prefixes:
            uri_prefixes.extend(additional_prefixes)
        
        # Create manifest structure
        manifest = {
            "fileLocations": [
                {
                    "URIs": uris
                },
                {
                    "URIPrefixes": uri_prefixes
                }
            ],
            "globalUploadSettings": {
                "format": format_type,
                "delimiter": delimiter,
                "textqualifier": text_qualifier,
                "containsHeader": contains_header
            }
        }
        
        # Write manifest file
        try:
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=4)
            
            print(f"✅ Manifest file created: {output_file}")
            print(f"📊 Objects included: {len(uris)}")
            print(f"📁 URI Prefixes: {len(uri_prefixes)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error writing manifest file: {e}")
            return False
    
    def generate_s3_tables_manifest(self, table_bucket_arn, table_id, source_bucket):
        """Generate manifest specifically for S3 Tables integration"""
        
        # Extract bucket name from ARN
        table_bucket_name = table_bucket_arn.split('/')[-1]
        warehouse_bucket = f"{table_id}-hgyt1by31wbnezdejhddi1uuo6bfquse1b--table-s3"
        
        # Get source bucket objects
        source_objects = self.get_bucket_objects(source_bucket)
        source_uris = [f"s3://{source_bucket}/{obj['Key']}" for obj in source_objects]
        
        # S3 Tables specific prefixes
        s3_tables_prefixes = [
            f"s3://{source_bucket}/",
            f"s3://{warehouse_bucket}/data/",
            f"s3://{warehouse_bucket}/metadata/"
        ]
        
        manifest = {
            "fileLocations": [
                {
                    "URIs": source_uris
                },
                {
                    "URIPrefixes": s3_tables_prefixes
                }
            ],
            "globalUploadSettings": {
                "format": "JSON",
                "delimiter": ",",
                "textqualifier": "'",
                "containsHeader": "true"
            }
        }
        
        output_file = f"s3_tables_manifest_{table_id[:8]}.json"
        
        try:
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=4)
            
            print(f"✅ S3 Tables manifest created: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Error creating S3 Tables manifest: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Generate S3 manifest files')
    parser.add_argument('--bucket', required=True, help='S3 bucket name')
    parser.add_argument('--output', default='manifest.json', help='Output manifest file name')
    parser.add_argument('--format', default='JSON', help='Data format (JSON, CSV, etc.)')
    parser.add_argument('--delimiter', default=',', help='Field delimiter')
    parser.add_argument('--text-qualifier', default="'", help='Text qualifier')
    parser.add_argument('--contains-header', default='true', help='Contains header flag')
    parser.add_argument('--additional-prefixes', nargs='*', help='Additional URI prefixes')
    parser.add_argument('--s3-tables', action='store_true', help='Generate S3 Tables specific manifest')
    parser.add_argument('--table-id', help='S3 Tables table ID')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    
    args = parser.parse_args()
    
    generator = ManifestGenerator(region=args.region)
    
    if args.s3_tables and args.table_id:
        # Generate S3 Tables specific manifest
        table_arn = f"arn:aws:s3tables:{args.region}:953841955037:bucket/aws-s3"
        generator.generate_s3_tables_manifest(table_arn, args.table_id, args.bucket)
    else:
        # Generate standard manifest
        generator.generate_manifest(
            bucket_name=args.bucket,
            output_file=args.output,
            format_type=args.format,
            delimiter=args.delimiter,
            text_qualifier=args.text_qualifier,
            contains_header=args.contains_header,
            additional_prefixes=args.additional_prefixes
        )

if __name__ == "__main__":
    # If run without arguments, generate manifest for your specific case
    if len(__import__('sys').argv) == 1:
        print("🚀 Generating manifest for sapogrndata bucket...")
        generator = ManifestGenerator()
        
        # Generate standard manifest
        generator.generate_manifest(
            bucket_name='sapogrndata',
            output_file='sapogrndata_manifest.json'
        )
        
        # Generate S3 Tables specific manifest
        generator.generate_s3_tables_manifest(
            table_bucket_arn="arn:aws:s3tables:us-east-1:953841955037:bucket/aws-s3",
            table_id="734a81dd-4d68-47af-8081-fb474a486ddd",
            source_bucket="sapogrndata"
        )
    else:
        main()
