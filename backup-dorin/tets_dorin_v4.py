from MotorDriver import MotorDriver
from Entity import Trailer1, Trailer2, Trailer3, Trailer4, Trailer5

# trailer1 = Trailer1(I2CAddress = 0x11)
# MotorDriver.MotorRun(trailer1.driver1, speed=30) # V
# MotorDriver.stopMotor(trailer1.driver1)
# MotorDriver.MotorRun(trailer1.turn1, 10) # V
# MotorDriver.stopMotor(trailer1.turn1)
# MotorDriver.MotorRun(trailer1.pump1, 90) # V
# MotorDriver.stopMotor(trailer1.pump1)

# trailer2 = Trailer2(I2CAddress = 0x12)
# MotorDriver.MotorRun(trailer2.e1, speed=90) # does noise but pwm not strong enough to move
# MotorDriver.stopMotor(trailer2.e1)
# MotorDriver.MotorRun(trailer2.e2, speed=90) # not moving
# MotorDriver.stopMotor(trailer2.e2)

# trailer3 = Trailer3(I2CAddress = 0x13)
# MotorDriver.MotorRun(trailer3.t2, speed=90) # not strong enough to move
# MotorDriver.stopMotor(trailer3.t2)
# MotorDriver.MotorRun(trailer3.t3, speed=90) # not strong enough to move
# MotorDriver.stopMotor(trailer3.t3)

# trailer4 = Trailer4(I2CAddress = 0x14)
# MotorDriver.MotorRun(trailer4.e3, speed=90) # not strong enogh to move
# MotorDriver.stopMotor(trailer4.e3)
# MotorDriver.MotorRun(trailer4.e4, speed=90) # not strong enough to move 
# MotorDriver.stopMotor(trailer4.e4)

trailer5 = Trailer5(I2CAddress = 0x15)
# print("trailer5")
# MotorDriver.MotorRun(trailer5.d2, speed=90) # not moving
# MotorDriver.stopMotor(trailer5.d2) # didnt stop
# MotorDriver.MotorRun(trailer5.t4, 90) 
# MotorDriver.stopMotor(trailer5.t4)
# MotorDriver.MotorRun(trailer5.p2, 90)
# MotorDriver.stopMotor(trailer5.p2)

# MotorDriver.StopAllMotors()