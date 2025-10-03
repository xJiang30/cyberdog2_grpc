import os
import select
import sys

if os.name == 'nt':
    import msvcrt
    print('os.name is nt')
else:
    import termios
    import tty 
    print('os.name is', os.name)

import grpc
import json
import cyberdog_app_pb2
import cyberdog_app_pb2_grpc
import cv2
import numpy as np
import io
import shutil
import rospy
import subprocess


class Teleop:
    def __init__(self):
        # 省略其他初始化代码...
        if os.name != 'nt':
            self.__settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        # 在Windows上使用msvcrt
        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')
        # 在Linux上使用termios和tty
        else:
            tty.setraw(sys.stdin.fileno())
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                key = sys.stdin.read(1)
            else:
                key = ''
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.__settings)
            return key

class Client:
    def __init__(self, cyberdog_ip: str, ca_cert: str, client_key: str, client_cert: str):
        creds = grpc.ssl_channel_credentials(
            open(ca_cert, 'rb').read(),
            open(client_key, 'rb').read(),
            open(client_cert, 'rb').read())
        channel_options = (('grpc.ssl_target_name_override', 'cyberdog2.server'), 
                           ('grpc.default_authority', 'cyberdog2.server'))
        chennel = grpc.secure_channel(cyberdog_ip + ':50052', creds, channel_options)
        self.__stub = cyberdog_app_pb2_grpc.GrpcAppStub(chennel)
        print('Client is ready.')



    def move(self, name_code, params):
        try:
            result_list = self.__stub.sendMsg(
                cyberdog_app_pb2.SendRequest(
                    nameCode=name_code,
                    params=params))
            resp = list(result_list)
        except:
            print('failed to send msg')

    def relocate(self):
        param = {
            "type":7,
            "outdoor":False
        }
        response = self.__stub.sendMsg(
            cyberdog_app_pb2.SendRequest(
                nameCode=6004,
                params=json.dumps(param)))
        for i in response:
            print(i)
    
    def AB_nav(self):
        param = {
            "type":1,
            "goalX":0,
            "goalY":0
        }
        response = self.__stub.sendMsg(
            cyberdog_app_pb2.SendRequest(
                nameCode=6004,
                params=json.dumps(param)))
        for i in response:
            print(i)

    def image_tran(self):
        param1 = {
            'offer_sdp': '{"type": "offer", "sdp": "v=0\r\no=- 5173367415324555211 2 IN IP4 127.0.0.1\r\ns=-\r\nt=0 0\r\na=extmap-allow-mixed\r\na=msid-semantic: WMS"}',
            #'uid': 'your_app_identifier',
            'height': 1280,
            'width': 720,
            'alignment': 'middle'
        }
        response1 = self.__stub.sendMsg(
            cyberdog_app_pb2.SendRequest(
                nameCode=4001,
                params=json.dumps(param1)))
        for i in response1:
            print(i)

        # param2 = {
        #     'c_sdp':{"sdpMid":"image","sdpMLineIndex":0,"candidate":"candidate:1 1 udp 9 192.168.31.126 9 typ host"}
        # }
        # response2 = self.__stub.sendMsg(
        #     cyberdog_app_pb2.SendRequest(
        #         nameCode=4001,
        #         params=json.dumps(param2)
        #     )
        # )
        # for j in response2:
        #     print(j)


    def start_record(self):
         param = {"command":2}
         response = self.__stub.sendMsg(
              cyberdog_app_pb2.SendRequest(
                   nameCode=4002,
                   params=json.dumps(param)))
         for i in response:
            print(i)
         
    def end_record(self):
         param = {"command":3}
         response = self.__stub.getFile(
              cyberdog_app_pb2.SendRequest(
                   nameCode=4002,
                   params=json.dumps(param)))
         for i in response:
              record = i.buffer
              print(i.error_code)
              print(i.file_size)
         if len(record) == 0:
             print("Invalid image data received.")
         #cv2.namedWindow('Cyberdog Camera', cv2.WINDOW_NORMAL)
         
         with io.BytesIO(record) as f:
            with open('temp_video1.mp4', 'wb') as temp_file:
                f.seek(0)
                shutil.copyfileobj(f, temp_file)
        
    
    def get_image(self):
        # try:
            params = {"command":1}

            response = self.__stub.getFile(
                cyberdog_app_pb2.SendRequest(
                    nameCode=4002,
                    params=json.dumps(params)))
            for i in response:
              image_data = i.buffer
              print(i.error_code)
              print(i.file_size)

            #cv2.namedWindow('Cyberdog Camera', cv2.WINDOW_NORMAL)

            with open('temp_image.jpg', 'wb') as temp_file:
                temp_file.write(image_data)
            subprocess.run(["./darknet/darknet", "detect", "cfg/yolov3-voc.cfg", "backup/yolov3-voc.backup", "temp_image.jpg"])
        #     image = cv2.imdecode(np.frombuffer(image_data,np.uint8), cv2.IMREAD_COLOR)
        #     #cv2.imshow('Cyberdog Camera',image)
        #     while cv2.waitKey(1) < 0:  # 等待用户关闭窗口
        #         cv2.imshow('Cyberdog Camera', image)
        #     #cv2.waitKey(1)
        # # except:
        # #     print('failed to send msg')
    


