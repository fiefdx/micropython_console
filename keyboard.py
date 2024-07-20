from machine import Pin, PWM


class KeyBoard(object):
    def __init__(self):
        self.light = 4
        self.light_min = 0
        self.light_max = 15
        self.light_levels =[0, 100, 500, 1000, 5000, 6553, 13106, 19659, 26212, 32765, 39318, 45871, 52424, 58977, 65530]
        self.display_pwm = PWM(Pin(8))
        self.display_pwm.freq(1000)
        self.update_light_level()
        self.x_lines = [
            Pin(10, Pin.OUT), # 0
            Pin(11, Pin.OUT), # 1
            Pin(13, Pin.OUT), # 2
            Pin(14, Pin.OUT), # 3
            Pin(15, Pin.OUT), # 4
            Pin(16, Pin.OUT), # 5
            Pin(17, Pin.OUT), # 6
            Pin(18, Pin.OUT), # 7
            Pin(19, Pin.OUT), # 8
            Pin(20, Pin.OUT), # 9
        ]
        self.y_lines = [
            Pin(21, Pin.IN, Pin.PULL_UP), # 0
            Pin(22, Pin.IN, Pin.PULL_UP), # 1
            Pin(26, Pin.IN, Pin.PULL_UP), # 2
            Pin(27, Pin.IN, Pin.PULL_UP), # 3
            Pin(28, Pin.IN, Pin.PULL_UP), # 4
        ]
        self.keys = [
            [("q", "Q", "`"), ("w", "W", "~"), ("e", "E", "'"), ("r", "R", '"'), ("t", "T", "-"), ("y", "Y", "+"), ("u", "U", "["), ("i", "I", "]"), ("o", "O", "{"), ("p", "P", "}")],
            [("a", "A", "light-up"), ("s", "S", "SAVE"), ("d", "D"), ("f", "F", ";"), ("g", "G", ":"), ("h", "H", "="), ("j", "J", "_"), ("k", "K", "\\"), ("l", "L", "|"), ("/", "/", "?")],
            [("z", "Z", "light-down"), ("x", "X"), ("c", "C"), ("v", "V"), ("b", "B"), ("n", "N"), ("m", "M"), (",", ",", "<"), (".", ".", ">"), ("\b", "\b", "\b")],
            [("SH", "SH", "SH"), ("CP", "CP", "CP"), ("SE", "SE", "SE"), ("ES", "ES", "ES"), (" ", " ", " "), ("\n", "\n", "\n"), ("UP", "UP", "SUP"), ("DN", "DN", "SDN"), ("LT", "LT", "LT"), ("RT", "RT", "RT")],
            [("1", "1", "!"), ("2", "2", "@"), ("3", "3", "#"), ("4", "4", "$"), ("5", "5", "%"), ("6", "6", "^"), ("7", "7", "&"), ("8", "8", "*"), ("9", "9", "("), ("0", "0", ")")],
        ]
        self.press_buttons = [
            [False, False, False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False, False, False],
            [False, False, False, False, False, False, False, False, False, False],
        ]
        self.buttons = []
        self.release = []
        self.mode = "DF" # default
        self.button = ""
        self.continue_press_counter = 0
        self.continue_press_interval = 6
        
    def update_light_level(self):
        self.display_pwm.duty_u16(self.light_levels[self.light])
        
    def clear(self):
        self.button = ""
        self.buttons.clear()

    def scan(self):
        for x in range(10):
            for i in range(10):
                if i == x:
                    self.x_lines[i].low() # scan x line
                else:
                    self.x_lines[i].high() # disable other lines
            for y in range(5):
                if self.y_lines[y].value() == False: # pressd
                    if self.press_buttons[y][x]: # already pressed
                        if self.continue_press_counter >= self.continue_press_interval and self.continue_press_counter % (self.continue_press_interval // 3) == 0:
                            keys = self.keys[y][x]
                            key = keys[0]
                            if self.mode == "SH":
                                if len(keys) > 2:
                                    key = keys[2]
                            elif self.mode == "CP":
                                key = keys[1]
                            if key == "light-up":
                                self.light += 1
                                if self.light >= self.light_max:
                                    self.light = self.light_max - 1
                                self.update_light_level()
                            elif key == "light-down":
                                self.light -= 1
                                if self.light <= 0:
                                    self.light = 0
                                self.update_light_level()
                            if key not in ("light-up", "light-down", "SH", "CP"):
                                self.button = key
                        self.continue_press_counter += 1
                    self.press_buttons[y][x] = True
                    # print("press: ", self.keys[y][x])
                else: # not press
                    if self.press_buttons[y][x]:
                        if self.continue_press_counter > 0:
                            self.continue_press_counter = 0
                        # print("release: ", self.keys[y][x])
                        if self.keys[y][x][0] == "SH": # SH mode change
                            if self.mode == "DF":
                                self.mode = "SH"
                            elif self.mode == "SH":
                                self.mode = "DF"
                        elif self.keys[y][x][0] == "CP": # CP mode change
                            if self.mode == "DF":
                                self.mode = "CP"
                            elif self.mode == "CP":
                                self.mode = "DF"
                        else: # other keys
                            keys = self.keys[y][x]
                            key = keys[0]
                            if self.mode == "SH":
                                if len(keys) > 2:
                                    key = keys[2]
                            elif self.mode == "CP":
                                key = keys[1]
                            if key == "light-up":
                                self.light += 1
                                if self.light >= self.light_max:
                                    self.light = self.light_max - 1
                                self.update_light_level()
                            elif key == "light-down":
                                self.light -= 1
                                if self.light <= 0:
                                    self.light = 0
                                self.update_light_level()
                            if key not in ("light-up", "light-down", "SH", "CP"):
                                self.button = key
                                # self.buttons.append(key)
                            # print("click: ", key, self.mode)
                    self.press_buttons[y][x] = False
        return self.button
        
