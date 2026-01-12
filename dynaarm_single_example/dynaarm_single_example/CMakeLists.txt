cmake_minimum_required(VERSION 3.8)
project(dynaarm_single_example)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(launch_testing_ament_cmake REQUIRED)


install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
    add_launch_test(
        launch/mock.launch.py
        TIMEOUT 60
    )
    add_launch_test(
        launch/sim.launch.py
        TIMEOUT 60
    )
endif()

ament_package()
