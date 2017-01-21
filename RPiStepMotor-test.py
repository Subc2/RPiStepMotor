#!/usr/bin/python3

"""RPiStepMotor-test - tests RPiStepMotor module

        Power----------------+
GPIO6---------+              |
GPIO13------+ |              |
GPIO19----+ | |  +=========+ |
GPIO26--+ | | +---IN1      | |
Ground  | | +-----IN2      | |
   |    | +-------IN3      | |
   |    +---------IN4      | |
   |             |         | |
   |             | ULN2003 | |
   |             |         | |
   |             |Ground   | |
   |             |  | Power| |
   |             +==|===|==+ |
   |                |   |    |
   +----------------+   +----+
"""

__author__ = "Paweł Zacharek"
__copyright__ = "Copyright (C) 2015 Paweł Zacharek"
__date__ = "2015-09-24"
__license__ = "GPLv2+"
__version__ = "1.0.0"

from RPiStepMotor import StepMotor
import time

StepMotor.setmode()

with StepMotor((6, 13, 19, 26)) as motor:
	motor.rotate(180, 20, (lambda x: x, 0, 100), nofork=True)
	time.sleep(5)
	motor.rotate(-180, 10)
