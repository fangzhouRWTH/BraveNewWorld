# BraveNewWorld

BraveNewWorld 是 JobSlayer 的快速任务验证场：以
[Anygine](https://github.com/fangzhouRWTH/Anygine) 为基础引擎，持续创建边界清晰、可独立构建、
可运行、可验证的小规模原生 App。它不再承担网页端机电设备物理模拟产品的开发目标。

这个仓库是独立的顶层 CMake consumer，不复制 Anygine 源码，也不直接依赖引擎私有目录。
当前固定 Anygine `main` 的 commit `28b4934c24fdad6b8f45b945a89a6ada51703f5d`，通过引擎已经验证的
public build-tree targets 接入。

## 当前 App

`hello-task` 继续作为最小的 3 帧 Engine/Vulkan/Renderer/UI 基线。默认运行入口现为
`life-game`：一个 24×24 环面 Conway 生命游戏，规则为 B3/S23。其模型只使用 C++20 标准库，
固定 seed 是五细胞 glider；`reset` 会恢复 seed、generation 0 和暂停状态。

原生 UI 显示完整细胞网格、generation 与 live count，并提供 `Pause`/`Resume`、
`Single Step`、`Reset` 控件。无输入 smoke 会自动继续演化并在 12 个 presented frames 后退出；
固定成功标记包含 Vulkan validation requested/enabled、`errors=0`、帧数以及生命游戏统计。

不需要 Anygine 或图形设备的结构检查可单独运行：

```bash
./bnw contract
```

## 构建

先按 Anygine 自身说明准备 Conan/CMake/Vulkan 依赖，然后从本仓库运行：

```bash
./bnw doctor --engine-root /absolute/path/to/Anygine
./bnw configure --engine-root /absolute/path/to/Anygine
./bnw build --engine-root /absolute/path/to/Anygine
./bnw test --engine-root /absolute/path/to/Anygine
```

完整门禁：

```bash
./bnw check --engine-root /absolute/path/to/Anygine
```

若固定 Anygine worktree 与 Conan toolchain 不在同一目录，可显式传入：

```bash
./bnw check \
  --engine-root /absolute/path/to/pinned/Anygine \
  --toolchain /absolute/path/to/anygine/build/conan/conan_toolchain.cmake
```

具备显示设备和 Vulkan validation layer 时，默认入口会运行有界的 `life-game` smoke：

```bash
./bnw run --engine-root /absolute/path/to/Anygine
```

该命令会构建所有 BraveNewWorld targets，并实际启动 `BraveNewWorldLifeGame`；不会回退到
`hello-task`。模型 CTest 覆盖 blinker、glider、reset、pause/resume、single-step 和边界 wrap。

## 目录

- `Config/Engine.json`：固定的 Anygine 来源与 commit；
- `Config/Apps/*.json`：面向 JobSlayer 的小 App 任务/验证清单；
- `Source/Apps/<App>`：薄应用实现；
- `Source/Apps/LifeGame/Tests`：不依赖 GPU 的确定性模型测试；
- `Tests/ManifestContract.py`：manifest、入口、public-target 边界与文档绑定检查；
- `Scripts/BraveNewWorld.py`：跨平台 doctor/configure/build/test/run 入口，run 默认路由到 life-game；
- `docs/`：当前架构、ADR 与追加式开发记录。

详见 [架构说明](docs/ARCHITECTURE.md) 与 [开发记录](docs/DEVELOPMENT_LOG.md)。
