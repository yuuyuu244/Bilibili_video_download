# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2019/07/02--08:12
__author__ = 'Henry'

'''
项目: B站视频下载 - GUI版本
版本1: 加密API版,不需要加入cookie,直接即可下载1080p视频
20190422 - 增加多P视频单独下载其中一集的功能
20190702 - 增加视频多线程下载 速度大幅提升
20190711 - 增加GUI版本,可视化界面,操作更加友好
'''

import requests, time, hashlib, urllib.request, re, json
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
import os, sys, threading
from bs4 import BeautifulSoup

from tkinter import *
from tkinter import ttk
from tkinter import StringVar

import webbrowser
import subprocess
import shutil

root=Tk()
start_time = time.time()

PAGE_TITLE = ""
BASE_URL = ""
TYPE = "BV" # original : aid
IDDict = {'BV':'bvid', 'av':'aid'}
ID_TYPE = IDDict[TYPE]

LANG="ja"
IS_COMBINE = True

VIDEO_PATH = os.path.join(sys.path[0], 'bilibili_video')
# Refs: 
#   * https://www.bilibili.com/read/cv5263184

class LOG():
    DEBUG = 1,
    ERROR = 2

def log(log, text):
    if(LOG.DEBUG == log):
        print("[DEBUG]" + text)

# redirect output to table 
def msg_print(theText):
    theText = str(theText)
    msgbox.insert(END,theText+'\n')


