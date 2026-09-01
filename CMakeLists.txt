cmake_minimum_required(VERSION 3.24)

project(BraveNewWorld LANGUAGES CXX)

set(BNW_EXPECTED_ANYGINE_COMMIT
    "28b4934c24fdad6b8f45b945a89a6ada51703f5d"
    CACHE STRING "Source commit required by the BraveNewWorld engine contract")

if(NOT DEFINED ANYGINE_SOURCE_ROOT)
    message(FATAL_ERROR "Configure with -DANYGINE_SOURCE_ROOT=<absolute pinned Anygine checkout>.")
endif()
if(NOT IS_ABSOLUTE "${ANYGINE_SOURCE_ROOT}")
    message(FATAL_ERROR "ANYGINE_SOURCE_ROOT must be absolute.")
endif()
if(NOT EXISTS "${ANYGINE_SOURCE_ROOT}/CMakeLists.txt")
    message(FATAL_ERROR "ANYGINE_SOURCE_ROOT does not identify an Anygine checkout.")
endif()

find_package(Git REQUIRED)
execute_process(
    COMMAND "${GIT_EXECUTABLE}" -C "${ANYGINE_SOURCE_ROOT}" rev-parse HEAD
    OUTPUT_VARIABLE BNW_ACTUAL_ANYGINE_COMMIT
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY)
if(NOT BNW_ACTUAL_ANYGINE_COMMIT STREQUAL BNW_EXPECTED_ANYGINE_COMMIT)
    message(FATAL_ERROR
        "Anygine revision mismatch: expected ${BNW_EXPECTED_ANYGINE_COMMIT}, "
        "found ${BNW_ACTUAL_ANYGINE_COMMIT}.")
endif()

set(ANYGINE_BUILD_APPLICATIONS OFF CACHE BOOL "" FORCE)
set(ANYGINE_BUILD_BENCHMARKS OFF CACHE BOOL "" FORCE)
set(ANYGINE_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(ANYGINE_BUILD_PROFILER_SANDBOX OFF CACHE BOOL "" FORCE)
set(ANYGINE_BUILD_RAY_TRACING_EXPERIMENT OFF CACHE BOOL "" FORCE)
set(ANYGINE_ENABLE_USD OFF CACHE BOOL "" FORCE)
set(ANYGINE_MUJOCO_BACKEND OFF CACHE BOOL "" FORCE)
set(ANYGINE_PHYSICS_JOLT_BACKEND OFF CACHE BOOL "" FORCE)
set(ANYGINE_BUILD_SHADERS ON CACHE BOOL "" FORCE)

add_subdirectory("${ANYGINE_SOURCE_ROOT}" "${CMAKE_CURRENT_BINARY_DIR}/anygine")
add_subdirectory(Source/Apps/HelloTask)

add_custom_target(BraveNewWorldBuildAll)
add_dependencies(BraveNewWorldBuildAll BraveNewWorldHelloTask)

enable_testing()
find_package(Python3 3.11 REQUIRED COMPONENTS Interpreter)
add_test(
    NAME BraveNewWorldManifestContract
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/Tests/ManifestContract.py"
            "${CMAKE_CURRENT_SOURCE_DIR}")
set_tests_properties(BraveNewWorldManifestContract PROPERTIES LABELS "contract")
