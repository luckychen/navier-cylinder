cmake_minimum_required(VERSION 3.8)

project(NavierStokesCylinderFlow CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
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

# Compiler flags
if(UNIX AND NOT APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3 -march=native")
endif()

# Main executable
add_executable(navier_solver navier_solver.cpp)

# Link libraries
if(MPI_FOUND)
  target_link_libraries(navier_solver
    PRIVATE
      mfem
      MPI::MPI_CXX
      m  # math library
  )
else()
  target_link_libraries(navier_solver
    PRIVATE
      mfem
      m  # math library
  )
endif()

# Include directories for target
target_include_directories(navier_solver
  PRIVATE
    "${MFEM_SOURCE_DIR}"
    "${MFEM_BUILD_DIR}"
    "${MPI_INCLUDE_PATH}"
)

# Optional: Preprocessing for mesh generation
add_custom_target(generate_mesh
  COMMAND python3 generate_mesh.py
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  COMMENT "Generating cylinder mesh..."
)

# Make navier_solver depend on mesh generation
add_dependencies(navier_solver generate_mesh)

# Installation targets
install(TARGETS navier_solver DESTINATION bin)
install(FILES cylinder.mesh DESTINATION share)
install(FILES generate_mesh.py DESTINATION share)

# Custom target to run simulation
add_custom_target(run_simulation
  COMMAND mpirun -np 1 ./navier_solver -r 0 -Re 1000 -dt 0.001 -t 100
  DEPENDS navier_solver
  COMMENT "Running Navier-Stokes simulation..."
)

# Verbose output
message(STATUS "MFEM_DIR: ${MFEM_DIR}")
message(STATUS "MPI_CXX_COMPILER: ${MPI_CXX_COMPILER}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
