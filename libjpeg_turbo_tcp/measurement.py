import threading, time


class Measure(threading.Thread):
    def __init__(self, print_str):
        threading.Thread.__init__(self)
        self.delay_list = []
        self.print_str = print_str

    def run(self):
        while True:
            time.sleep(5)
            total = 0
            try:
                for _ in range(5):
                    total += self.delay_list.pop()
                total /= 5
            except:
                pass
            self.delay_list.clear()
            print(self.print_str, total)

    def add(self, item):
        self.delay_list.append(item)