# SAP OData OAuth2 Filter Testing Results

**System:** https://vhcals4hci.awspoc.club  
**Generated:** 2025-08-09 23:49:41

## Test Results


### AuthenticationMode OAuth2

**Status:** error  
**Error:** {"error":{"code":"005056A509B11EE1B9A8FEA8DE87F78E","message":{"lang":"en","value":"Property AuthenticationMode not found in type Service"},"innererror":{"transactionid":"C83CB3D2A1420080E00689503E02B  
**Status Code:** 400

### AuthenticationMode oauth2 (lowercase)

**Status:** error  
**Error:** {"error":{"code":"005056A509B11EE1B9A8FEA8DE87F78E","message":{"lang":"en","value":"Property AuthenticationMode not found in type Service"},"innererror":{"transactionid":"C83CB3D2A1420080E00689503E02B  
**Status Code:** 400

### Contains OAuth

**Status:** error  
**Error:** {"error":{"code":"005056A509B11EE1B9A8FEA8DE87F78E","message":{"lang":"en","value":"Property AuthenticationMode not found in type Service"},"innererror":{"transactionid":"C83CB3D2A1420080E00689503E02B  
**Status Code:** 400

### Security Method OAuth2

**Status:** error  
**Error:** {"error":{"code":"005056A509B11EE1B9A8FEA8DE87F78E","message":{"lang":"en","value":"Property SecurityMethod not found in type Service"},"innererror":{"transactionid":"C83CB3D2A1420080E00689503E02B488"  
**Status Code:** 400

### All services (to see available fields)

**Status:** success  
**Services Found:** 5  
**Available Fields:** __metadata, ID, Description, Title, Author, TechnicalServiceVersion, MetadataUrl, TechnicalServiceName, ImageUrl, ServiceUrl, UpdatedDate, ReleaseStatus, Category, IsSapService, ServiceType, EntitySets, TagCollection, Annotations

**Sample Services:**
```json
[
  {
    "__metadata": {
      "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')",
      "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')",
      "type": "CATALOGSERVICE.Service"
    },
    "ID": "ZAPS_BUM_COLLABORATION_USER_SRV_0001",
    "Description": "APS Collaboration Business User",
    "Title": "APS_BUM_COLLABORATION_USER_SRV",
    "Author": "BPINST",
    "TechnicalServiceVersion": 1,
    "MetadataUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BUM_COLLABORATION_USER_SRV/$metadata",
    "TechnicalServiceName": "ZAPS_BUM_COLLABORATION_USER_SRV",
    "ImageUrl": "",
    "ServiceUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BUM_COLLABORATION_USER_SRV",
    "UpdatedDate": "/Date(1603751644000)/",
    "ReleaseStatus": "",
    "Category": "",
    "IsSapService": true,
    "ServiceType": "UI",
    "EntitySets": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')/EntitySets"
      }
    },
    "TagCollection": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')/TagCollection"
      }
    },
    "Annotations": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')/Annotations"
      }
    }
  },
  {
    "__metadata": {
      "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BCT_MBC_SRV_0001')",
      "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BCT_MBC_SRV_0001')",
      "type": "CATALOGSERVICE.Service"
    },
    "ID": "ZAPS_BCT_MBC_SRV_0001",
    "Description": "Maintain Business Configurations",
    "Title": "APS_BCT_MBC_SRV",
    "Author": "BPINST",
    "TechnicalServiceVersion": 1,
    "MetadataUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BCT_MBC_SRV/$metadata",
    "TechnicalServiceName": "ZAPS_BCT_MBC_SRV",
    "ImageUrl": "",
    "ServiceUrl": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/sap/APS_BCT_MBC_SRV",
    "UpdatedDate": "/Date(1603751644000)/",
    "ReleaseStatus": "",
    "Category": "",
    "IsSapService": true,
    "ServiceType": "Not Classified",
    "EntitySets": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BCT_MBC_SRV_0001')/EntitySets"
      }
    },
    "TagCollection": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BCT_MBC_SRV_0001')/TagCollection"
      }
    },
    "Annotations": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BCT_MBC_SRV_0001')/Annotations"
      }
    }
  }
]
```


## Analysis

Based on these tests, we can determine:
1. Which filter approach works best
2. What authentication-related fields are available
3. The most efficient way to query OAuth2 services

## Recommendations

The most effective approach should be used to update the main filtering script.
