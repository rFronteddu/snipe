# Snipe
Simple AI personal assistant written from scratch.

## Requirements

## Roadmap
- [ ] JSON Validator with specific format

## Naming
* Agent: LLM Powered autonomous component
* Tool: Deterministic tool an Agent can use

## Capabilities
* [V] weather service tool https://www.weather.gov/documentation/services-web-api
* [ ] 

## Security Notes

## Architecture -- Tentative docs

```mermaid
flowchart TD
    %% Define Styles
    classDef user fill:#8b5cf6,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef core fill:#3b82f6,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef llm fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef memory fill:#10b981,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef tool fill:#ef4444,stroke:#fff,stroke-width:2px,color:#fff,font-weight:bold
    classDef loop fill:#1f2937,stroke:#4b5563,stroke-width:2px,color:#e5e7eb,stroke-dasharray: 5 5

    %% Entities
    User((User)):::user
    Agent["⚙️ Agent<br/>(handle_message)"]:::core
    Memory["💾 Memory<br/>(memory.json)<br/>get_recent_context<br/>add_chat_turn<br/>summarize_if_needed"]:::memory
    LLM{"🧠 Local LLM"}:::llm
    Tools["🛠️ Tools<br/>(e.g., weather_tool)"]:::tool

    %% Initial Input
    User -->|1. Raw Message| Agent

    %% Phase 1: Context & Planning
    Agent -->|2. Fetch History| Memory
    Memory -.->|History| Agent
    
    Agent -->|3. Planner input| LLM
    LLM -.->|4. JSON Plan| Agent

    %% Phase 2: Execution Loop
    subgraph Execution_Loop [Execution Loop]
        direction TB
        Parse["_safe_parse_json()"]
        LoopCheck{"Next step?"}
        
        Parse --> LoopCheck
        
        LoopCheck -->|tool| ExecTool["_exec_tool()"]
        ExecTool -->|run| Tools
        Tools -.->|result| SaveObs["append observations"]
        SaveObs --> LoopCheck
        
        LoopCheck -->|respond| Finalize["_finalize()<br/>format output"]
    end
    class Execution_Loop loop

    Agent -->|5. Parse Plan| Parse
    
    %% Phase 3: Synthesis
    Finalize -->|6. Context + Observations| LLM
    LLM -.->|7. Final Response| Agent

    %% Phase 4: Memory Management
    Agent -->|8. Save Turns| Memory
    Agent -->|9. Check Summary| Memory
    Memory -->|if large| LLM
    LLM -.->|summary| Memory

    %% Output
    Agent -->|10. Return| User
```