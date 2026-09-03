#include <BraveNewWorld/LifeGame/LifeGameModel.hpp>

#include <Anygine/Configuration/RuntimeConfig.hpp>
#include <Anygine/Engine/Application.hpp>
#include <Anygine/Graphics/Vulkan/VulkanBackend.hpp>
#include <Anygine/Math/DepthConvention.hpp>
#include <Anygine/Renderer/RenderFeatureProfile.hpp>
#include <Anygine/Renderer/Renderer.hpp>
#include <Anygine/UI/UiContext.hpp>

#include <algorithm>
#include <concepts>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

#ifndef ANYGINE_GENERATED_SHADER_DIR
#error "Link Anygine::RuntimeAssets to receive the registered build-tree shader directory."
#endif

namespace
{
using brave_new_world::life_game::LifeGameModel;

template <typename>
inline constexpr bool kUnsupportedButtonInterface = false;

template <typename Frame>
[[nodiscard]] bool DrawButton(Frame& frame, const char* label)
{
    if constexpr (requires(Frame& candidate, const char* text) {
                      { candidate.Button(text) } -> std::convertible_to<bool>;
                  })
    {
        return frame.Button(label);
    }
    else if constexpr (requires(Frame& candidate, std::string_view text) {
                           { candidate.Button(text) } -> std::convertible_to<bool>;
                       })
    {
        return frame.Button(std::string_view{label});
    }
    else if constexpr (requires(Frame& candidate, const std::string& text) {
                           { candidate.Button(text) } -> std::convertible_to<bool>;
                       })
    {
        return frame.Button(std::string{label});
    }
    else
    {
        static_assert(
            kUnsupportedButtonInterface<Frame>,
            "The public Anygine IUiFrame must expose clickable buttons for life-game.");
        return false;
    }
}

class LifeGameApplication final : public anygine::engine::IApplication
{
public:
    static constexpr std::uint64_t kSmokeFrameCount = 12U;

    void OnStart(anygine::platform::Window& window) override
    {
        m_vulkan.emplace(anygine::graphics::vulkan::VulkanBackendCreateInfo{
            .window = window,
            .validationMode = anygine::configuration::VulkanValidationMode::Required,
            .applicationName = "BraveNewWorld Life Game",
            .shaderDirectory = std::filesystem::path{ANYGINE_GENERATED_SHADER_DIR},
        });
        if (!m_vulkan->GetInfo().validationRequested || !m_vulkan->GetInfo().validationEnabled)
        {
            throw std::runtime_error{"Required Vulkan validation was not enabled."};
        }

        m_renderer.emplace(*m_vulkan);
        m_ui = anygine::ui::UiContext::Create(anygine::ui::UiContextCreateInfo{
            .vulkan = &(*m_vulkan),
            .window = &window,
            .enabled = true,
        });
        if (!m_ui.has_value() || !m_ui->IsEnabled())
        {
            throw std::runtime_error{"Public Anygine UI context creation failed."};
        }

        m_ui->RegisterPanel(anygine::ui::UiPanelDescriptor{
            .id = "life-game",
            .title = "Conway Life Game",
            .drawCallback =
                [this](anygine::ui::IUiFrame& frame)
            {
                DrawControls(frame);
                DrawGrid(frame);
            },
            .visibilityProvider = {},
        });
        m_model.Resume();
    }

    void OnUpdate(const anygine::engine::FrameTiming&) override
    {
        if (!m_vulkan.has_value() || !m_renderer.has_value() || !m_ui.has_value())
        {
            return;
        }

        m_ui->BeginFrame();
        (void)m_model.Advance();

        const auto& swapchain = m_vulkan->GetInfo().swapchain;
        const std::uint32_t framebufferWidth = std::max(swapchain.extent.width, 1U);
        const std::uint32_t framebufferHeight = std::max(swapchain.extent.height, 1U);
        anygine::renderer::RenderFrameRequest request{};
        request.view.clearColor = {0.015F, 0.025F, 0.045F, 1.0F};
        request.view.projection = anygine::math::BuildMainViewPerspective(
            1.0471975511965976,
            static_cast<double>(framebufferWidth) / static_cast<double>(framebufferHeight),
            0.1,
            100.0);
        request.view.hasFrameUniforms = true;
        request.view.shadowsEnabled = false;
        request.framebufferWidth = framebufferWidth;
        request.framebufferHeight = framebufferHeight;
        anygine::renderer::ApplyRenderFeatureProfile(
            anygine::renderer::BuildBasicRenderFeatureProfile(), request.view);

        if (!m_renderer->RenderFrame(request))
        {
            m_ui->FinishFrame(false);
            m_renderFailed = true;
            return;
        }
        ++m_presentedFrameCount;
    }

