# Architecture Diagrams for OData Service AI Classifier

## 1. MCP Server Integration Flow

```mermaid
sequenceDiagram
    participant QCli as Q CLI
    participant MCP as MCP Server
    participant Tools as Custom Tools
    participant SM as SageMaker
    participant OData as SAP OData

    QCli->>MCP: User query via MCP protocol
    MCP->>Tools: Route to appropriate tool
    Tools->>SM: Classify intent
    SM->>Tools: Service classification
    Tools->>OData: Execute authenticated query
    OData->>Tools: Return data
    Tools->>MCP: Format response
    MCP->>QCli: Return structured result
```

## 2. Agent Core Decision Making

```mermaid
flowchart TD
    A[User Input] --> B{Intent Clear?}
    B -->|Yes| C[Direct Classification]
    B -->|No| D[Bedrock LLM Analysis]
    
    C --> E[SageMaker Classifier]
    D --> F[Enhanced Context]
    F --> E
    
    E --> G{Confidence > 0.8?}
    G -->|Yes| H[Execute Query]
    G -->|No| I[Request Clarification]
    
    H --> J[OAuth2 Authentication]
    J --> K[OData Service Call]
    K --> L[Result Processing]
    L --> M[Response Generation]
    
    I --> N[Interactive Clarification]
    N --> A
```

## 3. Multi-Service Orchestration

```mermaid
graph TB
    subgraph "User Layer"
        U1[Business User]
        U2[Developer]
        U3[Admin]
    end
    
    subgraph "AI Orchestration"
        QBiz[Q Business]
        QDev[Q Developer]
        Agent[Agent Core]
    end
    
    subgraph "Intelligence Services"
        BR[Bedrock LLM]
        SM[SageMaker ML]
        KB[Knowledge Base]
    end
    
    subgraph "Integration Layer"
        MCP[MCP Server]
        Lambda[Lambda Functions]
        API[API Gateway]
    end
    
    subgraph "Enterprise Systems"
        SAP1[Customer Service]
        SAP2[Sales Service]
        SAP3[Inventory Service]
        SAP4[Finance Service]
    end
    
    U1 --> QBiz
    U2 --> QDev
    U3 --> Agent
    
    QBiz --> BR
    QDev --> SM
    Agent --> KB
    
    BR --> MCP
    SM --> Lambda
    KB --> API
    
    MCP --> SAP1
    Lambda --> SAP2
    API --> SAP3
    Lambda --> SAP4
```

## 4. Data Flow and Security

```mermaid
flowchart LR
    subgraph "Secure Zone"
        A[Encrypted Input] --> B[Authentication]
        B --> C[Authorization]
        C --> D[Data Classification]
    end
    
    subgraph "Processing Zone"
        D --> E[Intent Analysis]
        E --> F[Service Selection]
        F --> G[Query Generation]
    end
    
    subgraph "Integration Zone"
        G --> H[OAuth2 Token]
        H --> I[OData Call]
        I --> J[Response Validation]
    end
    
    subgraph "Response Zone"
        J --> K[Data Sanitization]
        K --> L[Result Formatting]
        L --> M[Encrypted Output]
    end
    
    style A fill:#ff9999
    style M fill:#99ff99
    style H fill:#ffff99
```

## 5. Monitoring and Observability

```mermaid
graph TD
    subgraph "Application Metrics"
        A1[Response Time]
        A2[Success Rate]
        A3[User Satisfaction]
    end
    
    subgraph "Business Metrics"
        B1[Query Volume]
        B2[Service Usage]
        B3[Cost Optimization]
    end
    
    subgraph "Technical Metrics"
        T1[System Health]
        T2[Error Rates]
        T3[Resource Usage]
    end
    
    subgraph "Monitoring Stack"
        CW[CloudWatch]
        XRay[X-Ray Tracing]
        Logs[CloudWatch Logs]
    end
    
    A1 --> CW
    A2 --> CW
    A3 --> Logs
    
    B1 --> CW
    B2 --> XRay
    B3 --> CW
    
    T1 --> CW
    T2 --> XRay
    T3 --> CW
```

## 6. Deployment Pipeline

```mermaid
gitGraph
    commit id: "Initial Setup"
    branch development
    checkout development
    commit id: "MCP Server"
    commit id: "Agent Core"
    commit id: "Q Integration"
    
    checkout main
    merge development
    commit id: "v1.0 Release"
    
    branch feature/bedrock
    checkout feature/bedrock
    commit id: "Bedrock LLM"
    commit id: "Enhanced NLP"
    
    checkout development
    merge feature/bedrock
    commit id: "Integration Tests"
    
    checkout main
    merge development
    commit id: "v2.0 Release"
```

## 7. Error Handling and Recovery

```mermaid
stateDiagram-v2
    [*] --> Processing
    Processing --> Success : Query Successful
    Processing --> AuthError : Authentication Failed
    Processing --> ServiceError : Service Unavailable
    Processing --> ClassificationError : Low Confidence
    
    AuthError --> TokenRefresh : Refresh OAuth Token
    TokenRefresh --> Processing : Retry Query
    TokenRefresh --> ManualAuth : Refresh Failed
    
    ServiceError --> Fallback : Try Alternative Service
    Fallback --> Processing : Service Available
    Fallback --> QueueRequest : All Services Down
    
    ClassificationError --> UserClarification : Request More Info
    UserClarification --> Processing : Clarification Provided
    
    Success --> [*]
    ManualAuth --> [*]
    QueueRequest --> [*]
```

## 8. Scalability Architecture

```mermaid
C4Context
    title System Context Diagram for OData AI Classifier
    
    Person(user, "Business User", "Needs access to SAP data")
    Person(dev, "Developer", "Builds and maintains integrations")
    Person(admin, "System Admin", "Manages infrastructure")
    
    System(classifier, "OData AI Classifier", "Intelligent routing and query system")
    
    System_Ext(sap, "SAP Systems", "Enterprise OData services")
    System_Ext(aws, "AWS Services", "Cloud infrastructure and AI services")
    System_Ext(auth, "OAuth Provider", "Authentication and authorization")
    
    Rel(user, classifier, "Asks questions in natural language")
    Rel(dev, classifier, "Configures and extends")
    Rel(admin, classifier, "Monitors and maintains")
    
    Rel(classifier, sap, "Queries OData services")
    Rel(classifier, aws, "Uses AI/ML services")
    Rel(classifier, auth, "Authenticates requests")
```
