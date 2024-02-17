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


* build:

```Shell
cd win32
./win32-build.bat
```


* Dev steps:

1. copy images which need be reacted to folder "img-route"

2. run "pic2py.py" make static images file into python object

3. add load data from "string_pc.py"
```Python
map_images = [
    ....
]
```

* Run test
```Shell
cd win32
python main.py -a [帳號] -p [密碼] -t [等待時間] -c [壓縮碼]
```
or
```Shell
cd win32
./win32-dev.bat
```

---

## 3. Folder Construct

- asar.app **(解譯的 skype desktop 業務邏輯)**
- img-route **(存放判斷過程需要的圖片 )**
- win32 **(主程序目錄)**
  | - `main.py` **(主程序python)**
  | - `string_pic.py` **(通過pic2py.py產生的圖像base64)**
  | - `test_decrypt.py` **(驗證加解密方式)(測試用)**
  | - `win32-build.bat` **(封裝`main.py` 成 正式exe檔)**
  | - `win32-dev.bat` **(封裝`main.py` 成 debug用exe檔, 會有log產生)**
- `image.ipynb` **(測試圖像模糊化Jupyter note)**
- `MS.txt` **(Microsoft Windows 的視窗訊號對應文件)** 
- `pic2py.py` **(用以將 `img-route` 內的圖片壓成 base64 string )**
- `requirements.txt` **(pip必要的library)**