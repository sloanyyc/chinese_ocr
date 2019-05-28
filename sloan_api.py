# -*- coding: UTF-8 -*-
"""
构建flask接口服务
接收 files={'image_file': ('text.jpg', BytesIO(bytes), 'application')} 参数识别验证码
需要配置参数：
    image_height = 300
    image_width = 400
"""
import json
from io import BytesIO
import os

import numpy as np
import time
from flask import Flask, request, jsonify, Response
from PIL import Image

import ocr

# 配置参数
api_image_dir = './api_file/'
api_done_dir = './rec_done/'
# Flask对象
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

def response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
#
# @app.route('/e', methods=['GET'])
# def report_image():
#     # curl - v 'http://127.0.0.1:5000/e?value=cjf3&time=154751883167'
#     if request.method == 'GET':
#         value = request.args.get("value")
#         timev = request.args.get("time")
#         timec = str(time.time()).replace(".", "")
#         file_name = "{}_{}.{}".format(value, timev, 'png')
#         file_path = os.path.join(api_done_dir + file_name)
#         dest_path = os.path.join(api_failed_dir + file_name)
#         content = None
#         if os.path.exists(file_path):
#             os.system('mv ' + file_path + ' ' + dest_path)
#             content = json.dumps({"error_code": 0})
#         else:
#             content = json.dumps({"error_code": 1002, 'error_message': 'not found'})
#         resp = response_headers(content)
#         return resp


@app.route('/ocr', methods=['POST'])
def up_image():
    # curl -v http://127.0.0.1:9436/ocr -F "image_file=@./test.jpg"
    if request.method == 'POST' and request.files.get('image_file'):
        timec = str(time.time()).replace(".", "")
        file = request.files.get('image_file')
        print(file)
        img_data = file.read()
        img = BytesIO(img_data)
        img = Image.open(img, mode="r")
        # username = request.form.get("name")
        size = img.size
        print("接收图片尺寸: {}".format(size))
        if size[0] < 20 or size[1] < 14:
            content = json.dumps({"error_code": 1003, 'error_message': 'file to small'})
            resp = response_headers(content)
            return resp
        # 保存图片
        file_name = "{}_{}.{}".format('temp', timec, 'jpg')
        print("保存图片： {}".format(file_name))
        file_path = os.path.join(api_image_dir + file_name)
        with open(file_path, 'wb') as f:
            f.write(img_data)
            f.close()
        s = time.time()
        value = []

        try:
            image = np.array(img.convert('RGB'))
            t = time.time()
            result, image_framed, scale = ocr.model(image)
            file_name = "{}_{}.{}".format('ocr_', timec, 'jpg')
            dest_path = os.path.join(api_done_dir + file_name)
            # os.system('mv '+file_path+' '+dest_path)
            Image.fromarray(image_framed).save(dest_path)
            print("Mission complete, it took {:.3f}s".format(time.time() - t))
            print("\nRecognition Result:\n")
            for key in result:
                print(result[key][1])
                value.append({'loc': [int(x) for x in result[key][0]],
                              'rate': result[key][2],'text': result[key][1]})

            e = time.time()
            print("识别结果: {}".format(json.dumps(value, ensure_ascii=False)))
            result = {
                'error_code': 0,
                'time': timec,  # 时间戳
                'value': value,  # 预测的结果
                'scale': scale,  #
                'author': 'sloanyyc',
                'speed_time(ms)': int((e - s) * 1000)  # 识别耗费的时间
            }
            return json.dumps(result, ensure_ascii=False)
        except:
            e = time.time()
            print('识别')
            result = {
                'error_code': 1004,
                'time': timec,  # 时间戳
                'value': [],  # 预测的结果
                'scale': 1,  #
                'author': 'sloanyyc',
                'speed_time(ms)': int((e - s) * 1000)  # 识别耗费的时间
            }
            return json.dumps(result, ensure_ascii=False)

    else:
        content = json.dumps({"error_code": 1001, 'error_message': 'only file via form post support'})
        resp = response_headers(content)
        return resp


if __name__ == '__main__':
    first_load_image = Image.open('test.png', mode="r")
    ocr.model(np.array(first_load_image.convert('RGB')))
    app.run(host='0.0.0.0', debug=False, port=9436)
