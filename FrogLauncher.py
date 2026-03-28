from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd
from time import sleep

#LCD setup
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
scan = i2c.scan()
if not scan:
    raise RuntimeError("LCD not found. Check wiring.")
I2C_ADDR = scan[0]  #grab first device address found on the bus
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)  #2 rows, 16 cols

#Button setup
buttons = [
    Pin(3, Pin.IN, Pin.PULL_UP), # +1
    Pin(2, Pin.IN, Pin.PULL_UP), # -1
    Pin(4, Pin.IN, Pin.PULL_UP), # +3
    Pin(5, Pin.IN, Pin.PULL_UP), # +2
    Pin(6, Pin.IN, Pin.PULL_UP)  # -1
]
reset_button = Pin(15, Pin.IN, Pin.PULL_UP)

#Track previous states for edge detection
prev_state = [True] * 5  # True is not pressed, False is pressed

#Score tracking
score = 0

def show_score():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("Score Counter")
    lcd.move_to(0, 1)
    lcd.putstr("Score: " + str(score))
    if score >= 4: #win condition
        lcd.clear()
        lcd.putstr("You Win!!!! The alligators die")

#Start program
show_score()

while True:
    i = 0
    while i < len(buttons):
        current = buttons[i].value() #HIGH is not pressed, LOW is pressed

        if reset_button.value() == 0: #button pressed (LOW)
            score = 0
            lcd.clear()
            lcd.putstr("Score Reset!")
            sleep(0.5)
            show_score()
            while reset_button.value() == 0: #wait for release to prevent multiple resets
                sleep(0.02)

        #Detect press event (transition from released -> pressed)
        if prev_state[i] and not current:
            if i in [1, 4]:    #pins 2, 6
                score -= 1
            elif i == 0:       #pin 3
                score += 1
            elif i == 3:       #pin 5
                score += 2
            elif i == 2:       #pin 4
                score += 3
            show_score()
            sleep(0.1)  #debounce delay

        prev_state[i] = current  #update previous state
        i += 1                   #move to next button

    sleep(0.02)  #loop delay
