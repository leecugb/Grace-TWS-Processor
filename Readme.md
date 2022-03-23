# 长周期序列Grace TWS水文数据产品变化分析及其可视化

地球重力观测卫星Grace和Grace-FO的不同级别数据产品被科学家和其他兴趣用户广泛应用于研究地球系统的质量迁移。然而，将Grace/Grace-FO数据（Level-0级原始数据或Level-1/2低级地球引力场数据产品）处理成不同领域用户喜闻乐见的产品却不是一件容易的事情。为了扩大Grace/Grace-FO数据的应用群体，多家科研机构推出了Level-3级数据产品。

在这些Level-3级数据产品中，比较有影响力的是德国地学研究中心（German Research Centre for Geosciences， GFZ）的陆地水储量（terrestrial water storage over non-glaciated regions）数据产品。本文将介绍该水文数据产品的长周期变化分析和可视化方法。

## 数据格式
德国地学中心（GFZ）的Level-3级重力卫星水文数据产品存储为NetCDF（network Common Data Form）格式，每个文件包含``time``, ``lon``, ``lat``, ``tws``, ``std_tws``, ``leakage``, ``model_atmosphere``等7个数据子集。``tws``包含了一个``n x 180 x 360``的数组，代表了``n``个月度的水储量变化数据；``time``包含了``n``个月度的时间信息（相对于格林威治时间2002-4-18 00：00：00的天数时间差）；``lon``存储了一个``1 x 360``的数组，记录``tws``中数据的经度信息；``lat``存储了一个``1 x 180``的数组，记录了``tws``中数据的纬度信息。

## 数据处理
为了方便地处理德国地学中心的一百多个Level-3级重力卫星水文数据NetCDF文件，我们写了个简易且实用的脚本程序，使用方法如下：

### 应用示例
首先，导入该python包
```
>>> import GFZ_TWS
``` 
#### 下载数据
可以选择从http://gravis.gfz-potsdam.de/home手动下载，将下载好的数据文件集中放在某一路径下，设为rootDir。然后用rootDir初始化Reader对象。

```
>>> tws=GFZ_TWS.Reader(r'./tws/')
```
也可以选择使用工具包中Reader类的自动下载函数完成数据下载。
```
>>> tws.update()
```


#### 绘制区域陆地水储量变化折线图
通过调用tws.plot(vector)函数即可绘制区域陆地水储量变化折线图，vector为兴趣区矢量文件。
```
>>> data=tws.plot('./tws/mask.shp')

```
![grace_plot.png](https://upload-images.jianshu.io/upload_images/24572219-aaff111ebbfe9d54.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)




data变量存储了折线数据。

#### 可视化全球变化趋势
```
plt.imshow(tws.gradient)

``` 
![gradient.png](https://upload-images.jianshu.io/upload_images/24572219-0c6205dfc927e3a4.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
