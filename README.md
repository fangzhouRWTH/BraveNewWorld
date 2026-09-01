# BraveNewWorld

BraveNewWorld 是 JobSlayer 的快速任务验证场：以
[Anygine](https://github.com/fangzhouRWTH/Anygine) 为基础引擎，持续创建边界清晰、可独立构建、
可运行、可验证的小规模原生 App。它不再承担网页端机电设备物理模拟产品的开发目标。

这个仓库是独立的顶层 CMake consumer，不复制 Anygine 源码，也不直接依赖引擎私有目录。
当前固定 Anygine `main` 的 commit `28b4934c24fdad6b8f45b945a89a6ada51703f5d`，通过引擎已经验证的
public build-tree targets 接入。

## 当前最小闭环

首个 `hello-task` App 只验证五件事：

1. BraveNewWorld 能在仓库外部注册固定版本的 Anygine；
2. 只通过公共 `Anygine::*` targets 编译和链接；
3. 能创建窗口、Vulkan backend、Renderer 与 UI context；
4. 能运行固定 3 帧并输出机器可检查的结果；
5. App manifest、引擎 pin、构建与测试可以由同一个入口重复执行。

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

具备显示设备和 Vulkan validation layer 时可运行 3 帧烟雾案例：

```bash
./bnw run --engine-root /absolute/path/to/Anygine
```

## 目录

- `Config/Engine.json`：固定的 Anygine 来源与 commit；
- `Config/Apps/*.json`：面向 JobSlayer 的小 App 任务/验证清单；
- `Source/Apps/<App>`：薄应用实现；
- `Tests/ManifestContract.py`：不依赖图形设备的结构契约检查；
- `Scripts/BraveNewWorld.py`：跨平台 doctor/configure/build/test/run 入口；
- `docs/`：当前架构、ADR 与追加式开发记录。

详见 [架构说明](docs/ARCHITECTURE.md) 与 [开发记录](docs/DEVELOPMENT_LOG.md)。
