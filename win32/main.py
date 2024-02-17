import sys, os, re, time, getopt, base64
import win32gui
import win32ui
import win32api
import win32con
import win32event
# import win32process
# import win32com.client
from sys import exit
from ctypes import windll
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename
from Crypto.Cipher import AES
from binascii import hexlify, unhexlify
import hashlib
import math
import numpy as np
import cv2
# import win32clipboard as clipboard
from PIL import Image, ImageGrab, ImageFilter
# import skimage.metrics as sm
from string_pic import *
from io import BytesIO


SKYPE_REG = re.compile('^Skype*')
SKYPE_CLASS_REG = re.compile('^Chrome_WidgetWin_1*')
SKYPE_CLASS_RENDER_REG = re.compile('Chrome_RenderWidgetHostHWND')
SKYPE_CLASS_INTERMEDIATE_REG = re.compile('Intermediate D3D Window')
SKYPE_FOR_DESKTOP_CLASS_REG = re.compile('^CabinetWClass*')

BS = AES.block_size

debug_mode = False

def padding_pkcs5(value):
    return str.encode(value + (BS - len(value) % BS) * chr(BS - len(value) % BS))

def aes_ecb_encrypt(key, value):
    # cryptor = AES.new(bytes.fromhex(key), AES.MODE_ECB)
    cryptor = AES.new(key, AES.MODE_ECB)
    padding_value = padding_pkcs5(value)    # padding content with pkcs5
    ciphertext = cryptor.encrypt(padding_value)
    return ''.join(['%02x' % i for i in ciphertext])

def aes_ecb_decrypt(key, value):
    # key = bytes.fromhex(key)
    cryptor = AES.new(key, AES.MODE_ECB)
    ciphertext = cryptor.decrypt(bytes.fromhex(value))
    return ciphertext.decode('utf-8')

def loadImageToBlurArray(img):
    _img = convert_stylish_image(img)
    _ary = np.array(_img)

    return _ary

def calculate_similarity(ary1, ary2):
    sub_ary1 = ary1[20:520, 20:420]
    sub_ary2 = ary2[20:520, 20:420]

    bounding_boxes = get_bounding_boxes(sub_ary1, 4)
    bounding_boxes_2 = get_bounding_boxes(sub_ary2, 4)

    similarity = 0
    _i = len(bounding_boxes)
    is_same_contours = _i == len(bounding_boxes_2)
    if is_same_contours and _i > 1:
        similarity = 1
        while (_i > 0):
            _i -= 1
            _imageary = get_image_by_rect(ary1, bounding_boxes[_i])
            _imageary_2 = get_image_by_rect(ary2, bounding_boxes_2[_i])
            similarity -= int((np.mean(_imageary) - np.mean(_imageary_2)) ** 2) / 16
    else:
        con_1 = sub_ary1 < 4
        con_2 = sub_ary2 < 4
        combined_con = np.logical_not(con_1, con_2)
        # print(combined_con, combined_con.shape)
        left_ary_1 = sub_ary1[combined_con]
        left_ary_2 = sub_ary2[combined_con]

        mse = np.mean((left_ary_1 - left_ary_2) ** 2)
        similarity = 1 - (mse / 255)
    
    return similarity


def convert_stylish_image(img):
    _img = img.filter(ImageFilter.FIND_EDGES)
    _img = _img.convert("L")
    _img = _img.filter(ImageFilter.GaussianBlur(8))
    return _img


