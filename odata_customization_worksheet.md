# OData Service Customization Worksheet

Use this worksheet to gather information about your SAP OData services. Fill out each section completely for best AI model accuracy.

## 📋 Service Information Checklist

### Service 1: Customer/Business Partner Service

**Basic Information:**
- [ ] Service Name: ________________
- [ ] OData Endpoint URL: ________________
- [ ] OAuth2 Token Endpoint: ________________
- [ ] Client ID: ________________

**Business Purpose (Write 2-3 sentences describing what this service does):**
```
Example: "Manages comprehensive customer master data including business partner information, contact details, credit limits, payment terms, and customer relationships. Handles all customer-related inquiries, credit checks, and customer demographic information for sales and service processes."

Your Description:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Main Entities (List the key entities this service exposes):**
1. ________________ (e.g., Customer, BusinessPartner)
2. ________________ (e.g., CustomerAddress, ContactInfo)
3. ________________ (e.g., CustomerCredit, PaymentTerms)

**Use Cases (How would users ask for this data? List 8-10 examples):**
- [ ] "Find customer information"
- [ ] "Get customer credit limit"
- [ ] "Look up customer contact details"
- [ ] "Check customer payment terms"
- [ ] "Find customer by company name"
- [ ] "Get customer address information"
- [ ] "Verify customer credit status"
- [ ] "Update customer contact info"
- [ ] ________________
- [ ] ________________

---

### Service 2: Sales Order Service

**Basic Information:**
- [ ] Service Name: ________________
- [ ] OData Endpoint URL: ________________
- [ ] OAuth2 Token Endpoint: ________________
- [ ] Client ID: ________________

**Business Purpose:**
```
Example: "Handles complete sales order lifecycle including order creation, modification, tracking, and fulfillment. Manages order headers, line items, pricing, delivery schedules, and order status updates for all sales transactions."

Your Description:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Main Entities:**
1. ________________ (e.g., SalesOrder, OrderHeader)
2. ________________ (e.g., SalesOrderItem, OrderLine)
3. ________________ (e.g., OrderStatus, DeliveryInfo)

**Use Cases:**
- [ ] "Track order status"
- [ ] "Find sales order details"
- [ ] "Get order history"
- [ ] "Check order delivery date"
- [ ] "List recent orders"
- [ ] "Find orders by customer"
- [ ] "Get order line items"
- [ ] "Check order total amount"
- [ ] ________________
- [ ] ________________

---

### Service 3: Product/Inventory Service

**Basic Information:**
- [ ] Service Name: ________________
- [ ] OData Endpoint URL: ________________
- [ ] OAuth2 Token Endpoint: ________________
- [ ] Client ID: ________________

**Business Purpose:**
```
Example: "Manages product catalog, inventory levels, stock movements, and product information. Handles product lookups, availability checks, inventory tracking, and stock level monitoring across all warehouses and locations."

Your Description:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

**Main Entities:**
1. ________________ (e.g., Product, Material)
2. ________________ (e.g., Stock, Inventory)
3. ________________ (e.g., StockMovement, Warehouse)

**Use Cases:**
- [ ] "Check product availability"
- [ ] "Get product information"
- [ ] "Check stock levels"
- [ ] "Find products by category"
- [ ] "Get inventory status"
- [ ] "Check product pricing"
- [ ] "List products in stock"
- [ ] "Get product specifications"
- [ ] ________________
- [ ] ________________

---

## 🔍 Field Details Template

For each entity, describe the key fields in business terms:

### Example: Customer Entity Fields
```json
"CustomerID": "Unique customer identifier used for lookups, references in orders, and linking customer data across systems",
"CompanyName": "Legal business name of the customer organization used for contracts, invoicing, and official correspondence",
"CreditLimit": "Maximum credit amount approved for customer transactions, used for credit checks and order approval processes",
"Industry": "Business sector classification used for market analysis, targeted marketing, and risk assessment",
"PaymentTerms": "Standard payment conditions and terms negotiated with customer, affects invoicing and collection processes"
```

### Your Field Descriptions:

**Service 1 - Entity 1 Fields:**
- Field 1: ________________
  Description: _________________________________________________________________
- Field 2: ________________
  Description: _________________________________________________________________
- Field 3: ________________
  Description: _________________________________________________________________

**Service 2 - Entity 1 Fields:**
- Field 1: ________________
  Description: _________________________________________________________________
- Field 2: ________________
  Description: _________________________________________________________________
- Field 3: ________________
  Description: _________________________________________________________________

**Service 3 - Entity 1 Fields:**
- Field 1: ________________
  Description: _________________________________________________________________
- Field 2: ________________
  Description: _________________________________________________________________
- Field 3: ________________
  Description: _________________________________________________________________

---

## 💡 Tips for Better Descriptions

### ✅ Good Examples:
- **Purpose**: "Manages customer master data including demographics, contact information, credit limits, and business relationships for all customer interactions and sales processes"
- **Field**: "OrderStatus - Current processing stage of the sales order (draft, confirmed, shipped, delivered) used for tracking and customer communication"
- **Use Case**: "What's the delivery status of my order?"

### ❌ Avoid These:
- **Purpose**: "Customer service" (too vague)
- **Field**: "OrderStatus - Status field" (not descriptive)
- **Use Case**: "Get data" (not specific)

### 🎯 Key Questions to Ask:
1. **What business process does this serve?**
2. **When would a user need this information?**
3. **How would they naturally ask for it?**
4. **What business decisions does this data support?**

---

## 📝 Next Steps

1. **Fill out this worksheet completely**
2. **Review with business users** to ensure accuracy
3. **Test with real user questions** you've heard before
4. **I'll help convert this into the JSON format**
5. **Run local testing to validate**

---

**Ready to start?** Begin with your most important/frequently used service first!
