# @Time    : 2025/01/17
# @Author  : toisard

# region 导入库

import os
import time
import subprocess
from cryptography.fernet import Fernet
from loguru import logger
import pretty_errors


# endregion
# region 配置日志
# 日志文件的名称格式为"hls_YYYY-MM-DD.log"，其中YYYY-MM-DD是当前日期
# rotation参数设置为"10 MB"，表示当日志文件大小达到10MB时，自动创建一个新的日志文件
logger.add(f"hls_{time.strftime("%Y-%m-%d")}.log", rotation="10 MB")


# endregion
# region 生成密钥
def generate_key(path):
    """
    生成一个新的 Fernet 密钥，并将其保存到指定的文件路径。

    参数:
        path (str): 保存密钥的文件路径。

    返回:
        bytes: 生成的 Fernet 密钥。
    """
    # 使用 Fernet 库生成一个新的密钥
    key = Fernet.generate_key()
    # 检查指定路径的文件夹是否存在，如果不存在则创建
    if not os.path.exists(path):
        os.makedirs(path)
    # 以二进制写入模式打开指定路径的文件
    with open(path, "wb") as key_file:
        # 将生成的密钥写入文件
        key_file.write(key)
    # 记录日志信息，表示密钥已生成并保存到指定路径
    logger.info(f"密钥已生成并保存到: {path}")
    # 返回生成的密钥
    return key


# endregion
# region 加载密钥
def load_key(path):
    """
    从指定路径加载 Fernet 密钥。

    参数:
        path (str): 密钥文件的路径。

    返回:
        bytes: 从文件中读取的 Fernet 密钥。
    """
    # 检查指定路径的文件是否存在
    if not os.path.exists(path):
        # 如果文件不存在，则打印错误信息并返回 None
        print("密钥文件不存在")
        logger.error(f"密钥文件不存在: {path}")
        return None
    # 以二进制读取模式打开指定路径的文件
    with open(path, "rb") as key_file:
        # 读取文件内容并将其赋值给变量 key
        key = key_file.read()
    # 记录日志信息，表示密钥已加载
    logger.info(f"密钥已加载: {path}")
    # 返回读取到的密钥
    return key


# endregion
# region 加密文件
def encrypt_file(file_path, key):
    """
    使用提供的密钥加密文件。

    参数:
        file_path (str): 要加密的文件的路径。
        key (str): 用于加密的密钥。

    返回:
        None
    """
    # 创建一个 Fernet 对象，用于加密和解密数据
    fernet = Fernet(key)
    # 以二进制读取模式打开文件
    with open(file_path, "rb") as file:
        # 读取文件内容
        original = file.read()
    # 使用 Fernet 对象加密文件内容
    encrypted = fernet.encrypt(original)
    # 以二进制写入模式打开文件
    with open(file_path, "wb") as encrypted_file:
        # 将加密后的内容写入文件
        encrypted_file.write(encrypted)


# endregion
# region 解密文件
def decrypt_file(file_path, key):
    """
    使用提供的密钥解密文件。

    参数:
        file_path (str): 要解密的文件的路径。
        key (str): 用于解密的密钥。

    返回:
        None
    """
    # 创建一个 Fernet 对象，用于加密和解密数据
    fernet = Fernet(key)
    # 以二进制读取模式打开文件
    with open(file_path, "rb") as enc_file:
        # 读取加密后的文件内容
        encrypted = enc_file.read()
    # 使用 Fernet 对象解密文件内容
    decrypted = fernet.decrypt(encrypted)
    # 以二进制写入模式打开文件
    with open(file_path, "wb") as dec_file:
        # 将解密后的内容写入文件
        dec_file.write(decrypted)


