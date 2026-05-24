# 用例图

```mermaid
graph LR
    subgraph System[系统边界]
        UC1[用例1]
        UC2[用例2]
        UC3[用例3]
    end
    User((用户)) --> UC1
    User --> UC2
    Admin((管理员)) --> UC3
```
