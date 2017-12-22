import machine
import time
import utime
import ubinascii
import webrepl

from umqtt.simple import MQTTClient



class ConfigManager:

    # These defaults are overwritten with the contents of /config.json by load_config()
    CONFIG = {
        "broker": "192.168.1.50",
        "button_pin": 12, 
        "led_pin": 14,
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
        self.pin = machine.Pin(pin_number, machine.Pin.IN)
        self.handler = None
    
    def handle(self, pin):
        # current_value = pin.value()
        # print(current_value)
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
    LED_ON_TIME = 500

    def __init__(self, pin_number):
        self.pin = machine.Pin(pin_number, machine.Pin.OUT)

    def on(self):
        self.pin.on()

    def off(self):
        self.pin.off()

    def blink(self):
        # TODO
        print("Blinking led")

class Mqtt:
    def __init__(self, client_id, broker):
        self.client_id = client_id
        self.client = MQTTClient(client_id, broker)
        self.client.connect()
        print("Connected to {}".format(broker))

    def publish(self, topic, message):
        print(self.client_id)
        self.client.publish(
            '{}/{}'.format(
                topic,
                self.client_id
            ), 
            message
        )

# def button_pressed(self):
#     global time_since_last_press
#     global time_led_off
#     global led_pin
#     if (time.ticks_ms() > (time_since_last_press + DEBOUNCE)):
#         print("Button pressed")
#         led_pin.on()
#         time_led_off = time.ticks_ms() + LED_ON_TIME
#     time_since_last_press = time.ticks_ms()
#     if time.ticks_ms() > time_led_off:
#         led_pin.off()
    

def main():
    #while True:
    #    data = sensor_pin.value()
    #    client.publish('{}/{}'.format(CONFIG['topic'],
    #                                      CONFIG['client_id']),
    #                                      bytes(str(data), 'utf-8'))
    #    print('Sensor state: {}'.format(data))
    #    time.sleep(5)
    time.sleep(10)

def button_handler(pin):
    print("Button pressed")
    mqtt.publish(config['topic'], "{'button': 'pressed'}")


if __name__ == '__main__':
    config_manager = ConfigManager()
    config = config_manager.get_config()

    button = Button(config['button_pin'])
    led = Led(config['led_pin'])
    mqtt = Mqtt(config['client_id'],config['broker'])

    button.set_handler(button_handler)

    led.on()
    time.sleep(10)
    led.off()
