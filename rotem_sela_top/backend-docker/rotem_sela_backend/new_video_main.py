import json
from linux_system_monitor import LinuxSystemStatus
import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.web import RequestHandler, Application
import asyncio
import v4l2py
from robot_main2 import RobotMain, stopVideo
import threading
import json
import multiprocessing
import time

CAM_PORTS_FLIP = {
            5000 : ['5.1','3.1','3.2','5.2','1.2'],
            5001: ['6.1','4.1','4.2','2.2','6.2'],
            5002: ['1.1','1.1','1.1','1.1','4.1'],
            5003: ['2.1','2.1','2.1','3.1','2.1']
           
            }

CAM_PORTS_NOT_FLIP = {
           
            5000: ['1.1','1.1','1.1','1.1','4.1'],
            5001: ['2.1','2.1','2.1','3.1','2.1'],
            5002 : ['5.1','3.1','3.2','5.2','1.2'],
            5003: ['6.1','4.1','4.2','2.2','6.2']
            }


CAM_PORTS = CAM_PORTS_NOT_FLIP

cameras = {}
devices = {}
isMain = True
subQueues = []
txQueues = []
barrier = multiprocessing.Barrier(4)
txQueues = []

def sendCamsCB():
    return txQueues

def sendCamsCB():
    return txQueues



def map_cams():
    cameras = LinuxSystemStatus.list_usb_cameras()

    id2name = {"1.1":3,"1.2.1":2,"1.2.2":1,"1.2.3":6,"1.2.4":5,"1.4":4}

    map = {
            str(id2name[cameras[0][0].split("-")[1]])+".1":{'dev' : cameras[0][1], 'width' : 640 ,'height' : 480, 'name':'cam1-side'},
            str(id2name[cameras[0][0].split("-")[1]])+".2":{'dev' : cameras[0][1], 'width' : 640 ,'height' : 400, 'name':'cam1-front'},
            str(id2name[cameras[1][0].split("-")[1]])+".1":{'dev' : cameras[1][1], 'width' : 640 ,'height' : 480, 'name':'cam2-front'},
            str(id2name[cameras[1][0].split("-")[1]])+".2":{'dev' : cameras[1][1], 'width' : 640 ,'height' : 400, 'name':'cam2-side'},
            str(id2name[cameras[2][0].split("-")[1]])+".1":{'dev' : cameras[2][1], 'width' : 640 ,'height' : 480, 'name':'cam3-side'},
            str(id2name[cameras[2][0].split("-")[1]])+".2":{'dev' : cameras[2][1], 'width' : 640 ,'height' : 400, 'name':'cam3-front'},
            str(id2name[cameras[3][0].split("-")[1]])+".1":{'dev' : cameras[3][1], 'width' : 640 ,'height' : 480, 'name':'cam4-front'},
            str(id2name[cameras[3][0].split("-")[1]])+".2":{'dev' : cameras[3][1], 'width' : 640 ,'height' : 400, 'name':'cam4-side'},
            str(id2name[cameras[4][0].split("-")[1]])+".1":{'dev' : cameras[4][1], 'width' : 640 ,'height' : 480, 'name':'cam5-front'},
            str(id2name[cameras[4][0].split("-")[1]])+".2":{'dev' : cameras[4][1], 'width' : 640 ,'height' : 400, 'name':'cam5-side'},
            str(id2name[cameras[5][0].split("-")[1]])+".1":{'dev' : cameras[5][1], 'width' : 640 ,'height' : 480, 'name':'cam5-front'},
            str(id2name[cameras[5][0].split("-")[1]])+".2":{'dev' : cameras[5][1], 'width' : 640 ,'height' : 400, 'name':'cam5-side'},
           }
    
    print(map)
    return map
    
class CorsHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()


class IndexHandler(CorsHandler):
    def get(self):
        self.write(json.dumps('backend only'))


def websocket_server(port):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = tornado.web.Application(ChannelHandler.urls())
        # Setup HTTP Server
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port, '0.0.0.0')
        tornado.ioloop.IOLoop.instance().start()
       
def flipCams():
    for q in subQueues:
        q.put({'event':'flip'})

def toggleCams(event):
    for q in subQueues:
        q.put({'event':f'{event}'})

def sendCommand(command:int):
    for q in subQueues:
        q.put({
            'command':command
        })
        
