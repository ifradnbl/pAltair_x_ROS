import math, threading, queue, time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

PATTERNS = {
    'P': [(1.0, 0.0, 3.0), (0.0, math.pi, 1.0), (1.0, 0.0, 3.0)],
    'R': [(1.0, 0.0, 3.0), (0.0, math.pi / 2, 1.0), (1.0, 0.0, 1.5), (0.0, math.pi / 2, 1.0)] * 2,
    'Z': [(1.0, 0.0, 2.0), (0.0, math.pi / 4, 1.0), (1.0, 0.0, 2.0),
          (0.0, -math.pi / 2, 1.0), (1.0, 0.0, 2.0)],
}

class Menu(Node):
    def __init__(self):
        super().__init__('turtle_menu')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.q = queue.Queue()
        self.segs, self.i, self.seg_start, self.quit = [], 0, 0.0, False
        self.create_timer(0.05, self.tick)
        threading.Thread(target=self.read_input, daemon=True).start()
        self.prompt()

    def prompt(self):
        print('\nP=Patrol  R=Rectangle  Z=Zigzag  Q=Quit > ', end='', flush=True)

    def read_input(self):
        while True:
            try:
                self.q.put(input())
            except EOFError:
                self.q.put('Q')
                return

    def send(self, lin, ang):
        m = Twist(); m.linear.x = lin; m.angular.z = ang
        self.pub.publish(m)

    def tick(self):
        now = time.monotonic()
        if self.segs:
            while not self.q.empty():      # ignore input while moving
                self.q.get_nowait()
            if now - self.seg_start >= self.segs[self.i][2]:
                self.i += 1
                if self.i >= len(self.segs):
                    self.segs = []
                    self.send(0.0, 0.0)
                    print('Pattern finished, stopped.')
                    self.prompt()
                    return
                self.seg_start = now
            lin, ang, _ = self.segs[self.i]
            self.send(lin, ang)
            return
        try:
            cmd = self.q.get_nowait().strip().upper()
        except queue.Empty:
            return
        if cmd in PATTERNS:
            self.segs, self.i, self.seg_start = PATTERNS[cmd], 0, now
        elif cmd == 'Q':
            self.send(0.0, 0.0)
            self.quit = True
        else:
            print(f"Invalid input '{cmd}'. Use P, R, Z or Q.")
            self.prompt()

def main():
    rclpy.init()
    n = Menu()
    try:
        while rclpy.ok() and not n.quit:
            rclpy.spin_once(n, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    n.destroy_node()
    rclpy.try_shutdown()
