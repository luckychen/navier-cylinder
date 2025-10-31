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
# User can specify MFEM_DIR via command line: cmake -DMFEM_DIR=/path/to/mfem ..
# Or it will look for mfem-src in parent directories
if(NOT MFEM_DIR)
  # Try to find MFEM automatically - look for libmfem.a in build dir or root
  find_file(MFEM_LIB_FILE libmfem.a PATHS
    "${CMAKE_CURRENT_SOURCE_DIR}/../mfem-src/build"
    "${CMAKE_CURRENT_SOURCE_DIR}/../mfem-src"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../mfem-src/build"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../mfem-src"
    "$ENV{HOME}/mfem-src/build"
    "$ENV{HOME}/mfem-src"
    "$ENV{HOME}/mfem/mfem-src/build"
    "$ENV{HOME}/mfem/mfem-src"
    NO_DEFAULT_PATH
  )

  if(MFEM_LIB_FILE)
    get_filename_component(MFEM_BUILD_DIR_FOUND "${MFEM_LIB_FILE}" DIRECTORY)
    # Get parent directory (source dir)
    get_filename_component(MFEM_DIR "${MFEM_BUILD_DIR_FOUND}" DIRECTORY)
    # If libmfem.a was in the source dir itself (not build/), use it as source dir
    if(NOT EXISTS "${MFEM_DIR}/fem")
      set(MFEM_DIR "${MFEM_BUILD_DIR_FOUND}")
    endif()
    message(STATUS "Found MFEM at: ${MFEM_DIR}")
  else()
    message(FATAL_ERROR "MFEM not found. Please specify -DMFEM_DIR=/path/to/mfem when running cmake")
  endif()
endif()

# Check if MFEM exists (CMake or Make build)
set(MFEM_SOURCE_DIR "${MFEM_DIR}")
set(MFEM_BUILD_DIR "${MFEM_DIR}/build")

# Check for CMake-built MFEM first, then Make-built
if(EXISTS "${MFEM_BUILD_DIR}/libmfem.a")
  set(MFEM_LIB "${MFEM_BUILD_DIR}/libmfem.a")
  message(STATUS "Found CMake-built MFEM at: ${MFEM_BUILD_DIR}")
elseif(EXISTS "${MFEM_DIR}/libmfem.a")
  set(MFEM_LIB "${MFEM_DIR}/libmfem.a")
  set(MFEM_BUILD_DIR "${MFEM_DIR}")
  message(STATUS "Found Make-built MFEM at: ${MFEM_DIR}")
else()
  message(FATAL_ERROR "MFEM library not found in ${MFEM_DIR}")
endif()

# If MFEM not built, we'll build it
if(NOT EXISTS "${MFEM_LIB}")
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
# Look in the current conda environment first
if(DEFINED ENV{CONDA_PREFIX})
  link_directories("$ENV{CONDA_PREFIX}/lib")
  include_directories("$ENV{CONDA_PREFIX}/include")
endif()

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
