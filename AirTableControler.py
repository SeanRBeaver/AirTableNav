import requests
import time
import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import Twist
from irobot_create_msgs.action import Dock, Undock
from irobot_create_msgs.msg import LightringLeds, LedColor

#airtable specifics (super secret token ohno)
URL     = 'https://api.airtable.com/v0/appxYDs8cGdOsn5nH/Table%201'
Headers = {
    'Authorization': 'Bearer patUQ3nF5wWjGlMRb.361191ea73cbd06bfa25a7cf0e309dcf82ee4cfb52bfe83877a2b0e0d9f4877b',
    'Content-Type': 'application/json'
}

#general setup
class RobotController(Node):
    def __init__(self):
        super().__init__('robot_airtable')

        self.cmd_pub   = self.create_publisher(Twist,         '/cmd_vel',       10)
        self.light_pub = self.create_publisher(LightringLeds, '/cmd_lightring', 10)

        self.dock_client   = ActionClient(self, Dock,   'dock')
        self.undock_client = ActionClient(self, Undock, 'undock')

        print("Robot ready!")

    #setup drive/turn
    def drive(self, linear, angular):
        msg = Twist()
        msg.linear.x  = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

    #setup lights
    def set_lights(self, r, g, b):
        msg = LightringLeds()
        msg.override_system = True
        msg.leds = [LedColor(red=r, green=g, blue=b) for i in range(6)]
        self.light_pub.publish(msg)

    #setup docking/undocking
    def dock(self):
        self.dock_client.wait_for_server()
        self.dock_client.send_goal_async(Dock.Goal())
    def undock(self):
        self.undock_client.wait_for_server()
        self.undock_client.send_goal_async(Undock.Goal())

#look for pending commands in airtable
def get_pending():
    r = requests.get(URL, headers=Headers, params={
        'filterByFormula': "{Status}='pending'"
    })
    return r.json().get('records', [])

#mark those commands done
def mark_done(record_id):
    requests.patch(f"{URL}/{record_id}", headers=Headers, json={'fields': {'Status': 'done'}})

#execute those airtable commands
def execute(robot, command):
    Speed     = 0.3
    TurnSpeed = 0.8

    drive_cmds = {
        'forward':  ( Speed,  0.0),
        'backward': (-Speed,  0.0),
        'left':     (  0.0,  TurnSpeed),
        'right':    (  0.0, -TurnSpeed),
        'stop':     (  0.0,  0.0),
    }

    #change light color
    if command.startswith('light:'):
        r, g, b = [int(x) for x in command.split(':')[1].split(',')]
        robot.set_lights(r, g, b)
        print(f"Lights: {r},{g},{b}")

    #execute drive commands
    elif command in drive_cmds:
        robot.drive(*drive_cmds[command])
        print(f"Executed: {command}")
    
    #execute dock/undock
    elif command == 'dock':
        robot.dock()
        print("Docking")
    elif command == 'undock':
        robot.undock()
        print("Undocking")

#ROS setup
rclpy.init()
robot = RobotController()
spin_thread = threading.Thread(target=rclpy.spin, args=(robot,), daemon=True)
spin_thread.start()

try:
    while True:
        #look for pending commands
        records = get_pending()
        
        #execute each command and mark done
        for record in records:
            command = record['fields'].get('Command', '').lower()
            execute(robot, command)
            mark_done(record['id'])
       
        #loop time
        time.sleep(0.2)
except KeyboardInterrupt:
    print("Stopped")
finally:
    robot.drive(0.0, 0.0)
    robot.destroy_node()
    rclpy.shutdown()