def get_bounding_boxes(imgarray, basic_color=4):
    _, thresholded = cv2.threshold(imgarray, basic_color, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_boxes.append((x, y, w, h))
        # IPython.display.display(Image.fromarray(imgarray[y:y+h, x:x+w]))

    return bounding_boxes

def get_image_by_rect(img, rect):
    x,y,w,h = rect
    return img[y:y+h, x:x+w]


hexstr_content = '62ea45d3499cf41e424373b145ce44dc0033609d0e989338807656ef6abcc96f'
aes_key = b't1tSr6B1RGHvujeW'
split_character = ' | '

# expect_result = 'c1ee1f3f2d74e02706be9af78aa79ba4'.upper()
# aes128string = aes_ecb_encrypt(aes_key, 'ABcdefGHIJ123456789KlmnopQ')
# decrypted = aes_ecb_decrypt(aes_key, '62ea45d3499cf41e424373b145ce44dc0033609d0e989338807656ef6abcc96f')

map_images = [
    {'name': '0png', 'img': Image.open(BytesIO(base64.b64decode(img0png)))},
    {'name': '1_1png', 'img': Image.open(BytesIO(base64.b64decode(img1_1png)))},
    {'name': '1_2png', 'img': Image.open(BytesIO(base64.b64decode(img1_2png)))},
    {'name': '1_3png', 'img': Image.open(BytesIO(base64.b64decode(img1_3png)))},
    {'name': '1_4png', 'img': Image.open(BytesIO(base64.b64decode(img1_4png)))},
    {'name': '2_1png', 'img': Image.open(BytesIO(base64.b64decode(img2_1png)))},
    {'name': '2_2png', 'img': Image.open(BytesIO(base64.b64decode(img2_2png)))},
    {'name': 'font2_2png', 'img': Image.open(BytesIO(base64.b64decode(imgfont2_2png)))},
    {'name': '3_1png', 'img': Image.open(BytesIO(base64.b64decode(img3_1png)))},
    # {'name': '3_2png', 'img': Image.open(BytesIO(base64.b64decode(img3_2png)))},
    {'name': '3_3png', 'img': Image.open(BytesIO(base64.b64decode(img3_3png)))},
    {'name': 'font3_3png', 'img': Image.open(BytesIO(base64.b64decode(imgfont3_3png)))},
    {'name': '4_1png', 'img': Image.open(BytesIO(base64.b64decode(img4_1png)))},
    # {'name': 'loadingpng', 'img': Image.open(BytesIO(base64.b64decode(imgloadingpng)))},
]

for idx, obimg in enumerate(map_images):
    map_images[idx]['ary'] = loadImageToBlurArray(obimg['img'])


def handle_skype(handle_id, acc='', pwd='', waiting_second = 2):

    waiting_gap = math.floor((waiting_second-1) / 2)

    windll.user32.SetForegroundWindow(handle_id)
    clsname = win32gui.GetClassName(handle_id)
    print('Start Handle Skype Login [HWND: {} , Class Name: {}]'.format(handle_id, clsname))

    inner_widget_id = get_inner_skype_widget(handle_id)
    inner_widget_class_name = win32gui.GetClassName(inner_widget_id)
    print('Chrome Widget Class Name: ', inner_widget_class_name)
    print('Waiting Second: ', waiting_second)
    time.sleep(waiting_second)

    _pos_start_btn = (227, 500)
    _pos_start_or_build_btn = (226, 375)
    _pos_middle_btn = (250, 460)
    _pos_other_account_btn = (224, 402)
    _pos_login_account_input = (80, 210)
    _pos_skypelogo_bottom = (215, 120)
    _pos_cancel_forget_pwd = (254, 346)
    _pos_add_other_account_v3 = (112, 366)
    _pos_login_or_create_account_v3 = (232, 294)
    _pos_upperright_password_before = (322, 42)



    def is_login_screen(hwnd):
        _login_size = (454, 631)
        _min_size = (344, 621)

        windll.user32.SetForegroundWindow(hwnd)
        win32gui.MoveWindow(hwnd, 0, 0, _min_size[0], _min_size[1], 1)
        time.sleep(1+waiting_gap)
        windll.user32.SetForegroundWindow(hwnd)
        _rect = win32gui.GetClientRect(hwnd)
        
        # print('Check Login Screen Rect: ', _rect)

        _login_width = _login_size[0]
        _width = _rect[2]
        if _login_width - _width > 60:
            win32gui.MoveWindow(hwnd, 8, 8, 960, 650, 1)
            return False
        else:
            return True


    def enter_str(hwnd, _str, delete=0):
        windll.user32.SetForegroundWindow(hwnd)
        print('Start Writing [{}....]'.format(_str[:2]))

        for _ in _str:
            win32api.PostMessage(hwnd, win32con.WM_CHAR, ord(_), 0)

        print('[Enter Str] Length: ', len(_str))
        
        if len(_str) > 0:
            win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, toKeyCode('enter'), 0)

        if delete:
            time.sleep(0.2)
            for _ in range(delete):
                win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, toKeyCode('back'), 0)
            
        time.sleep(0.2)
        print('End Writing.')


    def click(hwmd, x,y):
        iparam = x + (y * 0x10000)
        windll.user32.SetForegroundWindow(hwmd)
        # save_image_by_handle(hwmd, iparam)
        win32api.PostMessage(hwmd, win32con.WM_MOUSEMOVE, 1, iparam)
        time.sleep(0.2)
        win32api.PostMessage(hwmd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, iparam)
        time.sleep(0.2)
        win32api.PostMessage(hwmd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, iparam)
        time.sleep(0.3)
        
    
    
    def switchActionByImage(img, widget_id):
        BASE_SIMILAR = 0.742
        GOOD_SIMILAR = 0.995
        _matched = 0
        _array = loadImageToBlurArray(img)
        _tmp_high_rate = 0
        _tmp_hr_name = ''
        _high = {
            'rate': 0,
            'name': '',
            'idx': 0,
        }
        # print("switchActionByImage imgarray shape: ", _array.shape)
        if _array.shape[0] != map_images[0]['ary'].shape[0]:
            return True

        for _obj in map_images:
            _aryimg = _obj['ary']
            _rate = calculate_similarity(_array, _aryimg)
            # print('_rate: ', _rate)
            if _rate > _high['rate']:
                _high['idx'] = _matched
                _high['name'] = _obj['name']
                _high['rate'] = _rate
            if _rate > GOOD_SIMILAR:
                break

            _matched += 1
        
        _is_matched = _high['rate'] > BASE_SIMILAR
        if _is_matched:
            _img_name = _high['name']
            print('matched image name: ', _img_name)
            if _img_name == '0png':
                click(widget_id, _pos_start_btn[0], _pos_start_btn[1])
                # click(widget_id, _pos_middle_btn[0], _pos_middle_btn[1])
                # click(_pos_login_account_input[0], _pos_login_account_input[1])
            
            elif _img_name == '1_1png' or _img_name == '1_2png':
                # print('Find Inputs.')
                click(widget_id, _pos_other_account_btn[0], _pos_other_account_btn[1])
                click(widget_id, _pos_start_or_build_btn[0], _pos_start_or_build_btn[1])
            elif _img_name == '1_3png':
                click(widget_id, _pos_add_other_account_v3[0], _pos_add_other_account_v3[1])
            elif _img_name == '1_4png':
                click(widget_id, _pos_login_or_create_account_v3[0], _pos_login_or_create_account_v3[1])
            elif _img_name == '2_1png' or _img_name == '2_2png' or _img_name == 'font2_2png':
                print('Enter Account.')
                click(widget_id, _pos_skypelogo_bottom[0], _pos_skypelogo_bottom[1])
                win32api.PostMessage(widget_id, win32con.WM_KEYDOWN, toKeyCode('tab'), 0)
                time.sleep(0.5)
                enter_str(widget_id, acc)
                time.sleep(1)
            elif _img_name == '3_1png' or _img_name == '3_3png' or _img_name == 'font3_3png':
                # or _img_name == '3_2png'
                print('Enter Password.')
                # click(widget_id, _pos_upperright_password_before[0], _pos_upperright_password_before[1])
                # win32api.PostMessage(widget_id, win32con.WM_KEYDOWN, toKeyCode('tab'), 0)
                # time.sleep(0.5)
                enter_str(widget_id, pwd, delete=len(acc) + len(pwd))
            elif _img_name == '4_1png':
                click(widget_id, _pos_cancel_forget_pwd[0], _pos_cancel_forget_pwd[1])
            
            
        else:
            print('not matched. best rate: ', _high['rate'], ' best image: ', _high['name'])
        
        return _is_matched

    
    
    _i = 0
    _max = 25
    _process = 0
    
    time.sleep(1+waiting_gap)

    while True:

        if _i > _max or _process > 8:
            # messagebox.showerror('Timeout of try screen actions.')
            # sys.exit(2)
            break

        # is_test_screen(inner_widget_id)

        if is_login_screen(handle_id):
            
            bbox = win32gui.GetWindowRect(inner_widget_id)
            screenshot = ImageGrab.grab(bbox)
            if switchActionByImage(screenshot, inner_widget_id):
                _process += 0 if debug_mode else 1
            elif debug_mode:
                screenshot.save('./window_screenshot_{}.png'.format(_i))
            time.sleep(1+waiting_gap)
            _i += 1
        else:
            
            break
        
    return True



