# game_streaming(區網內的遊戲串流)

## 進度一覽表

### 2020

### 十月

### 十一月

+ meeting 過後，助教決定在區網內實作就好
+ 助教提議可以擷取顯卡的快取做加速，即在尚未顯示前就將影像傳出（較為困難）
+ GUI 開始製作
+ 測試純UDP的傳輸，配合mss

### 十二月

+ 發現mss的截圖速度不夠(約15fps)，且UDP會有server overwhelm client的問題
    + 解法：用buffer，比較不容易出現此問題
    + 之後要寫RTP或自創協定

### 2021

#### 一月

+ 測試win32gui的截圖速度，大約25fps上下

#### 二月

+ 2/22 找到最高效的截圖方法(d3dshot)
+ 2/23 截圖成功，fps達近60，準備進入協定部分

#### 三月

* 建置opencv libjpeg-turbo環境，速度上很快了
* 但可以繼續嘗試直接接上TurboJPEG，速度會更快
* 接下來目標看要用RTP、web版還是UDP自作協定版本





## 參考資料

[Video I/O Part 2: Fast JPEG Decoding – loopbio blog](http://blog.loopbio.com/video-io-2-jpeg-decoding.html)

[Speed-Up JPEG Encode/Decode Processing for OpenCV using libjpeg-turbo – Summary?Blog (unanancyowen.com)](http://unanancyowen.com/en/opencv-with-libjpeg-turbo/)

[OpenCV: Install OpenCV-Python in Windows](https://docs.opencv.org/master/d5/de5/tutorial_py_setup_in_windows.html)