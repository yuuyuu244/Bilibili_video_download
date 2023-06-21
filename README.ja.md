 ![enter image description here](Pic/logo.png)Bilibili Movie Download
===========================
![](https://img.shields.io/badge/Python-3.6.3-green.svg) ![](https://img.shields.io/badge/requests-2.18.4-green.svg) ![](https://img.shields.io/badge/moviepy-0.2.3.2-green.svg)

### Bilibili Official - https://www.bilibili.com/

|Author|:sunglasses:Henryhaohao:sunglasses:|
|---|---
|Email|:hearts:1073064953@qq.com:hearts:


****
## :dolphin:Disclaimer

### All software is for learning and communication only, please do not use it for any commercial purpose! Thank you all!

## :dolphin:Introduction

### The project for Bilibili (b station) video download (support sub-P multi-segment video download!)

- **For single P videos: directly pass in the B site av number or video link address (eg: 49842011 or https://www.bilibili.com/video/av49842011)**
- For multi-P video.
  > 1. Download the whole set: directly pass in the B site av number or video link address (eg: 49842011 or https://www.bilibili.com/video/av49842011)
  > 2. Download one of the episodes: pass in the video link address of that episode (eg: https://www.bilibili.com/video/av19516333/?p=2)

## :dolphin:versions

- **Version 1: bilibili_video_download_v1.py**
  
  > Encrypted API version, no need to add cookies, you can download 1080p videos directly
- **Version 2: bilibili_video_download_v2.py**
  
  > 1. No encryption API version, but you need to add the SESSDATA field in the cookie after login to download 720p and above videos
  > 2. If you want to download 1080p+ videos, you need to bring in the SESSDATA in the cookie of the big member of B site to do so. To replace the SESSDATA value in the cookie, please change it regularly.
- **Version 3: bilibili_video_download_v3.py**
  
  > That is, the upgrade version of version 2, for Threading multi-threaded download version, download speed greatly improved! 
  
- **Version 4: GUI版本 - bilibili_video_download-GUI.py**
  
  > In version three based on the addition of graphical interface, more user-friendly operation
  
- **Version 5: bilibili_video_download_bangumi.py**
  
  > In version one and three, add the download video of B station (eg: https://www.bilibili.com/bangumi/play/ep269835)

## :dolphin:Operating Environment

Version: Python3

## :dolphin:Installing Dependency Libraries

```
pip3 install -r requirements.txt
```
## :dolphin:Screenshot

> - **Run Download**<br><br>
![enter image description here](Pic/run.png)
> - graphical interface<br>  
![](Pic/GUI-run.png)
> - Download completed<br>
![enter image description here](Pic/video.png)
## :dolphin:**Conclusion**

> **Finally, if you think this project is good or helpful to you, give a Star, it is also a kind of encouragement to my learning path!
Hahaha, thanks everyone! Thank you!**:cupid::cupid:
