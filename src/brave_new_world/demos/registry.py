from brave_new_world.contracts import DemoManifest


DEMOS = (
    DemoManifest(
        id="first-order-step",
        version="1.0",
        title="一阶系统与低通滤波",
        summary="观察时间常数、增益和采样步长如何影响阶跃响应。",
        learning_objectives=(
            "把一阶微分方程与指数响应对应起来",
            "理解时间常数与响应速度的关系",
            "区分系统增益、输入幅值和初始状态的影响",
        ),
        parameter_names=(
            "duration_s",
            "dt_s",
            "input_amplitude",
            "time_constant_s",
            "gain",
            "initial_output",
        ),
    ),
)


def get_demo(demo_id: str) -> DemoManifest:
    for demo in DEMOS:
        if demo.id == demo_id:
            return demo
    raise KeyError(demo_id)
