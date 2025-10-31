cmake_minimum_required(VERSION 3.8)

project(NavierStokesCylinderFlow CXX)

# Set C++ standard (MFEM requires at least C++14, best with C++17)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Default build type
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Find MPI (optional - MFEM can work without it)
find_package(MPI QUIET)

# MFEM configuration
set(MFEM_DIR "/fs1/home/ceoas/chenchon/mfem/mfem-src" CACHE PATH "Path to MFEM source directory")

# Check if MFEM exists and is built
if(NOT EXISTS "${MFEM_DIR}")
  message(FATAL_ERROR "MFEM directory not found: ${MFEM_DIR}")
endif()

# Add MFEM library
set(MFEM_SOURCE_DIR "${MFEM_DIR}")
set(MFEM_BUILD_DIR "${MFEM_DIR}/build")

# If MFEM not built, we'll build it
if(NOT EXISTS "${MFEM_BUILD_DIR}/libmfem.a")
  message(STATUS "Building MFEM library...")
  execute_process(
    COMMAND mkdir -p build
    WORKING_DIRECTORY "${MFEM_DIR}"
  )
  execute_process(
    COMMAND cmake -DCMAKE_BUILD_TYPE=Release -DMFEM_USE_MPI=ON ..
    WORKING_DIRECTORY "${MFEM_BUILD_DIR}"
  )
  execute_process(
    COMMAND make -j4
    WORKING_DIRECTORY "${MFEM_BUILD_DIR}"
  )
endif()

# MFEM include directory
include_directories("${MFEM_SOURCE_DIR}")
include_directories("${MFEM_BUILD_DIR}")
include_directories("${MFEM_BUILD_DIR}/config")

# Link MFEM library
link_directories("${MFEM_BUILD_DIR}")

# Add conda paths for HYPRE, METIS, and other libraries
link_directories("/home/ceoas/chenchon/miniconda3_x86/envs/mfem/lib")

# Compiler flags
if(UNIX AND NOT APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3 -march=native")
endif()

# Main executable: Simplified Navier-Stokes solver
add_executable(navier_simple navier_simple.cpp)

# Link libraries
if(MPI_FOUND)
  target_link_libraries(navier_simple
    PRIVATE
      mfem
      MPI::MPI_CXX
      HYPRE
      metis
      m  # math library
  )
else()
  target_link_libraries(navier_simple
    PRIVATE
      mfem
      HYPRE
      metis
      m  # math library
  )
endif()

# Include directories for target
target_include_directories(navier_simple
  PRIVATE
    "${MFEM_SOURCE_DIR}"
    "${MFEM_BUILD_DIR}"
    "${MPI_INCLUDE_PATH}"
)

# Installation targets
install(TARGETS navier_simple DESTINATION bin)

# Verbose output
message(STATUS "MFEM_DIR: ${MFEM_DIR}")
message(STATUS "MPI_CXX_COMPILER: ${MPI_CXX_COMPILER}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Target: navier_simple")
