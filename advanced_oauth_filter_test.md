# SAP OData Advanced Filter Testing Results

**System:** https://vhcals4hci.awspoc.club  
**Generated:** 2025-08-09 23:50:22

## Key Findings

The original filtering approach `$filter=AuthenticationMode eq 'OAuth2'` **does not work** because:
- `AuthenticationMode` field does not exist in the SAP Gateway Catalog Service
- `SecurityMethod` field also does not exist
- Authentication information is not directly exposed in the service catalog

## Alternative Approaches Tested


### Services with OAuth in Title/Description

**Status:** success  
**Services Found:** 3360

**Sample Service:**
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
  }
]
```

### Services with Auth in Title/Description

**Status:** success  
**Services Found:** 3360

**Sample Service:**
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
  }
]
```

### Services with Security in Title/Description

**Status:** success  
**Services Found:** 3360

**Sample Service:**
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
  }
]
```

### Check TagCollection for OAuth info

**Status:** success  
**Services Found:** 3

**Sample Service:**
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
      "results": [
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH",
          "Text": "CDS.C_BPUSRACADEMICTITLEVH.C_BPUsrAcademicTitleVH",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRACADEMICTITLEVH.C_BPUSRACADEMICTITLEVH')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH",
          "Text": "CDS.C_BPUSRASSIGNMENTVH.C_BPUsrAssignmentVH",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRASSIGNMENTVH.C_BPUSRASSIGNMENTVH')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH",
          "Text": "CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFormOfAddressVH",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRFORMOFADDRESSVH.C_BPUSRFORMOFADDRESSVH')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH",
          "Text": "CDS.C_BPUSRRELSHPBPORGVH.C_BPUsrRelshpBPOrgVH",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_BPUSRRELSHPBPORGVH.C_BPUSRRELSHPBPORGVH')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP",
          "Text": "CDS.C_COLLABORATIONBUSINESSUSERTP.C_CollaborationBusinessUserTP",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.C_COLLABORATIONBUSINESSUSERTP.C_COLLABORATIONBUSINESSUSERTP')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME",
          "Text": "CDS.I_BUSPARTPREFIXNAME.I_BusPartPrefixName",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_BUSPARTPREFIXNAME.I_BUSPARTPREFIXNAME')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_COUNTRYVH.I_COUNTRYVH')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_COUNTRYVH.I_COUNTRYVH')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.I_COUNTRYVH.I_COUNTRYVH",
          "Text": "CDS.I_COUNTRYVH.I_CountryVH",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_COUNTRYVH.I_COUNTRYVH')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_COUNTRYVH.I_COUNTRYVH')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_COUNTRYVH.I_COUNTRYVH')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA",
          "Text": "CDS.I_DRAFTADMINISTRATIVEDATA.I_DraftAdministrativeData",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_DRAFTADMINISTRATIVEDATA.I_DRAFTADMINISTRATIVEDATA')/TagScopedServices"
            }
          }
        },
        {
          "__metadata": {
            "id": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_LANGUAGE.I_LANGUAGE')",
            "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_LANGUAGE.I_LANGUAGE')",
            "type": "CATALOGSERVICE.Tag"
          },
          "ID": "CDS.I_LANGUAGE.I_LANGUAGE",
          "Text": "CDS.I_LANGUAGE.I_Language",
          "Occurrence": 1,
          "Services": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_LANGUAGE.I_LANGUAGE')/Services"
            }
          },
          "TagRecommendedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_LANGUAGE.I_LANGUAGE')/TagRecommendedServices"
            }
          },
          "TagScopedServices": {
            "__deferred": {
              "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/TagCollection('CDS.I_LANGUAGE.I_LANGUAGE')/TagScopedServices"
            }
          }
        }
      ]
    },
    "Annotations": {
      "__deferred": {
        "uri": "https://VHCALS4HCI.AWSPOC.CLUB:443/sap/opu/odata/IWFND/CATALOGSERVICE;v=2/ServiceCollection('ZAPS_BUM_COLLABORATION_USER_SRV_0001')/Annotations"
      }
    }
  }
]
```

### Check Annotations for OAuth info

**Status:** error  
**Error:** {"error":{"code":"/IWFND/CM_MGW/051","message":{"lang":"en","value":"Resource not found for the segment 'ServiceCollection'"},"innererror":{"application":{"component_id":"","service_namespace":"/IWFND  
**Status Code:** 400

### Get service metadata schema

**Status:** error  
**Error:** {"error":{"code":"005056A509B11ED19BEB6513AA349DA5","message":{"lang":"en","value":"The resource identified by the request is only capable of generating response entities which have content characteri  
**Status Code:** 406


## Conclusion

**The filtering approach `$filter=AuthenticationMode eq 'OAuth2'` does NOT work** because:

1. **No Authentication Fields**: The SAP Gateway Catalog Service does not expose authentication-related fields
2. **Limited Metadata**: Service catalog only contains basic service information
3. **Security by Design**: Authentication configuration is typically handled at the system/gateway level, not service level

## Recommended Approach

The **current metadata inspection approach is actually the most reliable** method because:

1. **Service Metadata Analysis**: Check each service's `/$metadata` endpoint for OAuth2 indicators
2. **Gateway Configuration**: Authentication is configured at the SAP Gateway level
3. **Runtime Detection**: OAuth2 support is determined by examining service implementation details

## Better Optimization Strategies

Instead of server-side filtering, optimize the current approach:

1. **Parallel Processing**: Check multiple services concurrently
2. **Smart Sampling**: Prioritize services with auth-related keywords in title/description
3. **Caching**: Cache results to avoid repeated checks
4. **Batch Processing**: Process services in smaller batches

The metadata inspection approach, while slower, is the most accurate method for detecting OAuth2 support.
