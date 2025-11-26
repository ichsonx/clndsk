#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
from pathlib import Path

# 硬编码的关键字数组 - 任务完成后手动填充
keypoint = [".dat","赌",".zip","台 妹 子 線 上 現 場 直 播 各",".html",".exe",".apk","催情神药","宇宙最丰富完整","最 齐 全 H 漫 画","最好看.mp4","最强大.mp4",".rar"]

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
            # 使用os.walk()进行递归遍历，更好地处理编码问题
            for root, dirs, files in os.walk(str(target_path)):
                for filename in files:
                    try:
                        file_path = Path(root) / filename
                        # 检查文件名是否包含任意关键字
                        if any(keyword in filename for keyword in keypoint):
                            # 增强验证：检查文件是否实际存在且可访问
                            if file_path.exists() and file_path.is_file():
                                matched_files.append(file_path)
                            else:
                                # 使用更安全的文件名显示方法
                                try:
                                    safe_name = filename.encode('utf-8', errors='replace').decode('utf-8')
                                    print_red(f"跳过不可访问的文件: {safe_name}")
                                except:
                                    print_red(f"跳过不可访问的文件: [文件名编码错误]")
                    except (UnicodeDecodeError, OSError) as e:
                        # 跳过无法处理的单个文件，继续处理其他文件
                        try:
                            safe_name = filename.encode('utf-8', errors='replace').decode('utf-8')
                            print_red(f"跳过无法处理的文件: {safe_name} - {e}")
                        except:
                            print_red(f"跳过无法处理的文件: [文件名编码错误] - {e}")
                        continue
        else:
            # 使用os.listdir()进行非递归遍历
            try:
                for item in os.listdir(str(target_path)):
                    item_path = target_path / item
                    if item_path.is_file():
                        try:
                            # 检查文件名是否包含任意关键字
                            if any(keyword in item for keyword in keypoint):
                                # 增强验证：检查文件是否实际存在且可访问
                                if item_path.exists() and item_path.is_file():
                                    matched_files.append(item_path)
                                else:
                                    # 使用更安全的文件名显示方法
                                    try:
                                        safe_name = item.encode('utf-8', errors='replace').decode('utf-8')
                                        print_red(f"跳过不可访问的文件: {safe_name}")
                                    except:
                                        print_red(f"跳过不可访问的文件: [文件名编码错误]")
                        except (UnicodeDecodeError, OSError) as e:
                            # 跳过无法处理的单个文件，继续处理其他文件
                            try:
                                safe_name = item.encode('utf-8', errors='replace').decode('utf-8')
                                print_red(f"跳过无法处理的文件: {safe_name} - {e}")
                            except:
                                print_red(f"跳过无法处理的文件: [文件名编码错误] - {e}")
                            continue
            except (UnicodeDecodeError, OSError) as e:
                print_red(f"遍历目录时发生错误: {e}")
                return []
                    
    except Exception as e:
        # 使用更安全的错误显示方法
        try:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print_red(f"遍历文件时发生错误: {error_msg}")
        except:
            print_red(f"遍历文件时发生错误: [错误信息编码错误]")
        return []
    
    return matched_files

