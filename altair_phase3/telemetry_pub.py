import json, time, math, random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TelemetryPublisher(Node):
    def __init__(self):
        super().__init__('mars_telemetry_publisher')
        self.declare_parameter('start_battery_pct', 40.0)
        self.declare_parameter('depletion_pct_per_s', 1.0)
        self.start = self.get_parameter('start_battery_pct').value
        self.rate = self.get_parameter('depletion_pct_per_s').value
        self.t0 = time.monotonic()
        self.pub = self.create_publisher(String, 'rover_telemetry', 10)
        self.create_timer(1.0, self.tick)

    def tick(self):
        t = time.monotonic() - self.t0
        data = {
            'battery_pct': round(max(0.0, self.start - self.rate * t), 1),
            'temperature_c': round(25 + 5 * math.sin(t / 10) + random.uniform(-0.5, 0.5), 1),
            'wheel_speed_mps': round(0.5 + 0.2 * math.sin(t / 3), 2),
            'elapsed_s': round(t, 1),
        }
        self.pub.publish(String(data=json.dumps(data)))
        self.get_logger().info(f"Published: {data}")

def main():
    rclpy.init()
    n = TelemetryPublisher()
    try:
        rclpy.spin(n)
    except KeyboardInterrupt:
        pass
    n.destroy_node()
    rclpy.try_shutdown()
