# BraveNewWorld

BraveNewWorld 是一套面向控制理论、信号处理、运动学和机器人基础技术的示教、可视化与轻量仿真工具，也是 [JobSlayer](https://github.com/fangzhouRWTH/JobSlayer) 的外部实验测试床。

BNW-0 提供第一个可运行主题：一阶系统/一阶低通滤波器的阶跃响应。浏览器 UI 与无头命令调用同一套确定性 Python 仿真内核。

## 快速开始

无需安装运行时依赖。需要 Python 3.11 或更高版本。

```bash
./bnw check
./bnw simulate --duration 5 --dt 0.05 --tau 0.8
./bnw run-scenario scenarios/first-order-default.json
./bnw ui --open-browser
```

UI 默认只监听 `127.0.0.1:8080`。打开终端显示的地址即可调节输入幅值、系统增益、时间常数、初值、仿真时长和步长；曲线、指标与导出的 JSON 均来自真实仿真响应。

## 仓库结构

```text
src/brave_new_world/
├── contracts.py          # 稳定的请求、轨迹和 demo 契约
├── simulation/           # 确定性仿真内核
├── demos/                # 主题登记
└── ui/                   # loopback HTTP API 与模块化静态界面
tests/                    # 无头数值与 API 集成测试
scenarios/                # 版本化可复现实验输入
docs/                     # 架构、ADR 和逐步开发记录
```

远端仓库：<https://github.com/fangzhouRWTH/BraveNewWorld>
