# AgentRT 跨团队合约测试构建配置
# Copyright (c) 2026 SPHARX. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# 本文件构建 contract_tests 目标，验证三份跨团队合约头文件
# （contract_A_B.h / contract_A_C.h / contract_B_C.h）的可编译性
# 与二进制布局稳定性。
#
# 构建方式：
#   cmake -B build -DCMAKE_BUILD_TYPE=Release
#   cmake --build build --target contract_tests
#   ./build/contracts/contract_tests
#
# @owner team-A, team-B, team-C
# @see P0.14 跨团队合约任务

cmake_minimum_required(VERSION 3.20)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# ==================== 合约测试目标 ====================

# contract_tests: 验证三份合约头文件可独立编译，并对关键结构体
# 大小与偏移进行运行时断言。返回 0 表示全部通过。
add_executable(contract_tests
    contract_test.c
)

# 合约头文件仅依赖 C 标准库，无需链接外部库
target_link_libraries(contract_tests PRIVATE)

# 合约目录作为唯一 include 路径，确保头文件可独立编译
target_include_directories(contract_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# 启用严格警告以捕获合约中的潜在问题
if(NOT MSVC)
    target_compile_options(contract_tests PRIVATE
        -Wall
        -Wextra
        -Wpedantic
        -Werror
    )
else()
    target_compile_options(contract_tests PRIVATE /W4 /WX)
endif()

# ==================== CTest 注册 ====================

# 将合约验证注册为 CTest 测试，便于 CI 集成
if(BUILD_TESTING)
    add_test(
        NAME contract_tests
        COMMAND contract_tests
    )

    # 合约验证必须在 10 秒内完成（纯静态检查，无 IO）
    set_tests_properties(contract_tests PROPERTIES
        TIMEOUT 10
        LABELS "contracts;unit;cross-team"
        PASS_REGULAR_EXPRESSION "合约验证结果: [0-9]+/[0-9]+ 通过, 0 失败"
    )
endif()

# ==================== 头文件可编译性检查 ====================

# 为每份合约头文件添加独立的编译检查目标，
# 确保头文件可被独立包含（无隐藏依赖）。
set(CONTRACT_HEADERS
    contract_A_B.h
    contract_A_C.h
    contract_B_C.h
)

foreach(HEADER ${CONTRACT_HEADERS})
    set(CHECK_TARGET "contract_check_${HEADER}")
    string(REPLACE "." "_" CHECK_TARGET ${CHECK_TARGET})

    # 生成临时 .c 文件仅包含头文件
    set(CHECK_SRC "${CMAKE_CURRENT_BINARY_DIR}/check_${HEADER}.c")
    file(WRITE ${CHECK_SRC}
         "#include \"${HEADER}\"\nint main(void) { return 0; }\n")

    add_executable(${CHECK_TARGET} ${CHECK_SRC})
    target_include_directories(${CHECK_TARGET} PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
    )
    target_link_libraries(${CHECK_TARGET} PRIVATE)

    if(NOT MSVC)
        target_compile_options(${CHECK_TARGET} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
            -Werror
        )
    endif()

    # 注册为 CTest 测试
    if(BUILD_TESTING)
        add_test(
            NAME ${CHECK_TARGET}
            COMMAND ${CHECK_TARGET}
        )
        set_tests_properties(${CHECK_TARGET} PROPERTIES
            TIMEOUT 5
            LABELS "contracts;header-check;cross-team"
        )
    endif()
endforeach()

# ==================== 状态输出 ====================

message(STATUS "[Contracts] 跨团队合约测试已配置:")
message(STATUS "[Contracts]   contract_tests 目标: 验证结构体大小与偏移")
message(STATUS "[Contracts]   头文件可编译性检查: ${CONTRACT_HEADERS}")
message(STATUS "[Contracts]   合约版本: A_B=1.0.0 A_C=1.0.0 B_C=1.0.0")
