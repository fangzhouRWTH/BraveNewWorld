add_library(BraveNewWorldLifeGameModel Source/LifeGameModel.cpp)
target_compile_features(BraveNewWorldLifeGameModel PUBLIC cxx_std_20)
target_include_directories(BraveNewWorldLifeGameModel PUBLIC Include)

add_executable(BraveNewWorldLifeGame Source/Main.cpp)
target_compile_features(BraveNewWorldLifeGame PRIVATE cxx_std_20)
target_link_libraries(BraveNewWorldLifeGame
    PRIVATE
        BraveNewWorldLifeGameModel
        Anygine::Engine
        Anygine::GraphicsVulkan
        Anygine::RendererCore
        Anygine::RuntimeAssets
        Anygine::UI)

add_executable(BraveNewWorldLifeGameModelTests Tests/LifeGameModelTests.cpp)
target_compile_features(BraveNewWorldLifeGameModelTests PRIVATE cxx_std_20)
target_link_libraries(BraveNewWorldLifeGameModelTests PRIVATE BraveNewWorldLifeGameModel)

foreach(target
        BraveNewWorldLifeGameModel
        BraveNewWorldLifeGame
        BraveNewWorldLifeGameModelTests)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /permissive-)
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
    endif()
endforeach()
