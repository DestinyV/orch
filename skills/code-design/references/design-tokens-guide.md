# 设计令牌指南

前端 UI 生成时参考此文档定义设计系统。使用令牌（token）体系替代硬编码值，确保风格一致。

## 令牌体系结构

### 颜色令牌

```yaml
colors:
  primary: "#..."          # 品牌主色（CTA、关键链接）
  on-primary: "#..."       # 主色上的文本色
  ink: "#..."              # 正文文本色
  body: "#..."             # 次要文本色
  muted: "#..."            # 弱化文本/占位符
  canvas: "#..."           # 页面背景色
  surface-1: "#..."        # 卡片/面板背景色
  hairline: "#..."         # 边框/分割线色
  success: "#..."          # 成功状态色
  warning: "#..."          # 警告状态色
  error: "#..."            # 错误状态色
```

**命名规则**：语义化命名（primary/ink/canvas），不包含具体色相名。

### 字体令牌

```yaml
typography:
  display-xl:              # 超大标题（首页 Hero）
    fontFamily: "Inter, sans-serif"
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -1.5px
  display-md:              # 页面标题
    fontSize: 32px
    fontWeight: 600
  body-md:                 # 正文
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
  caption:                 # 辅助文字
    fontSize: 13px
    fontWeight: 400
  code:                    # 代码
    fontFamily: "JetBrains Mono, monospace"
    fontSize: 14px
```

**层级规则**：
- display-xl/lg/md/sm：标题层级，递减字号
- title-lg/md/sm：卡片/模块标题
- body-lg/md/sm：正文
- caption：辅助文字
- code：等宽代码

### 间距令牌

```yaml
spacing:
  xxs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
  huge: 48px
  massive: 64px
```

### 圆角令牌

```yaml
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  xl: 16px
  full: 9999px        # 胶囊/药丸形
```

### 阴影令牌

```yaml
shadows:
  level-1: "0 1px 3px rgba(0,0,0,0.08)"
  level-2: "0 4px 12px rgba(0,0,0,0.1)"
  level-3: "0 8px 24px rgba(0,0,0,0.12)"
```

## 组件样式定义

每个组件从令牌派生样式，不硬编码值：

### Button

```yaml
button-primary:
  background: "{colors.primary}"
  color: "{colors.on-primary}"
  font: "{typography.title-sm}"
  padding: "{spacing.sm} {spacing.lg}"
  border-radius: "{rounded.md}"
  hover:
    background: "{colors.primary} / 90%"
  disabled:
    opacity: 0.5
```

### Input

```yaml
input:
  background: "{colors.canvas}"
  border: "1px solid {colors.hairline}"
  color: "{colors.ink}"
  font: "{typography.body-md}"
  padding: "{spacing.sm} {spacing.md}"
  border-radius: "{rounded.sm}"
  focus:
    border-color: "{colors.primary}"
    box-shadow: "0 0 0 3px {colors.primary}33"
  placeholder:
    color: "{colors.muted}"
```

### Card

```yaml
card:
  background: "{colors.surface-1}"
  border: "1px solid {colors.hairline}"
  border-radius: "{rounded.lg}"
  padding: "{spacing.xl}"
  shadow: "{shadows.level-1}"
```

## 设计约束

### Do's and Don'ts

定义设计系统的使用边界：

```
## Do's and Don'ts

### Do
- 使用令牌引用而非硬编码值
- 保持色彩层次：背景 < 表面 < 边框 < 文字
- 交互元素使用 primary 色

### Don't
- 不引入未定义的颜色
- 不过度使用 primary 色（仅用于交互元素）
- 不混用多种字重（保持层级清晰）
```

## 响应式断点

```yaml
breakpoints:
  wide: 1440px      # 宽屏
  desktop: 1024px   # 桌面
  tablet: 768px     # 平板
  mobile: 0px       # 手机
```

### 断点行为

- **Desktop first**：从大屏向下适配
- 标题层级逐级缩小：display-xl 48px → display-md 32px → title-lg 22px
- 栅格系统：4列→3列→2列→1列

## 设计系统对齐流程

1. 确定设计风格（简洁/丰富/极简/自定义）
2. 定义颜色令牌（主色 + 语义色）
3. 定义字体层级
4. 定义间距/圆角/阴影
5. 按令牌派生组件样式
6. 输出设计约束文档
