# 状态图

```mermaid
stateDiagram-v2
    [*] --> Pending: create
    Pending --> Active: approve
    Active --> Completed: finish
    Active --> Cancelled: cancel
    Pending --> Cancelled: cancel
    Completed --> [*]
    Cancelled --> [*]
```