def get_mount_info_for_path(path):
    """获取指定路径的挂载信息"""
    try:
        abs_path = os.path.abspath(path)
        result = subprocess.run(['df', abs_path], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                return lines[1]  # 第二行包含磁盘信息
        return None
    except:
        return None

def is_ntfs_volume(path):
    """检查路径是否在NTFS卷上"""
    try:
        mount_info = get_mount_info_for_path(path)
        if mount_info:
            # 检查挂载信息中是否包含NTFS相关标识
            return 'ntfs' in mount_info.lower() or 'tuxera' in mount_info.lower()
        return False
    except:
        return False

def check_file_locked(filepath):
    """检查文件是否被其他进程锁定"""
    try:
        # 尝试以读写模式打开文件，如果失败则可能被锁定
        with open(filepath, 'r+b') as f:
            return False
    except (PermissionError, OSError):
        return True

def delete_files(file_list):
    """删除文件列表"""
    deleted_count = 0
    error_count = 0
    total_files = len(file_list)
    
    # 检查是否在NTFS卷上
    ntfs_detected = False
    if file_list:
        ntfs_detected = is_ntfs_volume(str(file_list[0]))
        if ntfs_detected:
            print("检测到NTFS文件系统，使用增强删除模式")
    
    for index, file_path in enumerate(file_list, 1):
        # 重试机制
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # 显示删除进度，使用安全的编码处理
                safe_filename = str(file_path.name).encode('utf-8', errors='replace').decode('utf-8')
                if retry_count > 0:
                    print(f"[{index}/{total_files}] 正在重试删除: {safe_filename} (第{retry_count+1}次)")
                else:
                    print(f"[{index}/{total_files}] 正在删除: {safe_filename}")
                
                # 改进的删除逻辑：使用绝对路径字符串进行删除
                # 避免Path对象在处理特殊字符时的编码问题
                absolute_path = str(file_path.resolve())
                
                # 多重验证：检查文件是否存在且可访问
                if not os.path.exists(absolute_path):
                    print_red(f"    ✗ 文件不存在: {safe_filename}")
                    error_count += 1
                    break  # 不再重试
                    
                # 检查文件权限
                if not os.access(absolute_path, os.W_OK):
                    print_red(f"    ✗ 文件无写权限: {safe_filename}")
                    error_count += 1
                    break  # 不再重试
                    
                # 检查文件是否被锁定
                if check_file_locked(absolute_path):
                    print_red(f"    ✗ 文件被锁定: {safe_filename}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # 等待1秒后重试
                    continue  # 尝试重试
                else:
                    # 文件未被锁定，继续删除
                    pass
                
                # 对于NTFS文件系统，尝试先解锁文件
                if ntfs_detected:
                    try:
                        # 尝试使用subprocess解锁文件
                        subprocess.run(['chflags', 'nouchg', absolute_path], check=False)
                        subprocess.run(['xattr', '-c', absolute_path], check=False)  # 清除扩展属性
                    except:
                        pass  # 如果解锁失败，继续尝试删除
                
                # 使用os.remove进行删除，处理编码问题
                os.remove(absolute_path)
                
                # 验证文件是否确实被删除
                if not os.path.exists(absolute_path):
                    safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                    print_green(f"    ✓ 已删除: {safe_path}")
                    deleted_count += 1
                    success = True
                else:
                    # 删除失败，使用系统命令作为备选方法
                    print_red(f"    ✗ 文件删除失败，尝试使用系统命令: {safe_filename}")
                    
                    if ntfs_detected:
                        # 对于NTFS卷，使用系统rm命令作为备选
                        result = subprocess.run(['rm', '-f', absolute_path], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and not os.path.exists(absolute_path):
                            safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                            print_green(f"    ✓ 已使用系统命令删除: {safe_path}")
                            deleted_count += 1
                            success = True
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                import time
                                time.sleep(1)  # 等待1秒后重试
                            else:
                                safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                                print_red(f"    ✗ 系统命令删除失败: {safe_path}")
                                error_count += 1
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            error_count += 1
                            
            except PermissionError as e:
                # 处理权限错误，尝试使用系统命令
                safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                print_red(f"    ✗ 权限不足无法删除 {safe_path}: {e}")
                
                # 尝试使用系统命令删除
                try:
                    result = subprocess.run(['rm', '-f', absolute_path], 
                                          capture_output=True, text=True)
                    if result.returncode == 0 and not os.path.exists(absolute_path):
                        print_green(f"    ✓ 已使用系统命令删除: {safe_path}")
                        deleted_count += 1
                        success = True
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            print_red(f"    ✗ 系统命令也删除失败: {safe_path}")
                            error_count += 1
                except Exception as system_cmd_error:
                    print_red(f"    ✗ 系统命令执行异常: {system_cmd_error}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        error_count += 1
                    
            except FileNotFoundError:
                # 文件不存在，跳过
                safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                print_red(f"    ✗ 文件不存在 {safe_path}")
                error_count += 1
                break  # 不再重试
                
            except OSError as e:
                # 处理操作系统错误，尝试使用系统命令
                safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                print_red(f"    ✗ 系统错误删除失败 {safe_path}: {e}")
                
                # 尝试使用系统命令删除
                try:
                    if ntfs_detected:
                        result = subprocess.run(['rm', '-f', absolute_path], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and not os.path.exists(absolute_path):
                            print_green(f"    ✓ 已使用系统命令删除: {safe_path}")
                            deleted_count += 1
                            success = True
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                import time
                                time.sleep(1)  # 等待1秒后重试
                            else:
                                print_red(f"    ✗ 系统命令也删除失败: {safe_path}")
                                error_count += 1
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            error_count += 1
                except Exception as system_cmd_error:
                    print_red(f"    ✗ 系统命令执行异常: {system_cmd_error}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        error_count += 1
                    
            except Exception as e:
                # 处理其他异常，尝试使用系统命令
                safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
                print_red(f"    ✗ 未知错误删除失败 {safe_path}: {e}")
                
                # 尝试使用系统命令删除
                try:
                    if ntfs_detected:
                        result = subprocess.run(['rm', '-f', absolute_path], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and not os.path.exists(absolute_path):
                            print_green(f"    ✓ 已使用系统命令删除: {safe_path}")
                            deleted_count += 1
                            success = True
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                import time
                                time.sleep(1)  # 等待1秒后重试
                            else:
                                print_red(f"    ✗ 系统命令也删除失败: {safe_path}")
                                error_count += 1
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(1)  # 等待1秒后重试
                        else:
                            error_count += 1
                except Exception as system_cmd_error:
                    print_red(f"    ✗ 系统命令执行异常: {system_cmd_error}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # 等待1秒后重试
                    else:
                        error_count += 1
    
    return deleted_count, error_count

def find_empty_folders(target_path, recursive):
    """查找空文件夹"""
    empty_folders = []
    
    try:
        if recursive:
            # 使用os.walk()进行递归遍历，更好地处理编码问题
            for root, dirs, files in os.walk(str(target_path)):
                folder_path = Path(root)
                # 检查文件夹是否为空
                try:
                    # 使用os.listdir()检查文件夹内容
                    contents = os.listdir(str(folder_path))
                    if not contents:
                        empty_folders.append(folder_path)
                except (PermissionError, OSError, UnicodeDecodeError) as e:
                    # 跳过无法访问的文件夹
                    continue
        else:
            # 使用os.listdir()进行非递归遍历
            try:
                for item in os.listdir(str(target_path)):
                    item_path = target_path / item
                    if item_path.is_dir():
                        try:
                            # 检查文件夹是否为空
                            contents = os.listdir(str(item_path))
                            if not contents:
                                empty_folders.append(item_path)
                        except (PermissionError, OSError, UnicodeDecodeError) as e:
                            # 跳过无法访问的文件夹
                            continue
            except (UnicodeDecodeError, OSError) as e:
                print_red(f"遍历目录时发生错误: {e}")
                return []
                    
    except Exception as e:
        print_red(f"遍历文件夹时发生错误: {e}")
        return []
    
    return empty_folders

def delete_empty_folders(folder_list):
    """删除空文件夹列表"""
    deleted_count = 0
    error_count = 0
    total_folders = len(folder_list)
    
    for index, folder_path in enumerate(folder_list, 1):
        try:
            # 显示删除进度，使用安全的编码处理
            safe_path = str(folder_path).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[{index}/{total_folders}] 正在删除空文件夹: {safe_path}")
            
            folder_path.rmdir()  # 删除空文件夹
            
            print_green(f"    ✓ 已删除空文件夹: {safe_path}")
            deleted_count += 1
        except Exception as e:
            safe_path = str(folder_path).encode('utf-8', errors='replace').decode('utf-8')
            print_red(f"    ✗ 删除空文件夹失败 {safe_path}: {e}")
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
    
    # TASK-1.1: 询问用户是否在清理文件完毕后也清理空文件夹
    print("请选择是否在清理文件完毕后也清理空文件夹：")
    print_blue("1: 是/yes")
    print_blue("2: 否/no")
    print()
    
    while True:
        try:
            clean_empty_folders_choice = input("请输入数字选择 (1 或 2): ").strip()
            
            if clean_empty_folders_choice == "1":
                clean_empty_folders = True
                print_green("选择：清理文件完毕后也清理空文件夹")
                break
            elif clean_empty_folders_choice == "2":
                clean_empty_folders = False
                print_green("选择：不清理空文件夹")
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
        safe_path = str(file_path).encode('utf-8', errors='replace').decode('utf-8')
        print(f"  {i+1}. {safe_path}")
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
                
                # TASK-1.2: 如果用户选择了清理空文件夹，则查找并询问是否删除空文件夹
                if clean_empty_folders:
                    print()
                    print("正在搜索空文件夹...")
                    empty_folders = find_empty_folders(target_path, recursive)
                    
                    if not empty_folders:
                        print_green("未找到空文件夹")
                    else:
                        # 显示前几个空文件夹作为预览
                        print("空文件夹预览：")
                        for i, folder_path in enumerate(empty_folders[:5]):
                            safe_path = str(folder_path).encode('utf-8', errors='replace').decode('utf-8')
                            print(f"  {i+1}. {safe_path}")
                        if len(empty_folders) > 5:
                            print(f"  ... 还有 {len(empty_folders) - 5} 个空文件夹")
                        print()
                        
                        # 显示空文件夹数量
                        print_red(f"找到 {len(empty_folders)} 个空文件夹")
                        print()
                        
                        # 询问是否删除空文件夹（蓝色选项）
                        print("请确认是否删除这些空文件夹：")
                        print_blue("1: 是/yes (删除所有空文件夹)")
                        print_blue("2: 否/no (退出程序)")
                        print()
                        
                        while True:
                            try:
                                delete_empty_choice = input("请输入数字选择 (1 或 2): ").strip()
                                
                                if delete_empty_choice == "1":
                                    print()
                                    print("开始删除空文件夹...")
                                    deleted_empty_count, error_empty_count = delete_empty_folders(empty_folders)
                                    print()
                                    print_green(f"空文件夹删除完成！成功删除 {deleted_empty_count} 个空文件夹")
                                    if error_empty_count > 0:
                                        print_red(f"删除失败 {error_empty_count} 个空文件夹")
                                    break
                                    
                                elif delete_empty_choice == "2":
                                    print_green("用户选择不删除空文件夹")
                                    break
                                    
                                else:
                                    print_red("错误：请输入 1 或 2")
                                    
                            except KeyboardInterrupt:
                                print("\n\n程序被用户中断")
                                sys.exit(0)
                            except Exception as e:
                                print_red(f"发生错误: {e}")
                                sys.exit(1)
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
