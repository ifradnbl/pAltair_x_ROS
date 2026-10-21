import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_msgs.msg import Bool
from std_srvs.srv import Trigger

TARGETS = [('Bottle', 8.0, 5.5), ('Mallet', 8.0, 8.0), ('Base', 5.5, 5.5)]
TOL = 0.3

class Mission(Node):
    def __init__(self):
        super().__init__('mission_node')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.create_subscription(Pose, '/turtle1/pose', self.on_pose, 10)
        self.create_subscription(Bool, '/field_blocked', self.on_blocked, 10)
        self.create_service(Trigger, '/resume_mission', self.on_resume)
        self.create_timer(0.1, self.tick)
        self.pose = None
        self.blocked = False
        self.state = 'RUNNING'
        self.idx = 0

    def on_pose(self, msg):
        self.pose = msg

    def on_blocked(self, msg):
        self.blocked = msg.data
        if msg.data and self.state == 'RUNNING':
            self.state = 'PAUSED'
            self.get_logger().warn('Route BLOCKED -> PAUSED')
        elif not msg.data:
            self.get_logger().info('Report cleared. Still PAUSED until /resume_mission.')

    def on_resume(self, req, res):
        if self.pose is None:
            res.success, res.message = False, 'Rejected: no pose yet'
        elif self.state == 'DONE':
            res.success, res.message = False, 'Rejected: mission complete'
        elif self.blocked:
            res.success, res.message = False, 'Rejected: route still blocked'
        elif self.state != 'PAUSED':
            res.success, res.message = False, 'Rejected: not paused'
        else:
            self.state = 'RUNNING'
            res.success, res.message = True, 'Resumed'
            self.get_logger().info('RESUMED')
        return res

    def send(self, lin, ang):
        m = Twist(); m.linear.x = lin; m.angular.z = ang
        self.pub.publish(m)

    def tick(self):
        if self.pose is None or self.state == 'DONE':
            return
        if self.state == 'PAUSED':
            self.send(0.0, 0.0)
            return
        name, gx, gy = TARGETS[self.idx]
        p = self.pose
        dx, dy = gx - p.x, gy - p.y
        d = math.hypot(dx, dy)
        if d <= TOL:
            self.get_logger().info(f'ARRIVED at {name}')
            self.idx += 1
            if self.idx >= len(TARGETS):
                self.send(0.0, 0.0)
                self.state = 'DONE'
                self.get_logger().info('DONE')
            return
        err = math.atan2(dy, dx) - p.theta
        err = math.atan2(math.sin(err), math.cos(err))
        if abs(err) > 0.3:
            self.send(0.0, max(-3.0, min(3.0, 4.0 * err)))
        else:
            self.send(min(2.0, 1.5 * d), max(-3.0, min(3.0, 4.0 * err)))

def main():
    rclpy.init()
    n = Mission()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    n.destroy_node()
    rclpy.try_shutdown()
