#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path

# 硬编码的关键字数组 - 任务完成后手动填充
keypoint = ["美女","赌","在线","www",".html",".exe"]

def print_blue(text):
    """打印蓝色文本"""
    print(f"\033[94m{text}\033[0m")

def print_green(text):
    """打印绿色文本"""
    print(f"\033[92m{text}\033[0m")

def print_red(text):
    """打印红色文本"""
    print(f"\033[91m{text}\033[0m")

def validate_path(path_str):
    """验证路径是否存在"""
    try:
        path = Path(path_str)
        if path.exists():
            return path.resolve()
        else:
            return None
    except Exception:
        return None

def find_matching_files(target_path, recursive):
    """查找包含关键字的文件"""
    matched_files = []
    
    try:
        if recursive:
            # 递归遍历所有目录
            file_iterator = target_path.rglob("*")
        else:
            # 仅遍历当前目录
            file_iterator = target_path.glob("*")
        
        for file_path in file_iterator:
            if file_path.is_file():
                # 检查文件名是否包含任意关键字
                filename = file_path.name
                if any(keyword in filename for keyword in keypoint):
                    matched_files.append(file_path)
                    
    except Exception as e:
        print_red(f"遍历文件时发生错误: {e}")
        return []
    
    return matched_files

def delete_files(file_list):
    """删除文件列表"""
    deleted_count = 0
    error_count = 0
    total_files = len(file_list)
    
    for index, file_path in enumerate(file_list, 1):
        try:
            # 显示删除进度
            print(f"[{index}/{total_files}] 正在删除: {file_path.name}")
            file_path.unlink()  # 删除文件
            print_green(f"    ✓ 已删除: {file_path}")
            deleted_count += 1
        except Exception as e:
            print_red(f"    ✗ 删除失败 {file_path}: {e}")
            error_count += 1
    
    return deleted_count, error_count

def main():
    """主程序入口"""
    print("=== 文件清理工具 clndsk ===")
    print()
    
    # TASK-1.1: 询问用户清理目录选项
    print("请选择清理目录：")
    print_blue("1: 清理当前目录下文件")
    print_blue("2: 清理指定路径文件")
    print()
    
    while True:
        try:
            choice = input("请输入数字选择 (1 或 2): ").strip()
            
            if choice == "1":
                target_path = Path.cwd()
                print_green(f"选择清理当前目录: {target_path}")
                break
                
            elif choice == "2":
                path_input = input("请输入路径 (绝对路径或相对路径): ").strip()
                target_path = validate_path(path_input)
                
                if target_path:
                    print_green(f"选择清理指定目录: {target_path}")
                    break
                else:
                    print_red("错误：路径不存在，请检查后重试")
                    print("程序退出")
                    sys.exit(1)
                    
            else:
                print_red("错误：请输入 1 或 2")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print_red(f"发生错误: {e}")
            sys.exit(1)
    
    print()
    print(f"目标目录已设置为: {target_path}")
    
    # TASK-1.2: 询问用户是否递归遍历目录
    print()
    print("请选择遍历方式：")
    print_blue("1: 递归遍历所有目录")
    print_blue("2: 仅遍历当前目录")
    print()
    
    while True:
        try:
            recursive_choice = input("请输入数字选择 (1 或 2): ").strip()
            
            if recursive_choice == "1":
                recursive = True
                print_green("选择：递归遍历所有目录")
                break
            elif recursive_choice == "2":
                recursive = False
                print_green("选择：仅遍历当前目录")
                break
            else:
                print_red("错误：请输入 1 或 2")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print_red(f"发生错误: {e}")
            sys.exit(1)
    
    print()
    
    # TASK-1.4: 查找匹配文件并确认删除
    print("正在搜索包含关键字的文件...")
    matched_files = find_matching_files(target_path, recursive)
    
    if not matched_files:
        print_green("未找到包含关键字的文件")
        print("程序退出")
        sys.exit(0)
    
    # 显示前几个匹配文件作为预览
    print("匹配文件预览：")
    for i, file_path in enumerate(matched_files[:5]):
        print(f"  {i+1}. {file_path}")
    if len(matched_files) > 5:
        print(f"  ... 还有 {len(matched_files) - 5} 个文件")
    print()
    
    # 显示匹配文件数量（红色字体）- 放在预览之后，确认之前
    print_red(f"找到 {len(matched_files)} 个待删除文件")
    print()
    
    # 询问是否删除（蓝色选项）
    print("请确认是否删除这些文件：")
    print_blue("1: 是/yes (删除所有匹配文件)")
    print_blue("2: 否/no (退出程序)")
    print()
    
    while True:
        try:
            delete_choice = input("请输入数字选择 (1 或 2): ").strip()
            
            if delete_choice == "1":
                print()
                print("开始删除文件...")
                deleted_count, error_count = delete_files(matched_files)
                print()
                print_green(f"删除完成！成功删除 {deleted_count} 个文件")
                if error_count > 0:
                    print_red(f"删除失败 {error_count} 个文件")
                break
                
            elif delete_choice == "2":
                print_green("用户选择不删除文件")
                print("程序退出")
                sys.exit(0)
                
            else:
                print_red("错误：请输入 1 或 2")
                
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print_red(f"发生错误: {e}")
            sys.exit(1)
    
    print()
    print("程序执行完成")

if __name__ == "__main__":
    main()
