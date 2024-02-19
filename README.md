# RV Skype Auto Login Kit
---
a tool for login skype desktop on windows with encrypted key

## 1. Requirement:

* Python 3.7.16


---

## 2. Install and Runing:

* install by pip
```shell
pip install -r requirements.txt
```


* Build prod:

```Shell
cd win32
./win32-build.bat
```
執行完後會在目錄 win32/dist/ 內產生檔案 `main.exe` 則是正式的程序

* Build dev:
```Shell
cd win32
.\win32-dev.bat
```
執行完後會在目錄 win32/dist/ 內產生檔案 `dev.exe` 此為debug版本會在運作時產生logging

---

* Dev steps:

1. 將需要的圖片copy至 "img-route" 目錄

2. 執行 `pic2py.py` 讓靜態圖片轉換成base64的python string

3. 將產生的 `string_pc.py` 檔案移至 win32 目錄底下覆蓋

4. 修改 `main.py` 內 map_images 的陣列, 增加自己有新增的對應圖片名稱
```Python
map_images = [
    ....
    {'name': '[圖片檔名]', 'img': Image.open(BytesIO(base64.b64decode([img+圖片檔名])))},
]
```


* Run test
 -- -a 與 -p 必須同時給予, 亦或者給 -c，否則報錯
 -- -c (可選) 如果有給就忽略 -a與-p
 -- -t (可選) 預設為2秒
```Shell
cd win32
python main.py -a [帳號] -p [密碼] -t [每次指令等待時間] -c [壓縮碼]
```


---

## 3. Folder Construct

- asar.app **(解譯的 skype desktop 業務邏輯)**
- img-route **(存放判斷過程需要的圖片 )**
- win32 **(主程序目錄)**
  - | - `main.py` **(主程序python)**
  - | - `string_pic.py` **(通過pic2py.py產生的圖像base64)**
  - | - `test_decrypt.py` **(驗證加解密方式)(測試用)**
  - | - `win32-build.bat` **(封裝`main.py` 成 正式exe檔)**
  - | - `win32-dev.bat` **(封裝`main.py` 成 debug用exe檔, 會有log產生)**
- `image.ipynb` **(測試圖像模糊化Jupyter note)**
- `MS.txt` **(Microsoft Windows 的視窗訊號對應文件)** 
- `pic2py.py` **(用以將 `img-route` 內的圖片壓成 base64 string )**
- `requirements.txt` **(pip必要的library)**