# Address API site
def get_play_list(start_url, cid, quality):
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    headers = {
        'Referer': start_url,  # Attention referer
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    # print(url_api)
    print("[debug][url_api]:" + url_api)
    html = requests.get(url_api, headers=headers).json()
    
    # print(json.dumps(html))
    video_list = []
    for i in html['durl']:
        video_list.append(i['url'])
    # print(video_list)
    return video_list


# Download video
'''
 urllib.urlretrieve Callback function：
def callbackfunc(blocknum, blocksize, totalsize):
    @blocknum:  Number of downloads
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
'''
def Schedule_cmd(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    download.coords(fill_line1,(0,0,pervent*465,23))
    root.update()
    pct.set(percent_str)



def Schedule(blocknum, blocksize, totalsize):
    speed = (blocknum * blocksize) / (time.time() - start_time)
    # speed_str = " Speed: %.2f" % speed
    speed_str = " Speed: %s" % format_size(speed)
    recv_size = blocknum * blocksize

    # 设置下载进度条
    f = sys.stdout
    pervent = recv_size / totalsize
    percent_str = "%.2f%%" % (pervent * 100)
    n = round(pervent * 50)
    s = ('#' * n).ljust(50, '-')
    msg_print(percent_str.ljust(6, ' ') + '-' + speed_str)
    f.flush()
    time.sleep(2)
    # print('\r')


# 字节bytes转化K\M\G
def format_size(bytes):
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        msg_print("[ERROR]The format of the incoming bytes is incorrect")
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.3fG" % (G)
        else:
            return "%.3fM" % (M)
    else:
        return "%.3fK" % (kb)

def download_video(url, filename, num, title):
    try:
        urllib.request.urlretrieve(url=url, filename=filename,reporthook=Schedule_cmd)  # 写成mp4也行  title + '-' + num + '.flv'
        print("[FUNC][down_video][" + str(num) + "]:end")
    except urllib.error.ContentTooShortError as e:
        print("[ERROR]:fail to download due to byte data too short.")
        msg_print("[ERROR]fail to download, retry...:" + title)
        # retry
        download_video(url, filename, num, title)

#  下载视频
def down_video(video_list, page_title, title, start_url, page, num):
    print("[debug][FUNC][down_video][" + str(num) + "]:start " + title)
    msg_print('[downloading P{},wait...]:'.format(page) + page_title)
    currentVideoPath = os.path.join(VIDEO_PATH, page_title)  # 当前目录作为下载目录
    print("[debug][currentVideoPath]:" + currentVideoPath)
    #print("[video_list]:" + str(video_list))
    print("[debug]video_list", end="")
    [print(x) for x in video_list]
    
    i = video_list[0]
    #for i in video_list: # 機能してない
        # if i == "":
        #     continue

    print("[debug][FUNC][down_video][" + str(num) + "]:start " + title + "i:[" + str(i) + "]")
    opener = urllib.request.build_opener()
    # 请求头
    opener.addheaders = [
        # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
        ('Referer', start_url),  # 注意修改referer,必须要加的!
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),
    ]
    urllib.request.install_opener(opener)
    # 创建文件夹存放下载的视频
    if not os.path.exists(currentVideoPath):
        os.makedirs(currentVideoPath)
    # 开始下载

    vtitle = page_title + "_" + title
    #if len(video_list) > 1:
    #    filename = os.path.join(currentVideoPath, r'{}-{}.flv'.format(vtitle, num))
    ##else:
    #    filename = os.path.join(currentVideoPath, r'{}.flv'.format(vtitle))
    filename = os.path.join(currentVideoPath, r'{}-{}.flv'.format(vtitle, num))
    download_video(i, filename, num, title)


# 合并视频(20190802新版)
def combine_video(title_list, page_title):
    if LANG == "ja":
        msg_print("[FUNC][combine_video]:結合開始")
    elif LANG == "en":
        msg_print("[FUNC][combine_video]:start")
    elif LANG == "zh":
        msg_print("[FUNC][combine_video]:start")

    current_video_path = os.path.join(VIDEO_PATH, page_title)
    #for title in title_list:
    if len(os.listdir(current_video_path)) >= 2:
        # The video is larger than one segment before it needs to be merged
        print('[下载完成,正在合并视频...]:' + current_video_path)
        os.chdir(current_video_path)
        # Define an array
        L = []
        AU = []
        # Traverse all files
        for file in sorted(os.listdir(current_video_path), key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            # 如果后缀名为 .mp4/.flv
            if os.path.splitext(file)[1] == '.flv':
                # 拼接成完整路径
                filePath = os.path.join(current_video_path, file)
                # 载入视频
                video = VideoFileClip(filePath)
                #audioclip = AudioFileClip(filePath)
                print("[DEBUG][combine] filePath:" + filePath)
                # 添加到数组
                L.append(video)
               # AU.append(audioclip)
        try:
            # 拼接视频
            final_clip = concatenate_videoclips(L)
            #concatenate_audioclip(AU)
            # 生成目标视频文件
            print("[DEBUG][conbine]current_video_path:" + current_video_path)
            #print("[DEBUG][conbine]title             :" + title)
            #final_clip.to_videofile(os.path.join(current_video_path, r'{}.mp4'.format(title)), fps=24, remove_temp=False)
            #final_clip.to_videofile(os.path.join(current_video_path, r'{}.mp4'.format(current_video_path)), fps=24, remove_temp=False)
            #audio=os.path.join(current_video_path, r'{}.mp3'.format(page_title))
            filename = os.path.join(current_video_path, r'{}.mp4'.format(page_title))
            final_clip.write_videofile(
                filename, 
                fps=24, 
                remove_temp=False, 
                progress_bar=False, 
                codec='libx264', 
                audio_codec='libmp3lame'
            )

            # video_ = VideoFileClip(filename)
            # video_.write_videofile(
            #     os.path.join(current_video_path, r'{}.mp4'.format(page_title)), 
            #     fps=24,
            #     remove_temp=False, 
            #     progress_bar=False, 
            #     codec='libx264', 
            #     audio_codec='libmp3lame',
            #     audio=os.path.join(r'{}TEMP_MPY_wvf_snd.mp3'.format(page_title))
            # )


            if LANG == "ja":
                msg_print("[結合完了        ]:" + current_video_path)
            elif LANG == "en":
                msg_print("[combine finished]:" + current_video_path)
            elif LANG == "zh":
                # 视频只有一段则直接打印下载完成
                msg_print('[视频合并完成     ]:' + current_video_path)
        except Exception as e:
            print("[ERROR] fail to combine :{0}".format(e.args))
            msg_print("[ERROR] fail to combine")

    else:
        if LANG == "ja":
            msg_print("[結合完了        ]:" + current_video_path)
        elif LANG == "en":
            msg_print("[combine finished]:" + current_video_path)
        elif LANG == "zh":
            # 视频只有一段则直接打印下载完成
            msg_print('[视频合并完成     ]:' + current_video_path)

def replace_title(title):
    before_char = r'[\\/:*?"<>| ]+'
    after_char  = '_'
    return_str = re.sub(before_char, after_char, title)
    return return_str[:-14]


def do_prepare(inputStart,inputQuality, id):
    TYPE = id
    ID_TYPE = IDDict[TYPE]
    # 清空进度条
    download.coords(fill_line1,(0,0,0,23))
    pct.set('0.00%')
    root.update()
    # 清空文本栏
    msgbox.delete('1.0','end')
    start_time = time.time()
    # 用户输入av号或者视频链接地址
    print('*' * 30 + 'Video Download Assistant for Station B' + '*' * 30)
    # title取得
    try:
        PAGE_TITLE = replace_title(BeautifulSoup(requests.get(inputStart).text, "html.parser").title.string)
    except Exception as e:
        PAGE_TITLE = "no_title"
        msg_print("[ERROR]http error: title get Error")

    start = inputStart
    print("inputStart " + inputStart)

    if not(start.startswith("http")):  # 如果输入的是av号
        # Get the api of cid, just pass in aid
        start_url = 'https://api.bilibili.com/x/web-interface/view?' + ID_TYPE + '=' + start
        BASE_URL = start_url
    else:
        id = start.split('/')[4]
        id = id.split('?')[0]
        print("[ID]:" + id)
        # https://www.bilibili.com/video/av46958874/?spm_id_from=333.334.b_63686965665f7265636f6d6d656e64.16
        start_url = 'https://api.bilibili.com/x/web-interface/view?' + ID_TYPE + '=' + id
        BASE_URL = start_url

    # 视频质量
    # <accept_format><![CDATA[flv,flv720,flv480,flv360]]></accept_format>
    # <accept_description><![CDATA[高清 1080P,高清 720P,清晰 480P,流畅 360P]]></accept_description>
    # <accept_quality><![CDATA[80,64,32,16]]></accept_quality>
    quality = inputQuality
    # 获取视频的cid,title
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    print("[DEBUG]start_url :" + start_url)
    html = requests.get(start_url, headers=headers).json()
    print(html)
    data = html['data']
    if PAGE_TITLE == "no_title":
        PAGE_TITLE = data['title']

    cid_list = []
    if '?p=' in start:
        # 单独下载分P视频中的一集
        p = re.search(r'\?p=(\d+)',start).group(1)
        cid_list.append(data['pages'][int(p) - 1])
    else:
        # 如果p不存在就是全集下载
        cid_list = data['pages']
    # print(cid_list)
    # 创建线程池
    threadpool = []
    title_list = []
    print("[debug]cid_list",end=" :")
    [print(x) for x in cid_list]
    num = 1
    for item in cid_list:
        if item == "":
            continue

        cid = str(item['cid'])
        title = item['part']
        title = re.sub(r'[\/\\:*?"<>|]', '', title)  # Replacement empty
        print('[debug][Download video cid  ]\t:' + cid)
        print('[debug][Download video theme]\t:' + title)
        title_list.append(title)
        page = str(item['page'])
        start_url = start_url + "/?p=" + page
        video_list = get_play_list(start_url, cid, quality)
        start_time = time.time()
        # down_video(video_list, title, start_url, page)
        # Fixed line
        th = threading.Thread(target=down_video, args=(video_list, PAGE_TITLE, title, start_url, page, num))
        # General line subscription line thread pond
        threadpool.append(th)
        num += 1

    # 开始线程
    for th in threadpool:
        th.start()
    #    th.join()
    
    #thread_list = threading.enumerate()
    #thread_list.remove(threading.main_thread())

    # 等待所有线程运行完毕
    #for th in thread_list:
    for th in threadpool:
        th.join()
    
    # 最后合并视频
    if IS_COMBINE:
        combine_video(title_list, PAGE_TITLE)

    end_time = time.time()  # 结束时间
    msg_print('At the time of download wear%.2f秒,约%.2f分钟' % (end_time - start_time, int(end_time - start_time) / 60))

    desc_to_text(BASE_URL, PAGE_TITLE)

    msg_print("[downloaded]")
    # 如果是windows系统，下载完成后打开下载目录
    currentVideoPath = VIDEO_PATH # 当前目录作为下载目录
    if (sys.platform.startswith('win')):
        os.startfile(currentVideoPath)

def thread_it(func, *args):
    '''将函数打包进线程'''
    # 创建
    t = threading.Thread(target=func, args=args) 
    # 守护 !!!
    t.setDaemon(True) 
    # 启动
    t.start()

def desc_to_text(start_url, file_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    html = requests.get(start_url, headers=headers).json()
    print("[DEBUG]html data:", str(html))
    data = html['data']
    text = data['desc']
    currentVideoPath = os.path.join(VIDEO_PATH, file_name, file_name)
    f = open(currentVideoPath + '.txt', 'a', encoding='UTF-8')
    f.write(text)
    f.close()

def open_site():
    webbrowser.open("https://www.bilibili.com/")

def open_dir_local():
    path = r"C:\Program Files Made BySelf\Bilibili_video_download\bilibili_video"
    #subprocess.Popen(['explorer', path.encode("cp932").replace("/", "\\")])
    os.startfile(path)

def open_dir_server():
    path = r"Z:\30_movie\04_テレビ番組\05.bilibili"
    os.startfile(path)

def move_movie():
    thread1 = threading.Thread(target=move)
    thread1.start()

def move():
    path_before = r'C:\Program Files Made BySelf\Bilibili_video_download\bilibili_video'
    for item in os.listdir(path_before):
        item_path = os.path.join(path_before,item)
        shutil.move(item_path, r'Z:\30_movie\04_テレビ番組\05.bilibili')

if __name__ == "__main__":
    # 设置标题
    root.title('Video Download Assistant for Station B-GUI')

    # create menu bar
    menu = Menu(root)

    menu1 = Menu(root) 
    menu.add_cascade(label='Setting(S)', menu=menu1) 
    menu1.add_command(label='open dir local', command=open_dir_local) 
    menu1.add_command(label='open dir server', command=open_dir_server)
    menu1.add_command(label='move movie', command=move_movie)

    menu2 = Menu(root)
    menu.add_cascade(label='Site(S)', menu=menu2)
    menu2.add_command(label='open bili', command=open_site) 

    menu3 = Menu(root)
    menu.add_cascade(label='Help(H)', menu=menu3)

    # menu を画面に設定
    root.config(menu=menu)

    # 设置ico
    root.iconbitmap('./Pic/favicon.ico')

    # 设置Logo
    photo = PhotoImage(file='./Pic/logo.png')
    logo = Label(root,image=photo)
    logo.pack()

    # 各项输入栏和选择框
    inputStart = Entry(root,bd=4,width=600)
    labelStart=Label(root,text="enter the B station " + TYPE + " number or video link address you want to download:") # 地址输入
    labelStart.pack(anchor="w")
    inputStart.pack()

    labelQual = Label(root,text="select the quality of the video you want to download") # 清晰度选择
    labelQual.pack(anchor="w")
    inputQual = ttk.Combobox(root,state="readonly")

    # 可供选择的表
    inputQual['value']=('1080P','720p','480p','360p')
    # 对应的转换字典
    keyTrans=dict()
    keyTrans['1080P']='80'
    keyTrans['720p']='64'
    keyTrans['480p']='32'
    keyTrans['360p']='16'
    # 初始值为720p
    inputQual.current(1)
    inputQual.pack(anchor="w")

    labelId = Label(root,text="select id (BV[new]/av[old])")
    labelId.pack(anchor="w")
    inputId = ttk.Combobox(root,state="readonly")
    inputId['value']=('BV','av')
    inputId.current(0)
    inputId.pack(anchor="w")

    confirm = Button(root,text="download",command=lambda:thread_it(do_prepare,inputStart.get(), keyTrans[inputQual.get()], inputId.get()))
    msgbox = Text(root)
    msgbox.insert(
        '1.0',
        "For single P video: directly pass in the av number of station B or the video link address\n \
            (eg: 49842011 or https://www.bilibili.com/video/" + TYPE + "49842011)\n \
        For multi-P video:\n \
            1.Download the complete works: directly pass in the B station av number or video link address\n \
                (eg: 49842011或者https://www.bilibili.com/video/" + TYPE + "49842011)\n \
            2.Download one of the episodes: pass in the video link address of that episode\n \
                (eg: https://www.bilibili.com/video/" + TYPE + "19516333/?p=2)")
    msgbox.pack()
    download=Canvas(root,width=465,height=23,bg="white")
    # 进度条的设置
    labelDownload=Label(root,text="Download progress")
    labelDownload.pack(anchor="w")
    download.pack()

    fill_line1 = download.create_rectangle(0, 0, 0, 23, width=0, fill="green")
    pct=StringVar()
    pct.set('0.0%')
    pctLabel = Label(root,textvariable=pct)
    pctLabel.pack()
    root.geometry("600x800")
    confirm.pack()
    # GUI主循环
    root.mainloop()
    
