#!/usr/bin/env python3
"""
Query VBAK (Sales Document Header) table record count
Database: 98.83.112.225:30215 (Instance 02)
User: system / Password: Dilkyakare1234
"""

import hdbcli.dbapi as hana_db
import sys

def query_vbak_records():
    """Query VBAK table to get total record count and sample data"""
    
    host = "98.83.112.225"
    port = 30215
    username = "system"
    password = "Dilkyakare1234"
    
    connection = None
    
    try:
        print("🔌 Connecting to SAP HANA...")
        print(f"   Host: {host}:{port}")
        print(f"   User: {username}")
        
        # Establish connection
        connection = hana_db.connect(
            address=host,
            port=port,
            user=username,
            password=password
        )
        
        print("✅ Connection successful!")
        
        cursor = connection.cursor()
        
        # Get current timestamp
        cursor.execute("SELECT CURRENT_TIMESTAMP FROM DUMMY")
        current_time = cursor.fetchone()[0]
        print(f"   Server Time: {current_time}")
        
        print("\n📊 Querying VBAK (Sales Document Header) table...")
        
        # Query 1: Get total record count
        try:
            cursor.execute("SELECT COUNT(*) FROM SAPHANADB.VBAK")
            total_count = cursor.fetchone()[0]
            print(f"✅ Total records in SAPHANADB.VBAK: {total_count:,}")
        except Exception as e:
            print(f"❌ Error getting total count: {e}")
            return False
        
        # Query 2: Get table structure
        try:
            print(f"\n📋 VBAK Table Structure:")
            cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE_NAME, LENGTH, IS_NULLABLE
            FROM TABLE_COLUMNS 
            WHERE SCHEMA_NAME = 'SAPHANADB' AND TABLE_NAME = 'VBAK'
            ORDER BY POSITION
            """)
            
            columns = cursor.fetchall()
            if columns:
                print("-" * 80)
                print(f"{'COLUMN_NAME':<20} {'DATA_TYPE':<15} {'LENGTH':<10} {'NULLABLE':<10}")
                print("-" * 80)
                for col_name, data_type, length, nullable in columns:
                    length_str = str(length) if length else 'N/A'
                    nullable_str = 'YES' if nullable == 'TRUE' else 'NO'
                    print(f"{col_name:<20} {data_type:<15} {length_str:<10} {nullable_str:<10}")
            else:
                print("No column information available")
                
        except Exception as e:
            print(f"❌ Error getting table structure: {e}")
        
        # Query 3: Get sample records (first 5)
        try:
            print(f"\n📝 Sample VBAK Records (first 5):")
            cursor.execute("""
            SELECT TOP 5
                VBELN,
                ERDAT,
                ERZET,
                ERNAM,
                ANGDT,
                BNDDT,
                AUDAT,
                VBTYP,
                TRVOG,
                AUART,
                AUGRU,
                GWLDT,
                SUBMI,
                LIFSK,
                FAKSK,
                NETWR,
                WAERK,
                VKORG,
                VTWEG,
                SPART,
                VKGRP,
                VKBUR,
                GSBER,
                GSKST,
                GUEBG,
                GUEEN,
                KNUMV,
                VDATU,
                VPRGR,
                KALSM,
                VSBED,
                FKARA,
                AWAHR,
                BSTNK,
                BSTDK,
                BSARK,
                BEDAT,
                KUNNR,
                STAFO,
                STWAE,
                AEDAT,
                KVGR1,
                KVGR2,
                KVGR3,
                KVGR4,
                KVGR5,
                KNKLI,
                GRUPP,
                SBGRP,
                CTLPC,
                CMWAE,
                HITYP_PR,
                ABRVW,
                ABDIS,
                VGBEL,
                OBJNR,
                BUKRS_VF,
                TAXK1,
                TAXK2,
                TAXK3,
                TAXK4,
                TAXK5,
                TAXK6,
                TAXK7,
                TAXK8,
                TAXK9,
                XBLNR,
                ZUONR,
                STCEG_L,
                LANDTX,
                HANDLE,
                PROLI,
                CONT_DG,
                UPD_TMSTMP,
                STCEG_H
            FROM SAPHANADB.VBAK
            ORDER BY VBELN
            """)
            
            sample_records = cursor.fetchall()
            if sample_records:
                print("-" * 120)
                print(f"{'VBELN':<12} {'ERDAT':<10} {'AUART':<8} {'NETWR':<15} {'WAERK':<5} {'VKORG':<6} {'KUNNR':<12}")
                print("-" * 120)
                
                for record in sample_records:
                    vbeln = record[0] if record[0] else 'N/A'
                    erdat = str(record[1]) if record[1] else 'N/A'
                    auart = record[9] if record[9] else 'N/A'
                    netwr = f"{record[15]:,.2f}" if record[15] else '0.00'
                    waerk = record[16] if record[16] else 'N/A'
                    vkorg = record[17] if record[17] else 'N/A'
                    kunnr = record[37] if record[37] else 'N/A'
                    
                    print(f"{vbeln:<12} {erdat:<10} {auart:<8} {netwr:<15} {waerk:<5} {vkorg:<6} {kunnr:<12}")
            else:
                print("No sample records found")
                
        except Exception as e:
            print(f"❌ Error getting sample records: {e}")
        
        # Query 4: Get summary statistics
        try:
            print(f"\n📈 VBAK Summary Statistics:")
            cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT AUART) as unique_order_types,
                COUNT(DISTINCT VKORG) as unique_sales_orgs,
                COUNT(DISTINCT KUNNR) as unique_customers,
                COUNT(DISTINCT WAERK) as unique_currencies,
                MIN(ERDAT) as earliest_date,
                MAX(ERDAT) as latest_date,
                SUM(NETWR) as total_net_value,
                AVG(NETWR) as avg_net_value,
                MAX(NETWR) as max_net_value
            FROM SAPHANADB.VBAK
            WHERE NETWR IS NOT NULL
            """)
            
            stats = cursor.fetchone()
            if stats:
                print("-" * 60)
                print(f"Total Records:        {stats[0]:,}")
                print(f"Unique Order Types:   {stats[1]:,}")
                print(f"Unique Sales Orgs:    {stats[2]:,}")
                print(f"Unique Customers:     {stats[3]:,}")
                print(f"Unique Currencies:    {stats[4]:,}")
                print(f"Date Range:           {stats[5]} to {stats[6]}")
                print(f"Total Net Value:      {stats[7]:,.2f}" if stats[7] else "Total Net Value:      N/A")
                print(f"Average Net Value:    {stats[8]:,.2f}" if stats[8] else "Average Net Value:    N/A")
                print(f"Maximum Net Value:    {stats[9]:,.2f}" if stats[9] else "Maximum Net Value:    N/A")
            else:
                print("No statistics available")
                
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    finally:
        if connection:
            connection.close()
            print(f"\n🔌 Connection closed")
    
    return True

if __name__ == "__main__":
    print("SAP HANA VBAK Table Analysis")
    print("=" * 60)
    query_vbak_records()
