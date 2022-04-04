import os
import html


INTERVAL = 8


def check_encoding(file_name):
    """
    只考虑utf-8和ansi编码
    """
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                line.encode("utf-8")
            f.close()
    except:
        return "ansi"
    else:
        return "utf-8"


def is_lyric(line):
    """
    歌词开头为[00:00.00],[与:中间为数字
    [ver:v1.0]之类的不是歌词
    https://github.com/ElliottSilence/LyricCapture
    的模式三自带中外歌词分离功能,没有对应中文翻译的歌词变成"//"
    """
    try:
        int(line.split("[")[1].split(":")[0])
    except:
        return False
    else:
        if line.split("]")[1].find("//") == -1:
            return True
        else:
            return False


def get_time(line):
    """
    [00:00.00]xxx -> 00:00.00
    """
    return line.split("]")[0].split("[")[1]


def get_lyric(line):
    """
    [00:00.00]xxx -> xxx
    qq音乐的韩语歌词要进行编码转换
    """
    if line.find("&#") != -1:
        return qq_music(line.split("]")[1])
    else:
        return line.split("]")[1]


def extend_time(time):
    """
    最后一句歌词的默认持续时间为INTERVAL(8秒)
    支持小数点后两位和三位时间,如00:00.00, 00:00.000
    """
    bit = len(time.split(".")[1])
    time = time_trans(time)
    time += INTERVAL
    decimal = str(time).split(".")[1]
    num = int(str(time).split(".")[0])
    minutes = str(num // 60)
    seconds = str(num % 60)
    if len(minutes) < 2:
        minutes = "0" + minutes
    if len(seconds) < 2:
        seconds = "0" + seconds
    while len(decimal) < bit:
        decimal += "0"
    return minutes + ":" + seconds + "." + decimal


def time_trans(time):
    """
    支持小数点后两位和三位时间,如00:00.00, 00:00.000
    获得每一句歌词的持续时间
    """
    if len(time.split(".")[1]) == 3:
        return (
            float(time.split(":")[0]) * 60
            + float(time.split(":")[1].split(".")[0])
            + float(time.split(".")[1]) * 0.001
        )
    else:
        return (
            float(time.split(":")[0]) * 60
            + float(time.split(":")[1].split(".")[0])
            + float(time.split(".")[1]) * 0.01
        )


def check_time(pre_time, time, pre_lyric):
    """
    显示持续时间超过INTERVAL(8秒)的歌词
    """
    if time_trans(time) - time_trans(pre_time) > INTERVAL:
        print(pre_time + " --> " + time + " " + pre_lyric.replace("\n", ""))


def qq_music(lyric):
    """
    qq音乐的韩语歌词要进行编码转换
    """
    return html.unescape(lyric)


def lrc2srt(file_name):
    n = 0
    flag = True  # 读第一行然后跳过,此后读第n行写第n-1行
    lrc_encoding = "utf-8"
    lrc_errors = ""

    if check_encoding(file_name) == "ansi":
        lrc_encoding = "ansi"
        lrc_errors = "ignore"  # 酷我音乐的韩语ansi编码歌词可能乱码

    print("\033[1;34;40m%s\033[0m" % file_name)

    with open(file_name.split(".")[0] + ".srt", "w", encoding="utf-8") as srt:
        with open(file_name, "r", encoding=lrc_encoding, errors=lrc_errors) as lrc:
            for line in lrc:
                if not is_lyric(line):  # 跳过非歌词
                    continue
                if flag:
                    pre_time = get_time(line)
                    pre_lyric = get_lyric(line)
                    flag = False
                    continue
                n += 1
                time = get_time(line)
                check_time(pre_time, time, pre_lyric)
                srt.write(
                    str(n)
                    + "\n"
                    + "00:"
                    + pre_time.replace(".", ",")
                    + " --> "
                    + "00:"
                    + time.replace(".", ",")
                    + "\n"
                    + pre_lyric
                    + "\n"
                )
                pre_time = time
                pre_lyric = get_lyric(line)
            n += 1  # 写最后一行
            srt.write(
                str(n)
                + "\n"
                + "00:"
                + pre_time.replace(".", ",")
                + " --> "
                + "00:"
                + extend_time(time).replace(".", ",")
                + "\n"
                + pre_lyric
                + "\n"
            )
        lrc.close()
    srt.close()


if __name__ == "__main__":
    count = 0
    os.system("")  # 没有这一句cmd颜色显示不出来
    print("\033[1;32;40m显示持续时间大于8秒的歌词,请注意是否为间奏,同时注意最后一句歌词(默认持续时间为8秒)\033[0m\n\n")
    for file_name in os.listdir():  # 转换当前目录中所有lrc文件
        if file_name.endswith("lrc"):
            count += 1
            lrc2srt(file_name)
            print("\n")
    if not count:
        os.system("")
        print("\033[1;31;40m当前目录下无lrc文件,请把程序与lrc歌词放在一起再运行\033[0m")
    os.system("pause")