def get_all_exsit_skypes(is_debug=False):
    result_list = []
    def _cb(handle_id, arg):
        _title = win32gui.GetWindowText(handle_id)
        if SKYPE_REG.match(_title):
            _clsname = win32gui.GetClassName(handle_id)
            
            if SKYPE_CLASS_REG.match(_clsname):
                result_list.append(handle_id)
            
            if is_debug:
                print('Getting EnumWindows Matched Skype :: TITLE = {} ,  CLASS = {} , HWND_ID = {}'.format(_title, _clsname, handle_id))
    
    win32gui.EnumWindows(_cb, None)
    if is_debug:
        print('===================================================')
    return result_list

def get_new_skype_id(old_ids):
    now_ids = get_all_exsit_skypes(True)
    new_id = None
    if len(now_ids) == len(old_ids) +1:
        for _ in now_ids:
            if _ not in old_ids:
                new_id = _
                break
    
    return new_id

def get_inner_skype_widget(skype_id):
    _max = 30
    _i = 0
    while True:
        time.sleep(1)
        if _i > _max:
            raise Exception('Time out of get inner skype widget.')
        _foreground = win32gui.GetForegroundWindow()
        # print('_foreground id: ', _foreground)
        # print('_foreground classname: ',win32gui.GetClassName(_foreground))
        # print('_foreground title: ',win32gui.GetWindowText(_foreground))
        if _foreground == skype_id:
            inner_id = win32gui.FindWindowEx(_foreground, 0, None, None)
            print('FindWindowEx inner_id: ', inner_id)
            time.sleep(1)
            return inner_id
        else:
            windll.user32.SetForegroundWindow(skype_id)
        
        _i += 1

    return None







