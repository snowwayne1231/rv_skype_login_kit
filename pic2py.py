import base64, sys, os

def pic2py(pics, py_name):
    datas = []
    for pic in pics:
        image = open(resource_path(pic), 'rb')
        key = pic.replace('.', '')
        key = key.replace('-', '_')
        value = base64.b64encode(image.read()).decode()
        image.close()
        datas.append('img{0} = "{1}"\n'.format(key, value))
    f = open('{0}.py'.format(py_name), 'w+')
    for data in datas:
        f.write(data)
    f.close()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./img-route")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    pics = os.listdir('./img-route')
    pic2py(pics, 'string_pic')