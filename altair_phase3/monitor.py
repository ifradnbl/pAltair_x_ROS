import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Monitor(Node):
    def __init__(self):
        super().__init__('mission_control_monitor')
        self.create_subscription(String, 'rover_telemetry', self.on_msg, 10)

    def on_msg(self, msg):
        d = json.loads(msg.data)
        print(f"[T+{d['elapsed_s']:6.1f} s] Battery: {d['battery_pct']:5.1f} % | "
              f"Temp: {d['temperature_c']:5.1f} C | Wheel: {d['wheel_speed_mps']:.2f} m/s")
        if d['battery_pct'] < 25.0:
            self.get_logger().warn(f"LOW BATTERY: {d['battery_pct']} % (< 25 %)")

def main():
    rclpy.init()
    n = Monitor()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    n.destroy_node()
    rclpy.try_shutdown()