def loop_handle_fn(Skype_exe):
    _exsit_skype_ids = get_all_exsit_skypes()
    if len(_exsit_skype_ids) == 0:
        # no skype opened
        # program = Skype_exe
        program = Skype_exe + " --secondary"
    else:
        # have skype launched
        program = Skype_exe + " --secondary"
    
    print("Skype Program: {}".format(program))

    _exec = win32api.WinExec(program)
    acc = ''
    pwd = ''
    waiting_second = 2

    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:p:c:t:", [])
        for o, a in opts:
            if o in ("-a", "--acc"):
                acc = a
            elif o in ("-p", "--pwd"):
                pwd = a
            elif o in ("-c", '--code'):
                _code = a
                _ap = aes_ecb_decrypt(aes_key, _code)
                _ap_list = _ap.split(split_character, 1)
                if len(_ap_list) == 2:
                    print(_ap)
                    acc = _ap_list[0]
                    pwd = _ap_list[1]
                else:
                    messagebox.showerror('Error', "code format is wrong.")
                    raise Exception("Wrong of Split Account and Password")
            elif o in ("-t", "--time"):
                waiting_second += int(a)
        
        acc = acc.strip()
        pwd = pwd.strip()
        
    except getopt.GetoptError as err:
        print(err)
        messagebox.showerror('Error', err)
        sys.exit(2)

    if not (acc and pwd):
        messagebox.showerror('Error', 'Account or Password not given.')
        sys.exit(2)
    
    _i = 0
    _max = 30
    print('Login with account length: {}, pwd length: {}'.format(len(acc), len(pwd)))
    print('Start Getting Skype HWND ID..')

    while True:
        time.sleep(1)
        print('Getting... [{}]'.format(_i+1))
        new_skype_id = get_new_skype_id(_exsit_skype_ids)
        if new_skype_id:
            print('Finded HWND ID: ', new_skype_id)
            time.sleep(4)
            if handle_skype(new_skype_id, acc, pwd, waiting_second):
                break
        else:
            if _i >= _max:
                raise Exception('Time Out of getting skype hwnd id.')
        _i += 1
    
    return True


