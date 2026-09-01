add_executable(BraveNewWorldHelloTask Source/Main.cpp)
target_compile_features(BraveNewWorldHelloTask PRIVATE cxx_std_20)
target_link_libraries(BraveNewWorldHelloTask
    PRIVATE
        Anygine::Engine
        Anygine::GraphicsVulkan
        Anygine::RendererCore
        Anygine::RuntimeAssets
        Anygine::UI)

if(MSVC)
    target_compile_options(BraveNewWorldHelloTask PRIVATE /W4 /permissive-)
else()
    target_compile_options(BraveNewWorldHelloTask PRIVATE -Wall -Wextra -Wpedantic)
endif()
