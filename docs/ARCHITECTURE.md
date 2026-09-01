# Architecture

## 1. 定位

BraveNewWorld 是“小 App 工厂”和 JobSlayer 外部测试床，不是第二个引擎，也不是 Anygine 的分支。
每个 App 提供一个足够具体的开发目标，使任务规划、串行执行、证据反馈和人工门禁可以在较短周期内
反复验证。

## 2. 依赖边界

```text
JobSlayer control plane
  -> 固化任务 DAG、执行、验证与反馈
  -> BraveNewWorld app repository
       -> top-level CMake project
       -> public Anygine::* targets
            -> pinned Anygine source worktree
```

BraveNewWorld 通过 `add_subdirectory(ANYGINE_SOURCE_ROOT, build/anygine)` 注册固定源码 worktree。
首阶段只允许引擎已验证的 public targets：`Anygine::Engine`、`Anygine::GraphicsVulkan`、
`Anygine::RendererCore`、`Anygine::RuntimeAssets` 与 `Anygine::UI`。App 不复制 Anygine 源文件、
不添加 `Private` include、也不修改引擎 checkout。

## 3. App 单元

一个可进入任务规划闭环的 App 至少包含：

- `Config/Apps/<id>.json`：目标、入口 target、验收与验证命令；
- `Source/Apps/<Name>/`：薄 CMake target 与实现；
- 不依赖 GPU 的 manifest/contract check；
- 可选的有界 Vulkan/UI smoke；
- 对应的开发日志证据。

只有第二个 App 证明存在真实复用需求后，才把重复逻辑提取为 BraveNewWorld 公共库。

## 4. 版本与构建

`Config/Engine.json` 与根 `CMakeLists.txt` 双重固定 Anygine commit。`Scripts/BraveNewWorld.py`
统一 doctor、configure、build、test 与 run；CMake/CTest 仍拥有真实构建和测试语义。

## 5. JobSlayer 边界

BraveNewWorld 只拥有源码、App manifests 和项目内验证。任务状态、权限、重试、验证报告、审批与完成
结论始终由 JobSlayer 的控制面和 `WorkflowKernel` 管理。