# endregion
# region 切片视频为HLS格式
def slice_video(input_folder, output_folder, segment_duration=10):
    """
    切片视频为HLS格式，支持mp4,mkv,avi格式。

    该函数使用FFmpeg将输入视频文件切片为HLS格式，每个切片的时长为10秒。
    切片后的视频文件将存储在指定的输出目录中，并且会生成一个名为index.m3u8的播放列表文件。

    参数:
        input_folder (str): 输入视频文件的路径。
        output_folder (str): 输出目录的路径，切片后的视频文件将存储在此目录中。

    返回:
        None
    """
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print("输入文件夹不存在")
        logger.error(f"输入文件夹不存在: {input_folder}")
        return
    # 检查输入文件夹是否为空
    if not os.listdir(input_folder):
        print("输入文件夹为空")
        logger.error(f"输入文件夹为空: {input_folder}")
        return
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        return
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件是否为mp4,mkv,avi格式
        if (
            filename.endswith(".mp4")
            or filename.endswith(".mkv")
            or filename.endswith(".avi")
        ):
            # 构建输入文件的完整路径
            input_file = os.path.join(input_folder, filename)
            # 构建输出文件的路径，使用文件名作为文件夹名
            output_folder = os.path.join(output_folder, os.path.splitext(filename)[0])
            # 检查输出文件夹是否存在，如果不存在则创建
            os.makedirs(output_folder)
            # 使用FFmpeg命令行工具切片视频
            # -i 指定输入文件
            # -codec: copy 表示直接复制视频和音频流，不进行重新编码
            # -start_number 0 设置切片的起始编号为0
            # -hls_time 10 设置每个切片的时长为10秒
            # -hls_list_size 0 表示播放列表中包含所有切片
            # -f hls 指定输出格式为HLS
            # {output_folder}/videolist.m3u8 指定输出的播放列表文件路径
            command = [
                "ffmpeg",
                "-i",
                input_file,
                "-codec:v",
                "copy",
                "-codec:a",
                "copy",
                "-start_number",
                "0",
                "-hls_time",
                f"{segment_duration}",
                "-hls_list_size",
                "0",
                "-f",
                "hls",
                f"{output_folder}/videolist.m3u8",
            ]
            # 使用subprocess.run执行FFmpeg命令，避免使用shell=True
            subprocess.run(command)
            # 记录日志信息，表示视频切片完成
            logger.info(f"视频切片完成: {input_file} >>> {output_folder}")
        else:
            # 如果文件不是mp4,mkv,avi格式，则跳过
            continue


# endregion
# region 加密HLS视频切片
def encrypt_video(input_folder, key):
    """
    加密HLS视频切片。

    该函数使用提供的密钥加密HLS视频切片，并将加密后的切片存储在指定的输出目录中。

    参数:
        input_folder (str): 输入HLS视频切片的路径。
        key (str): 用于加密的密钥。
    返回:
        None
    """
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print("输入文件夹不存在")
        logger.error(f"输入文件夹不存在: {input_folder}")
        return
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件是否为.ts 格式（HLS 视频切片文件）
        if filename.endswith(".ts"):
            # 构建输入文件的完整路径
            input_file = os.path.join(input_folder, filename)
            # 对每个.ts 文件进行加密，使用提供的密钥
            encrypt_file(input_file, key)
            print(f"已加密 {filename}")
    # 记录日志信息，表示视频加密完成
    logger.info(f"视频加密完成: {input_folder}")


# endregion
# region 解密HLS视频切片
def decrypt_video(input_folder, key):
    """
    解密HLS视频切片。

    该函数使用提供的密钥解密HLS视频切片，并将解密后的切片存储在指定的输出目录中。

    参数:
        input_folder (str): 输入HLS视频切片的路径。
        key (str): 用于解密的密钥。
    返回:
        None
    """
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print("输入文件夹不存在")
        logger.error(f"输入文件夹不存在: {input_folder}")
        return
    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        # 检查文件是否为.ts 格式（HLS 视频切片文件）
        if filename.endswith(".ts"):
            # 构建输入文件的完整路径
            input_file = os.path.join(input_folder, filename)
            # 对每个.ts 文件进行解密，使用提供的密钥
            decrypt_file(input_file, key)
            print(f"已解密 {filename}")
    # 记录日志信息，表示视频解密完成
    logger.info(f"视频解密完成: {input_folder}")


# endregion
# region 测试
start_time = time.time()
if __name__ == "__main__":
    # 生成密钥
    # key = generate_key("/")
    # 加载密钥
    key = load_key("Files/HLS/videolist.key")
    # 切片视频
    slice_video("Files/HLS", "Files/HLS", 10)
    # 加密视频切片
    # encrypt_video("Files/HLS/", key)
    # 解密视频切片
    # decrypt_video("Files/HLS/", key)
    # 计算运行时间
    end_time = time.time()
    elapsed_time = f"操作耗时:{end_time - start_time}秒"
    print(elapsed_time)
    logger.debug(elapsed_time)
# endregion