    void OnStop() override
    {
        if (m_vulkan.has_value())
        {
            (void)m_vulkan->WaitUntilDeviceIdle();
            const auto validation = m_vulkan->GetValidationDiagnostics();
            m_validationRequested = validation.has_value() && validation->requested;
            m_validationEnabled = validation.has_value() && validation->enabled;
            m_validationErrorCount =
                validation.has_value() ? validation->errorMessageCount : UINT64_MAX;
        }

        m_ui.reset();
        if (m_renderer.has_value())
        {
            (void)m_renderer->Shutdown();
        }
        m_renderer.reset();
        m_vulkan.reset();
    }

    [[nodiscard]] bool Succeeded() const noexcept
    {
        return !m_renderFailed && m_presentedFrameCount == kSmokeFrameCount &&
               m_validationRequested && m_validationEnabled && m_validationErrorCount == 0U &&
               m_model.Generation() == kSmokeFrameCount && m_model.LiveCount() == 5U;
    }

    void PrintResult() const
    {
        std::cout << "BraveNewWorld life-game: validation="
                  << (m_validationRequested ? "requested" : "not-requested") << "/"
                  << (m_validationEnabled ? "enabled" : "disabled")
                  << " errors=" << m_validationErrorCount
                  << " presented=" << m_presentedFrameCount
                  << " generation=" << m_model.Generation()
                  << " live=" << m_model.LiveCount() << " grid=24x24 ui=enabled\n";
    }

private:
    void DrawControls(anygine::ui::IUiFrame& frame)
    {
        if (DrawButton(frame, m_model.IsPaused() ? "Resume" : "Pause"))
        {
            m_model.TogglePaused();
        }
        if (DrawButton(frame, "Single Step"))
        {
            m_model.Pause();
            m_model.SingleStep();
        }
        if (DrawButton(frame, "Reset"))
        {
            m_model.Reset();
        }

        const std::string status =
            "Generation: " + std::to_string(m_model.Generation()) +
            "  Live: " + std::to_string(m_model.LiveCount()) +
            "  State: " + (m_model.IsPaused() ? "paused" : "running");
        frame.Text(status.c_str());
        frame.Text("24 x 24 toroidal grid - Conway B3/S23 - # alive, . dead");
    }

    void DrawGrid(anygine::ui::IUiFrame& frame) const
    {
        for (std::size_t row = 0U; row < LifeGameModel::kRows; ++row)
        {
            std::string line;
            line.reserve(LifeGameModel::kColumns * 2U);
            for (std::size_t column = 0U; column < LifeGameModel::kColumns; ++column)
            {
                line += m_model.IsAlive(row, column) ? "# " : ". ";
            }
            frame.Text(line.c_str());
        }
    }

    LifeGameModel m_model;
    std::optional<anygine::graphics::vulkan::VulkanBackend> m_vulkan;
    std::optional<anygine::renderer::Renderer> m_renderer;
    std::optional<anygine::ui::UiContext> m_ui;
    std::uint64_t m_presentedFrameCount = 0U;
    std::uint64_t m_validationErrorCount = UINT64_MAX;
    bool m_validationRequested = false;
    bool m_validationEnabled = false;
    bool m_renderFailed = false;
};
} // namespace

int main()
{
    try
    {
        LifeGameApplication application;
        const int runResult = anygine::engine::RunApplication(
            application,
            anygine::engine::ApplicationConfig{
                .title = "BraveNewWorld Life Game",
                .initialWindowExtent = {960U, 720U},
                .maxFrameCount = LifeGameApplication::kSmokeFrameCount,
            });
        application.PrintResult();
        return runResult == 0 && application.Succeeded() ? 0 : 1;
    }
    catch (const std::exception& exception)
    {
        std::cerr << "BraveNewWorld life-game failed: " << exception.what() << '\n';
        return 2;
    }
}
