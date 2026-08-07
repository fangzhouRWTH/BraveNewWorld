# BNW-0 架构

## 目标

BNW-0 建立一个小而真实的教学产品基线：同一确定性仿真内核既服务无头验证，也服务浏览器交互。首个主题用一阶系统阶跃响应说明时间常数、增益、输入和初值。

```text
浏览器参数 ──HTTP JSON──┐
                        ├─> SimulationRequest ─> first-order kernel ─> SimulationTrace
无头 CLI 参数 ──────────┘                                      │
                                                               ├─> JSON 证据
                                                               └─> Canvas 曲线
```

## 模块边界

- `contracts.py`：严格请求、轨迹点、轨迹和 demo manifest；不依赖 HTTP 或浏览器。
- `simulation/`：纯计算。首个内核使用零阶保持下的一阶系统精确离散更新。
- `demos/`：教学主题元数据登记，不拥有第二套时钟或仿真逻辑。
- `ui/server.py`：loopback-only HTTP 边界、JSON 校验和静态资源服务。
- `ui/assets/`：极简参数表单与 Canvas 呈现，只消费 API 返回的真实轨迹。
- `cli.py`：`simulate`、`ui` 和统一本地检查入口。

## 数值约定

模型为 `τ dy/dt + y = K u`。输入在 `t=0` 施加并在步间保持，状态更新为：

```text
y[k+1] = K u + (y[k] - K u) exp(-dt / τ)
```

请求要求 `duration / dt` 为整数且不超过 5000 步。轨迹包含 `t=0` 初值和终点，因此采样点数为步数加一。版本化 `Scenario` 固定教学输入；轨迹 JSON 使用固定字段、引擎版本、Python 运行时版本和 SHA-256 哈希支持复现。

## 当前边界

BNW-0 不模拟噪声、暂停时钟或多体动力学。UI 只有“重新计算式”的运行、复位和真实 JSON 导出；没有伪造尚未实现的暂停、单步或动画状态。后续主题只有在共享契约足够时才扩展。