def videoFeedHandler(port, cam_id, queue, barrier, qt):
        global isMain
        isMain = False
        webSocket_thread = threading.Thread(target=websocket_server, args=(port,))
        webSocket_thread.start()
        res = map_cams()
        global cameras
        global devices
        camIdx = 0
        isFlip = False

        while True:
            video_dev = res[cam_id[camIdx]]['dev']
            if video_dev not in cameras:
                cameras[cam_id[camIdx]] = video_dev

            print(f"{cam_id} start feed")
            print(f"Open video device {video_dev}")
            barrier.wait();
            
            startTS = time.time()
            
            with v4l2py.Device(video_dev) as device:
                devices[cam_id[camIdx]] = device
                device.set_format(buffer_type=1, width=res[cam_id[camIdx]]['width'], height=res[cam_id[camIdx]]['height'], pixel_format='MJPG')
                device.set_fps(buffer_type=1, fps=10)
                for frame in device:
                    try:
                        if stopVideo:
                            break
                       
                        ChannelHandler.send_message(frame.data)
                        qt.put({"port":port,
                                    "cam_name":res[cam_id[camIdx]]['name']})
                        try:
                            item = queue.get(block=False)

                            if item['event'] == 'flip':
                                isFlip = not isFlip
                                if isFlip:
                                    cam_id = CAM_PORTS_FLIP[port]
                                else:
                                    cam_id = CAM_PORTS_NOT_FLIP[port]

                            if item['event'] == str(ord('0')):
                                print("0 press")
                                camIdx = 0
                            if item['event'] ==  str(ord('1')):
                                print("1 press")
                                camIdx = 1
                            if item['event'] == str(ord('2')):
                                print("2 press")
                                camIdx = 2
                            if item['event'] == str(ord('3')):
                                print("3 press")
                                camIdx = 3
                            if item['event'] == str(ord('4')):
                                print("4 press")
                                camIdx = 4
                                
                            qt.put({"port":port,
                                    "cam_name":res[cam_id[camIdx]]['name']})
                            break
                        except Exception:
                            # traceback.print_exc()
                            pass
                    except Exception:
                        # traceback.print_exc()
                        break
                  

def make_app():
    return Application([
        (r"/", IndexHandler)
    ])

class ChannelHandler(tornado.websocket.WebSocketHandler):
    
    clients = set()

    def open(self):
        ChannelHandler.clients.add(self)

    def on_close(self):
        try:
            ChannelHandler.clients.remove(self)
        except Exception as e:
            print(str(e))

    @classmethod
    def send_message(cls, message: str):
        # print(f"Sending message {message} to {len(cls.clients)} client(s).")
        
        try:
            for client in cls.clients:
                try:
                    if isMain:
                        client.write_message(message, binary=False)
                    else:
                        client.write_message(message, binary=True)
                except Exception as e:
                    cls.clients.remove(client)
                    break
        except Exception as e:
            print(str(e))
          
    """
    Handler that handles a websocket channel
    """
    @classmethod
    def urls(cls):
        return [
            (r'/ws', cls,{}),  # Route/Handler/kwargs
        ]
    
    def initialize(self):
        self.channel = None
    
    def check_origin(self, origin):
        """
        Override the origin check if needed
        """
        return True
    


if __name__ == "__main__":
    processes = []
    
    for item in CAM_PORTS:
        queue = multiprocessing.Queue()
        qt = multiprocessing.Queue()
        process = multiprocessing.Process(target=videoFeedHandler, args=(item, CAM_PORTS[item], queue, barrier, qt))
        processes.append(process)
        subQueues.append(queue)
        txQueues.append(qt)
        process.start()

    app = tornado.web.Application(ChannelHandler.urls())
    http_server = tornado.httpserver.HTTPServer(app)
    # Setup HTTP Server
    http_server.listen(8888, '0.0.0.0')
    print(f"Websocket started")
    # Start IO/Event loop
   
    obj = RobotMain()
    obj.setTelemetryChannel(ChannelHandler)
    obj.setFlipCallback(flipCams)
    obj.setCommandKB(toggleCams) #michal - cameras, toggle from keyboard
    # obj.setToggleCallback(toggleCams) -> no toggle from button circle
    obj.setCamsCallback(sendCamsCB)


    tornado.ioloop.IOLoop.instance().start()
    for process in processes:
        process.join()
 

