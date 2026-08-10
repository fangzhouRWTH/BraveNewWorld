# ADR-0002：提供跨平台源码 UI 启动入口

- 状态：Accepted
- 日期：2026-08-11

## 背景

BNW-0 的 `bnw` 源码入口是带 shebang 的无扩展名 Python 文件，可在 POSIX 直接执行，但 Windows 无法把它作为原生可执行文件启动，会在 UI 服务创建前报 `WinError 193`。安装后的 console script 已经跨平台，源码检出场景仍缺少 Windows 入口。

## 决策

- 保留 `./bnw` 作为 POSIX 源码入口，新增 `bnw.cmd` 作为 Windows 源码入口；两者都进入同一个 `brave_new_world.cli`，不复制命令或仿真逻辑。
- Windows 启动器优先使用仓库 `.venv`，其次使用系统 `py -3`，最后使用 `python`。安装后继续以 `bnw <command>` 作为两端通用公共接口。
- UI 仍只监听 loopback。自动打开浏览器失败时继续提供服务并打印手工 URL；绑定失败时返回非零状态和动态端口重试提示。

## 后果

- Windows 和 POSIX 的源码检出都具有可直接发现、可测试的启动命令。
- 平台差异只存在于薄启动器层，HTTP 契约、仿真内核和浏览器资源保持单一实现。
- `--port 0` 可由操作系统选择空闲端口，避免用户必须先诊断端口冲突。
