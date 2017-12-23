import machine
import time
import utime
import ubinascii
import webrepl

from umqtt.robust import MQTTClient

doorbell = True

class ConfigManager:

    # These defaults are overwritten with the contents of /config.json by load_config()
    CONFIG = {
        "broker": "192.168.1.50",
        "button_pin": 12, 
        "led_pin_1": 14,
        "led_pin_2": 16,
        "client_id": b"esp8266_" + ubinascii.hexlify(machine.unique_id()),
        "topic": b"doorbell",
    }

    def __init__(self):
        self.load_config()

    def load_config(self):
        import ujson as json
        try:
            with open("/config.json") as f:
                config = json.loads(f.read())
        except (OSError, ValueError):
            print("Couldn't load /config.json")
            save_config()
        else:
            self.CONFIG.update(config)
            print("Loaded config from /config.json")

    def save_config(self):
        import ujson as json
        try:
            with open("/config.json", "w") as f:
                f.write(json.dumps(self.CONFIG))
        except OSError:
            print("Couldn't save /config.json")

    def get_config(self):
        return self.CONFIG


class Button:
    DEBOUNCE = 50

    def __init__(self, pin_number):
        self.pin = machine.Pin(pin_number, machine.Pin.IN, machine.Pin.PULL_UP)
        self.handler = None
    
    def handle(self, pin):
        active = True
        count = 0
        while(count < self.DEBOUNCE):
            if pin.value() != 0:
                active = False
            count += 1
            utime.sleep_ms(1)
        if active:
            self.handler(pin)

    def set_handler(self, handler):
        self.handler = handler
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.handle)


class Led:
    LED_BLINK_TIME = 500

    def __init__(self, pin_number_1, pin_number_2):
        self.pin1 = machine.Pin(pin_number_1, machine.Pin.OUT)
        self.pin2 = machine.Pin(pin_number_2, machine.Pin.OUT)
        self.on()

    def on(self):
        self.pin1.on()
        self.pin2.on()

    def off(self):
        self.pin1.off()
        self.pin2.off()

    def blink(self):
        for i in range(0,20):
            self.off()
            utime.sleep_ms(200)
            self.on()
            utime.sleep_ms(200)
        self.on()

class Mqtt:
    def __init__(self, client_id, broker):
        self.client_id = client_id
        self.client = MQTTClient(client_id, broker)
        self.client.connect()
        print("Connected to {}".format(broker))

    def publish(self, topic, message):
        self.client.publish(
            '{}/{}'.format(
                topic,
                self.client_id
            ), 
            message
        )


def button_handler(pin):
    print("Button pressed")
    try:
        mqtt.publish(config['topic'], "{'button': 'pressed'}")
        led.blink()
    except Exception as msg:
        print(msg)
        for i in range(0,66):
            led.off()
            utime.sleep_ms(100)
            led.on()
            utime.sleep_ms(50)


# if __name__ == '__main__':
print("Doorbell application")
config_manager = ConfigManager()
config = config_manager.get_config()

button = Button(config['button_pin'])
led = Led(config['led_pin_1'], config['led_pin_2'])

button.set_handler(button_handler)

mqtt = False
while not mqtt:
    try:
        mqtt = Mqtt(config['client_id'],config['broker'])
    except Exception as msg:
        print("MQTT Not connected, trying again in 5 seconds")
        for i in range(0,3):
            led.off()
            utime.sleep_ms(200)
            led.on()
            utime.sleep_ms(100)
        time.sleep(5)
    

time.sleep(5)