class moveMSG:
    def __init__(self, acc=[0.1, 0.0, 1.0], freq=10.0, max_vel=[1.0, 0.0, 1.5]):
        self.__vel = [0.0, 0.0, 0.0]
        self.__acc = acc
        self.__freq = freq
        self.__max_vel = max_vel
        self.__settings = None
        if os.name != 'nt':
            self.__settings = termios.tcgetattr(sys.stdin)
        print('moveMSG is ready')

    def updateVel(self, delta_vel: list):
        updated = False
        for i in range(0, 3):
            if abs(delta_vel[i]) > 0.00001:
                updated = True
            else:
                continue 
            self.__vel[i] += delta_vel[i]
            if self.__vel[i] > self.__max_vel[i]:
                self.__vel[i] = self.__max_vel[i]
            elif self.__vel[i] < -self.__max_vel[i]:
                self.__vel[i] = -self.__max_vel[i]
        if updated:
            print('vel:', self.__vel)
        return self.__vel

    def __getKey(self, settings):
        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key
         	
    def getVelFromKey(self):
        key = self.__getKey(self.__settings)
        delta_vel = [0.0, 0.0, 0.0]
        if key == '\x1B':
            return (0, [])
        elif key == 'w' or key == 'W':
            delta_vel[0] = self.__acc[0] / self.__freq
        elif key == 'x' or key == 'X':
            delta_vel[0] = -self.__acc[0] / self.__freq
        elif key == 'a' or key == 'A':
            delta_vel[2] = self.__acc[2] / self.__freq
        elif key == 'd' or key == 'd':
            delta_vel[2] = -self.__acc[2] / self.__freq
        elif key == 's' or key == 'S':
            delta_vel[0] = -self.__vel[0]
            delta_vel[2] = -self.__vel[2]
        return (1002, delta_vel)

class ProtoEncoder:
    def encodeVel(self, vel):
        cmd = {}
        cmd['motion_id'] = 303
        cmd['cmd_type'] = 1
        cmd['cmd_source'] = 3
        cmd['value'] = 0
        cmd['step_height'] = [0.06, 0.06]
        cmd['vel_des'] = vel
        return json.dumps(cmd)

    def stopSignal(self):
        cmd = {}
        cmd['motion_id'] = 303
        cmd['cmd_type'] = 2
        cmd['cmd_source'] = 3
        cmd['value'] = 0
        cmd['step_height'] = [0.0, 0.0]
        cmd['vel_des'] = [0.0, 0.0, 0.0]
        return json.dumps(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('Please input gRPC server IP, CA certificate, client key and client certificate')
        exit()
    grpc_client = Client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    move_msg = moveMSG()
    encoder = ProtoEncoder()
    stop_signal = False
    
    teleop = Teleop()

    grpc_client.image_tran()
    #grpc_client.start_record()
    grpc_client.relocate()
    
    while True:
        # move
        result, delta_vel = move_msg.getVelFromKey()
        if result == 0:
            print('exit')
            break
        vel = move_msg.updateVel(delta_vel)
        key = teleop.get_key()
        if key == 'p' or key == 'P':
             #grpc_client.end_record()
            grpc_client.get_image()
        if abs(vel[0]) < 0.01 and abs(vel[2]) < 0.01:
            if stop_signal:
                continue
            stop_signal = True
        else:
            stop_signal = False
        if stop_signal:
            json_str = encoder.stopSignal()
        else:
            json_str = encoder.encodeVel(vel)
        grpc_client.move(1002, json_str)

