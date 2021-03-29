# -*- coding: utf-8 -*-

import logging
import os
import platform
import subprocess

from notetool.tool.log import logger


def check_phone():
    """
    查看连接的手机
    """
    stdout, stderr = execute_cmd("adb devices")

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logger.info(stdout)
    return stdout, stderr


def execute_cmd(cmd):
    execute = subprocess.Popen(
        str(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = execute.communicate()
    return stdout, stderr


def copy_file_to_local(from_path='/sdcard/screenshots.png', to_path="screenshots.png"):
    """
    从手机复制文件到电脑
    :param from_path: 手机文件位置
    :param to_path: 本地文件位置
    :return:
    """
    cmd = r"adb pull " + from_path + " " + to_path
    stdout, stderr = execute_cmd(cmd)
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logger.info("copy file from " + from_path + " to " + to_path)
    return stdout, stderr


def screenshot_to_phone(file_path='/sdcard/screenshots.png'):
    """
    在手机上截图
    :param file_path: 文件保存位置
    :return:
    """
    cmd = r"adb shell /system/bin/screencap -p " + file_path
    stdout, stderr = execute_cmd(cmd)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logger.info("screenshots and save to phone " + file_path)
    return stdout, stderr


def screenshot_to_local(file_path='screenshots.png'):
    """
    在手机上截图并复制到本地
    :param file_path:
    :return:
    """
    screenshot_to_phone()
    copy_file_to_local(to_path=file_path)


def swipe(x1, y1, x2, y2):
    cmd = r"adb shell input swipe " + \
        str(x1) + " " + str(y1) + " " + str(x2) + " " + str(y2)

    stdout, stderr = execute_cmd(cmd)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    print(stdout)
    print(stderr)
    logging.info("swipe position " + str(x1) + " " +
                 str(y1) + " " + str(x2) + " " + str(y2))
    return stdout, stderr


def click(axis_x, axis_y):
    cmd = r"adb shell input tap " + str(axis_x) + " " + str(axis_y)

    stdout, stderr = execute_cmd(cmd)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    print(stdout)
    print(stderr)
    logging.info("click position " + str(axis_x) + " " + str(axis_y))
    return stdout, stderr


def connect_ip(ip, port="5555"):
    cmd = r"adb connect " + ip + ":" + port
    stdout, stderr = execute_cmd(cmd)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logging.info("connected to " + ip + ":" + port)
    return stdout, stderr


def disconnect_ip(ip, port="5555"):
    cmd = r"adb disconnect " + ip + ":" + port
    stdout, stderr = execute_cmd(cmd)

    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")

    logging.info("disconnected to " + ip + ":" + port)
    return stdout, stderr


class AutoADB():
    def __init__(self):
        try:
            adb_path = 'adb'
            subprocess.Popen([adb_path], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
            self.adb_path = adb_path
        except OSError:
            if platform.system() == 'Windows':
                adb_path = os.path.join('Tools', "adb", 'adb.exe')
                try:
                    subprocess.Popen(
                        [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.adb_path = adb_path
                except OSError:
                    pass
            else:
                try:
                    subprocess.Popen(
                        [adb_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except OSError:
                    pass
            print('请安装 ADB 及驱动并配置环境变量')
            print('具体链接: https://github.com/wangshub/wechat_jump_game/wiki')
            exit(1)

    def get_screen(self):
        process = os.popen(self.adb_path + ' shell wm size')
        output = process.read()
        return output

    def run(self, raw_command):
        command = '{} {}'.format(self.adb_path, raw_command)
        process = os.popen(command)
        output = process.read()
        return output

    def test_device(self):
        print('检查设备是否连接...')
        command_list = [self.adb_path, 'devices']
        process = subprocess.Popen(
            command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = process.communicate()
        if output[0].decode('utf8') == 'List of devices attached\n\n':
            print('未找到设备')
            print('adb 输出:')
            for each in output:
                print(each.decode('utf8'))
            exit(1)
        print('设备已连接')
        print('adb 输出:')
        for each in output:
            print(each.decode('utf8'))

    def test_density(self):
        process = os.popen(self.adb_path + ' shell wm density')
        output = process.read()
        return output

    def test_device_detail(self):
        process = os.popen(self.adb_path + ' shell getprop ro.product.device')
        output = process.read()
        return output

    def test_device_os(self):
        process = os.popen(
            self.adb_path + ' shell getprop ro.build.version.release')
        output = process.read()
        return output


"""
1： adb shell input keyevent keycode
   这条命令模拟Android手机按下了event_code对应的按键。
   event_code表如下：
0 -->  "KEYCODE_UNKNOWN"
1 -->  "KEYCODE_MENU"
2 -->  "KEYCODE_SOFT_RIGHT"
3 -->  "KEYCODE_HOME"
4 -->  "KEYCODE_BACK"
5 -->  "KEYCODE_CALL"
6 -->  "KEYCODE_ENDCALL"
7 -->  "KEYCODE_0"
8 -->  "KEYCODE_1"
9 -->  "KEYCODE_2"
10 -->  "KEYCODE_3"
11 -->  "KEYCODE_4"
12 -->  "KEYCODE_5"
13 -->  "KEYCODE_6"
14 -->  "KEYCODE_7"
15 -->  "KEYCODE_8"
16 -->  "KEYCODE_9"
17 -->  "KEYCODE_STAR"
18 -->  "KEYCODE_POUND"
19 -->  "KEYCODE_DPAD_UP"
20 -->  "KEYCODE_DPAD_DOWN"
21 -->  "KEYCODE_DPAD_LEFT"
22 -->  "KEYCODE_DPAD_RIGHT"
23 -->  "KEYCODE_DPAD_CENTER"
24 -->  "KEYCODE_VOLUME_UP"
25 -->  "KEYCODE_VOLUME_DOWN"
26 -->  "KEYCODE_POWER"
27 -->  "KEYCODE_CAMERA"
28 -->  "KEYCODE_CLEAR"
29 -->  "KEYCODE_A"
30 -->  "KEYCODE_B"
31 -->  "KEYCODE_C"
32 -->  "KEYCODE_D"
33 -->  "KEYCODE_E"
34 -->  "KEYCODE_F"
35 -->  "KEYCODE_G"
36 -->  "KEYCODE_H"
37 -->  "KEYCODE_I"
38 -->  "KEYCODE_J"
39 -->  "KEYCODE_K"
40 -->  "KEYCODE_L"
41 -->  "KEYCODE_M"
42 -->  "KEYCODE_N"
43 -->  "KEYCODE_O"
44 -->  "KEYCODE_P"
45 -->  "KEYCODE_Q"
46 -->  "KEYCODE_R"
47 -->  "KEYCODE_S"
48 -->  "KEYCODE_T"
49 -->  "KEYCODE_U"
50 -->  "KEYCODE_V"
51 -->  "KEYCODE_W"
52 -->  "KEYCODE_X"
53 -->  "KEYCODE_Y"
54 -->  "KEYCODE_Z"
55 -->  "KEYCODE_COMMA"
56 -->  "KEYCODE_PERIOD"
57 -->  "KEYCODE_ALT_LEFT"
58 -->  "KEYCODE_ALT_RIGHT"
59 -->  "KEYCODE_SHIFT_LEFT"
60 -->  "KEYCODE_SHIFT_RIGHT"
61 -->  "KEYCODE_TAB"
62 -->  "KEYCODE_SPACE"
63 -->  "KEYCODE_SYM"
64 -->  "KEYCODE_EXPLORER"
65 -->  "KEYCODE_ENVELOPE"
66 -->  "KEYCODE_ENTER"
67 -->  "KEYCODE_DEL"
68 -->  "KEYCODE_GRAVE"
69 -->  "KEYCODE_MINUS"
70 -->  "KEYCODE_EQUALS"
71 -->  "KEYCODE_LEFT_BRACKET"
72 -->  "KEYCODE_RIGHT_BRACKET"
73 -->  "KEYCODE_BACKSLASH"
74 -->  "KEYCODE_SEMICOLON"
75 -->  "KEYCODE_APOSTROPHE"
76 -->  "KEYCODE_SLASH"
77 -->  "KEYCODE_AT"
78 -->  "KEYCODE_NUM"
79 -->  "KEYCODE_HEADSETHOOK"
80 -->  "KEYCODE_FOCUS"
81 -->  "KEYCODE_PLUS"
82 -->  "KEYCODE_MENU"
83 -->  "KEYCODE_NOTIFICATION"
84 -->  "KEYCODE_SEARCH"
85 -->  "TAG_LAST_KEYCODE"
2：adb shell input tap
    这条命令模拟Android手机在屏幕坐标（X,Y）处进行了点击操作。
3：adb shell input swipe  
    这条命令模拟Android手机从屏幕坐标（X1,Y1）滑动到坐标（X2,Y2）的操作。
4、uiautomator dump   dump: creates an XML dump of current UI hierarchy 这个命令是用来成成当前界面的UI层次，并用XML格式进行展示 。这样就可以获取各个组件的位置了
注：如果PC要想同时控制多台Android手机，必须在adb 后面添加-s
例如：adb -s 13b6e4c4 shell input tap 400 400
表示对13b6e4c4这台Android手机进行在屏幕上（400,400）坐标位置进行模拟的点击事件。
"""
# check_phone()

# # screenshot_to_local()

# # click(109, 274)
# swipe(0, 500, 10, 800)