def toKeyCode(c):
    keyCodeMap = {
        '0'       : 0x30,
        '1'       : 0x31,
        '2'       : 0x32,
        '3'       : 0x33,
        '4'       : 0x34,
        '5'       : 0x35,
        '6'       : 0x36,
        '7'       : 0x37,
        '8'       : 0x38,
        '9'       : 0x39,
        '+'       : win32con.VK_ADD,
        '-'       : win32con.VK_SUBTRACT,
        '*'       : win32con.VK_MULTIPLY,
        '/'       : win32con.VK_DIVIDE,
        '|'       : win32con.VK_SEPARATOR,
        '.'       : win32con.VK_DECIMAL,
        'del'     : win32con.VK_DELETE,
        'delete'  : win32con.VK_DELETE,
        'back'    : win32con.VK_BACK,
        'help'    : win32con.VK_HELP,
        'home'    : win32con.VK_HOME,
        'left'    : win32con.VK_LEFT,
        'right'   : win32con.VK_RIGHT,
        'down'    : win32con.VK_DOWN,
        'up'      : win32con.VK_UP,
        'tab'     : win32con.VK_TAB,
        ' '       : win32con.VK_SPACE,
        'enter'   : win32con.VK_RETURN,
    }

    if c.isalpha():
        c = c.lower()
        if len(c) == 1:
            keyCode = ord(c) - (0x60 - 0x40)
            return keyCode
        
    if c in keyCodeMap:
        keyCode = keyCodeMap[c]
    else:
        keyCode = 0
    
    return keyCode



def getBufferContent(hwnd):
    buf_size = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    # print('buf_size: ', buf_size)
    buf = win32gui.PyMakeBuffer(buf_size)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, buf)
    # print('_buf_str: ', str(buf))
    address, length = win32gui.PyGetBufferAddressAndLen(buf)
    text = win32gui.PyGetString(address, length)
    buf.release()
    return text



if __name__ == '__main__':
        
    try:

        print('Start Skype Auto Login.')
        Tk().withdraw()
        initialdir = r'C:\Program Files (x86)\Microsoft\Skype for Desktop'
        program = r"C:\Program Files (x86)\Microsoft\Skype for Desktop\Skype.exe"
        print('Withdrawed.. Ask Open File Name:')
        if os.path.isdir(initialdir):
            if os.path.isfile(program):
                filename = program
            else:
                filename = askopenfilename(initialdir=initialdir, filetypes=[('exe', '.exe')])
        else:
            filename = askopenfilename(filetypes=[('exe', '.exe')])

        print("File name: {}".format(filename))
        _file_list = re.split(r'[\/\\]+', filename)
        _file = _file_list[-1]
        if re.match('Skype.exe', _file):
            loop_handle_fn(filename)
            # messagebox.showinfo('Success', 'Done.')
        else:
            messagebox.showerror("Error", "It's not Skype.exe")

        
    except KeyboardInterrupt as ke:
        print('stop.')
        exit(2)
    except Exception as ee:
        print(ee)
        exit(2)

    print('done.')