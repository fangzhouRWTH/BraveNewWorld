# 开发决策与落实记录

本文件按追加方式记录 BraveNewWorld 的每次重要决策、具体落实和验证证据。JobSlayer 侧的治理决策继续记录在 JobSlayer 自身日志中。

## BNW-2026-08-07-01：建立 BNW-0 可运行基线

### 背景与决策

- 仓库最初没有提交和产品文件，`main` 指向不存在的远端基线。
- 选择纯 Python 标准库和原生浏览器技术，避免在尚无功能退出条件时引入基础设施依赖。
- 首个 demo 选择一阶系统/一阶低通阶跃响应，因为公式清晰、交互直观、数值结果可解析验证。
- 浏览器 UI 和无头 CLI 共用 `SimulationRequest -> simulate_first_order -> SimulationTrace`，不维护测试专用算法。
- UI 仅提供已实现的重新运行、恢复默认和 JSON 导出；不展示尚未实现的暂停、单步或实时动画。

### 落实步骤

1. 建立严格且不可变的请求、版本化场景、轨迹点、轨迹和主题清单契约，并登记默认单位阶跃场景。
2. 使用零阶保持精确离散公式实现固定步长一阶仿真，限制参数、步数和非有限数值。
3. 为轨迹加入 schema、引擎版本、Python 运行时版本、指标与基于规范 JSON 的 SHA-256 哈希。
4. 建立 `simulate` 无头命令、loopback-only JSON API 和静态资源服务器。
5. 建立独立 HTML、CSS、JavaScript 资源；Canvas 绘制 API 返回的输入和输出，指标不使用占位数据。
6. 建立 `./bnw check` 作为完整本地验证入口，并补充数值、契约、HTTP 和入口测试。
7. 编写架构说明和 ADR-0001，明确依赖边界及未来引入依赖的退出条件。

### 验证与后续

- 首轮 `./bnw check` 为 2/3：编译和 diff 检查通过，unittest 子进程因找不到 `src/` 包而失败。这是源码入口的环境传播缺陷，不是仿真断言失败。
- 已修正 `check`：在只影响子进程的环境副本中显式把仓库 `src/` 置于 `PYTHONPATH` 首位，同时保留调用者已有值。
- 最终 `./bnw check` 为 4/4：16 项 unittest、字节码编译、未暂存与已暂存 Git diff 检查全部通过。
- 使用 headless Chrome 在 1440×1000 视口加载真实 UI；默认 API 请求显示 101 个采样点、输入/输出曲线、数值指标与轨迹哈希。烟雾截图只保存在临时目录，不作为仓库制品。
- 初次暂存检查发现部分新文件末尾有额外空白行；统一清理，并把暂存区检查纳入 `./bnw check`，避免初始基线携带格式噪声。
- 验证通过后创建本地 `bnw-0` 固定标签；在首次推送前保持登记状态为 bootstrapping。

## BNW-2026-08-11-01：修复 Windows 可视化界面启动

### 背景与决策

- Windows 直接执行 POSIX `bnw` 源码入口会报 `WinError 193`，导致 UI 服务根本未启动；HTTP 页面、静态资源和仿真 API 经独立验证均正常。
- 按 ADR-0002 增加 Windows 薄启动器，保持安装后的 `bnw <command>` 为跨平台公共接口。
- 自动打开浏览器失败不应终止本地 UI；端口绑定失败必须返回非零状态并给出 `--port 0` 恢复路径。

### 落实步骤

1. 新增 `bnw.cmd` 和换行属性，复用现有 Python 源码入口，并优先发现仓库 `.venv`。
2. UI 命令立即刷新访问地址；浏览器无法打开时打印手工 URL；端口不可用时输出可操作错误。
3. 更新源码入口、浏览器失败和绑定失败测试，并补充 Windows/POSIX 快速开始说明。
4. 新增 ADR-0002，记录平台差异仅位于薄启动器边界的长期约束。

### 验证与后续

- 变更文件：`.gitattributes`、`bnw.cmd`、`README.md`、`src/brave_new_world/cli.py`、`tests/test_cli.py`、`tests/test_ui_server.py`、`docs/adr/0002-cross-platform-source-ui-launcher.md`、`docs/DEVELOPMENT_LOG.md`。
- `.\bnw.cmd --help`：Windows 源码入口退出码 0，正确列出 `simulate`、`run-scenario`、`ui`、`check`。
- `.\bnw.cmd check`：4/4 通过；18 项 unittest 全部通过，随后完成 `compileall`、未暂存 diff 和已暂存 diff 检查。
- `.\bnw.cmd ui --port 0`：Windows 源码入口成功监听系统分配的 `127.0.0.1:6225`；真实请求验证 `/`、`/styles.css`、`/app.js` 均返回 200，`/api/simulate` 返回 `first-order-exact-v1`、5 个采样点和 64 字符轨迹哈希。验证后已停止该临时服务并确认端口释放。
- 当前应用内浏览器没有可连接实例，因此本轮不能进行截图级视觉复核；HTTP 资源、前端脚本分发和真实 API 路径已独立实机验证。下一步建议在可用的桌面浏览器中执行 `.\bnw.cmd ui --open-browser` 做人工交互验收，并把 Windows/Linux 启动器纳入双平台 CI。
