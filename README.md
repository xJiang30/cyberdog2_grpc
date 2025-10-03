# grpc move, record, capture photo 

## Install

`pip3 install grpcio grpcio_tools`

`python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./cyberdog_app.proto`

## Run
Please first obtain the IP of the robot in the LAN. The parameters are: the ip of the robot, CA certificate, client key, and client certificate.
请先获取到机器人在局域网中的IP，参数分别为：机器人的ip、CA证书、client秘钥、client证书  
`python3 grpc_teleop.py 192.168.xxx.xxx cert/ca-cert.pem cert/client-key.pem cert/client-cert.pem`   
Operation method: w, x, a, and d are accelerations from front, back, left and right respectively. The speed remains unchanged when the keyboard is not pressed, s is stop, and esc is exit，and p is stop recording or get one real-time pictures and save to local files.
操作方法：w、x、a、d分别为前后左右加速，不按键盘时速度保持不变，s为停止，esc为退出，p为停止录像或截取实时图像，并保存到本地文件。


'python3 demo.py 192.168.31.126 cert/ca-cert.pem cert/client-key.pem cert/client-cert.pem'

python3 grpc_teleop.py 192.168.31.126 cert/ca-cert.pem cert/client-key.pem cert/client-cert.pem 

python3 nav2.py 192.168.31.126 cert/ca-cert.pem cert/client-key.pem cert/client-cert.pem