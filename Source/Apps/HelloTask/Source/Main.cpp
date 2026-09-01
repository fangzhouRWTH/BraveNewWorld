#include <Anygine/Configuration/RuntimeConfig.hpp>
#include <Anygine/Engine/Application.hpp>
#include <Anygine/Graphics/Vulkan/VulkanBackend.hpp>
#include <Anygine/Math/DepthConvention.hpp>
#include <Anygine/Renderer/RenderFeatureProfile.hpp>
#include <Anygine/Renderer/Renderer.hpp>
#include <Anygine/UI/UiContext.hpp>

#include <algorithm>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <optional>
#include <stdexcept>

#ifndef ANYGINE_GENERATED_SHADER_DIR
#error "Link Anygine::RuntimeAssets to receive the registered build-tree shader directory."
#endif

namespace
{
class HelloTaskApplication final : public anygine::engine::IApplication
{
public:
    void OnStart(anygine::platform::Window& window) override
    {
        m_vulkan.emplace(anygine::graphics::vulkan::VulkanBackendCreateInfo{
            .window = window,
            .validationMode = anygine::configuration::VulkanValidationMode::Required,
            .applicationName = "BraveNewWorld Hello Task",
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
            .id = "hello-task",
            .title = "Hello Task",
            .drawCallback =
                [](anygine::ui::IUiFrame& frame)
            {
                frame.Text("BraveNewWorld is ready for a planned small App task.");
            },
            .visibilityProvider = {},
        });
    }

    void OnUpdate(const anygine::engine::FrameTiming&) override
    {
        if (!m_vulkan.has_value() || !m_renderer.has_value() || !m_ui.has_value())
        {
            return;
        }
        m_ui->BeginFrame();

        const auto& swapchain = m_vulkan->GetInfo().swapchain;
        const std::uint32_t framebufferWidth = std::max(swapchain.extent.width, 1U);
        const std::uint32_t framebufferHeight = std::max(swapchain.extent.height, 1U);
        anygine::renderer::RenderFrameRequest request{};
        request.view.clearColor = {0.025F, 0.045F, 0.075F, 1.0F};
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
        return !m_renderFailed && m_presentedFrameCount == 3U && m_validationRequested &&
               m_validationEnabled && m_validationErrorCount == 0U;
    }

    void PrintResult() const
    {
        std::cout << "BraveNewWorld hello-task: validation="
                  << (m_validationRequested ? "requested" : "not-requested") << "/"
                  << (m_validationEnabled ? "enabled" : "disabled")
                  << " errors=" << m_validationErrorCount
                  << " presented=" << m_presentedFrameCount << " ui=enabled\n";
    }

private:
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
        HelloTaskApplication application;
        const int runResult = anygine::engine::RunApplication(
            application,
            anygine::engine::ApplicationConfig{
                .title = "BraveNewWorld Hello Task",
                .initialWindowExtent = {640U, 360U},
                .maxFrameCount = 3U,
            });
        application.PrintResult();
        return runResult == 0 && application.Succeeded() ? 0 : 1;
    }
    catch (const std::exception& exception)
    {
        std::cerr << "BraveNewWorld hello-task failed: " << exception.what() << '\n';
        return 2;
    }
}
