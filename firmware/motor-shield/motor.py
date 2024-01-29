import machine

class Motor:
    """
    Driver DRV8838
    """
    def __init__(self, pwm_pin, ph_pin):
        """
        """
        self.pwm = machine.PWM(pwm_pin, freq=1000)
        self.ph = machine.Pin(ph_pin, machine.Pin.OUT)
        self.dir = 0
        self.moving = False
        self.actualSpeed = 0
        self.targetSpeed = 0
        self.isFading = False
        self.timer = 0
        self.startTimer = 0
        self.duration = 0
        self.amountFader = 77
        self.f = machine.Timer()

    def Percent(self, val):
        """
        Return the speed betwen 0 and 100 on 16bits definition
        """
        percent = (val*65536) /100
        return int(percent)

#========= TIMER =========
    # Timer are made to auto turn off the motors after n secondes
    # It corresponds to the payload in the time object inside the json sent by nodered (main.py l.73) 
    def resetTimer(self, now):
        """
        """
        print('timer reset')
        self.startTimer = now

    def updateTimer(self, now):
        """
        """
        elapse = now-self.startTimer
        self.timer=elapse

#========= MOVES =========
    def faderin(self, timer):
        """
        Fade in the speed of the motor
        smoother movements
        """
        if self.actualSpeed<self.Percent(self.targetSpeed) :
            self.actualSpeed = self.actualSpeed+self.amountFader
            self.pwm.duty_u16(self.actualSpeed)
            self.isFading = True
        else : 
            self.isFading = False
            self.f.deinit()
            print('faderIn done')
    def faderout(self, timer):
        """
        Fade out the speed of the motor
        smoother movements
        """
        if self.actualSpeed>self.Percent(self.targetSpeed) :
            self.actualSpeed = self.actualSpeed-self.amountFader
            if self.actualSpeed<0:
                self.actualSpeed = 0
            self.pwm.duty_u16(self.actualSpeed)
            self.isFading = True
        else :
            self.isFading = False
            self.moving = False
            self.f.deinit()
            print('faderOut done')

    def Turn(self, direction, speed, now):
        """
        """
        self.resetTimer(now)
        self.ph.value(direction)
        self.targetSpeed = speed

        if self.Percent(self.actualSpeed) != self.targetSpeed and not self.moving:
            self.moving = True
            self.f.init(period=5, mode=machine.Timer.PERIODIC, callback=self.faderin)

    def Stop(self):
        """
        """
        self.targetSpeed = 0
        if self.Percent(self.actualSpeed) != self.targetSpeed and self.moving:
            self.f.init(period=5, mode=machine.Timer.PERIODIC, callback=self.faderout)

    def brake(self):
        self.moving = False
        self.pwm.duty_u16(0)

#========= GETTERS =========
    def getSpeed(self):
        """
        Return actualSpeed in between 0 and 100
        """
        return self.Percent(self.actualSpeed)

    def getDir(self):
        """
        Return the actual direction
        0 → CW 
        1 → CCW
        """
        return self.ph.value()

#========= SETTERS =========    
    def setDuration(self, t):
        """
        """
        self.duration = t
        print(f'duration set to {t}')

    def setSpeed(self, sp):
        """
        """
        self.actualSpeed = sp
        self.pwm.duty_u16(self.actualSpeed)