# 预载了 求生之路2 本体及DLC sound中所有wav音频信息的的第三方批量音频转换工具
## 安装与使用
请在Release中下载最新版本的exe

[视频使用演示](https://www.bilibili.com/video/BV1zLqQY5EBr/?share_source=copy_web&vd_source=d9788e6dc1a6f65d8c8ce24376e3fe35)

**注意：**
为减少搜索卡顿，搜索音频时在完成输入后需要按下回车键进行搜索

如果输入音频时长小于目标音频的时长，输出的音频尾部将会被填充空音频以达到目标时长

ps：填充不影响淡入淡出设置

**如果遇到问题，请提交issue**

## 注意事项
启动时需要读取预记录的音频数据生成选项，根据硬盘速度波动，读取7100MB/s的固态硬盘需要20s左右

## 待办
0.完善源码注释

1.美化界面

2.添加手动指定输出路径

3.添加自动vpk打包

4.去除ffprobe依赖

5.简化数据库，删除不必要数据

### 附言
第一次尝试，最初的想法是给出手动分类过的常用音频，但工作量超出预计，也更局限


使用了[ffmpeg-python](https://github.com/kkroening/ffmpeg-python.git)处理音频

使用了[Pyside6](https://doc.qt.io/qtforpython-6/index.html)开发GUI
