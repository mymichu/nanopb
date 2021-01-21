# Set the minimum version of CMake that can be used
# To find the cmake version run
# $ cmake --version
cmake_minimum_required(VERSION 3.16 FATAL_ERROR)

# Set the project name
project(NanoPbTest C CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_C_STANDARD 99)

#Include Conan
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package( Nanopb REQUIRED )

NANOPB_GENERATE_CPP(PROTO_SRCS PROTO_HDRS proto/simple.proto)

add_executable(${PROJECT_NAME} simple.c ${PROTO_SRCS} ${PROTO_HDRS})
target_include_directories(${PROJECT_NAME} PUBLIC ${NANOPB_OUT})
target_link_libraries(${PROJECT_NAME} ${CONAN_TARGETS})
conan_target_link_libraries(${PROJECT_NAME})