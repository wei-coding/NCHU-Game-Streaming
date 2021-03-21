# game_streaming(區網內的遊戲串流)

## 進度一覽表

### 2020

### 十月

### 十一月

+ meeting 過後，和助教決定在區網內實作就好
+ 助教提議可以擷取顯卡的快取做加速，即在尚未顯示前就將影像傳出（較為困難）
+ Client GUI 開始製作
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
* 目前測試自製UDP比較快(延遲小)，web比較穩(不會掉包)
* 直接上libjpeg-turbo並配合UDP速度上十分不錯
* 無線網路環境下效果不好，有很高的機率掉封包甚至出現Dup-ACK的狀況
* 使用pyqt5建立GUI
* 已經實作三向交握
* decode出現JPEG corrupt的狀況還待解決，會造成畫面閃爍
* 三向交握封包應該要用protocol實作
* 看要不要直接用structure來傳
* 目前發現UDP傳輸封包在全螢幕時非常不穩定，考慮改走TCP

## 安裝說明

* 見requirements.txt
* 外部安裝
  * [libjpeg-turbo](https://sourceforge.net/projects/libjpeg-turbo/files/2.0.90%20%282.1%20beta1%29/)



## 參考資料

[Speed-Up JPEG Encode/Decode Processing for OpenCV using libjpeg-turbo – Summary?Blog (unanancyowen.com)](http://unanancyowen.com/en/opencv-with-libjpeg-turbo/)