"""STEP MOTOR 28BYJ-48 driver for Raspberry Pi

        Power----------------+
GPIOXX--------+              |
GPIOXX------+ |              |
GPIOXX----+ | |  +=========+ |
GPIOXX--+ | | +---IN1      | |
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

from __future__ import division, unicode_literals

__author__ = "Paweł Zacharek"
__copyright__ = "Copyright (C) 2015 Paweł Zacharek"
__date__ = "2015-09-24"
__name__ = "RPiStepMotor"
__license__ = "GPLv2+"
__version__ = "0.7.7"

import math
import RPi.GPIO as GPIO
import threading
import time
import warnings

GPIO.defaultMode = GPIO.BCM

allMotors = set()
allPins = set()
minimalStepDelay = 0.00195
phases = 4

class StepMotor(object):
	"""Class for manipulating stepper motors.
	
	Once a stepper motor object is created, it is possible to rotate and view
	the status of the corresponding phisical motor.
	"""
	
	def __init__(self, pins, fullRotation=512):
		"""Create an object of stepper motor.
		
		Keyword arguments:
		pins -- four-element integer tuple/list defining motor's connections
		fullRotation -- number of cycles needed to make a complete turn
		"""
		if len(pins) != phases:
			raise ValueError("step motor needs %d input pins" % phases)
		if [pin for pin in pins if pin in allPins]:
			raise ValueError("some pins are already in use")
		global allMotors, allPins
		allMotors.add(self)
		allPins.update(pins)
		self._fullRotation = fullRotation
		self._pins = tuple(pins)
		self._thread = threading.Thread()
		try:
			GPIO.setup(self._pins, GPIO.OUT, initial=False)
		except RuntimeError:
			warnings.warn("pin numbering mode wasn't set, using default settings", RuntimeWarning)
			self.setmode()
			GPIO.setup(self._pins, GPIO.OUT, initial=False)
	
	def __enter__(self):
		"""Enter the runtime context related to stepper motor object."""
		return self
	
	def __exit__(self, exc_type, exc_value, traceback):
		"""Exit the runtime context related to stepper motor object."""
		self.cleanup()
	
	def cleanup(self=None):
		"""Perform a cleanup of stepper motor object(s).
		
		Function waits till all threads end and frees related GPIO pins,
		so cleaned up objects cannot be used again.
		
		Keyword arguments:
		self -- if equals to 'None' cleanup includes every previously defined
				stepper motor object, otherwise perform cleanup of specified object
				or objects (if 'self' is a tuple, list or set)
		"""
		iterable = allMotors if self is None else self if type(self) in (tuple, list, set) else (self,)
		for motor in list(iterable):
			motor._delete()
	
	def finish(self):
		"""Wait till object's thread end."""
		if self.isRunning():
			self._thread.join()
	
	def isRunning(self):
		"""Return True or False, depending on the state of motor."""
		return self._thread.is_alive()
	
	def isStopped(self):
		"""Return True or False, depending on the state of motor."""
		return not self._thread.is_alive()
	
	def rotate(self, angle, timeForRevolution, function=None, nofork=False, radians=False):
		"""Rotate the step motor through an angle 'angle' in time 'timeForRevolution'.
		
		Keyword arguments:
		function -- three-element tuple containing function object (velocity
				function of time) and its first and last integer argument (used to
				create iterable - the more they differ, the more accurate is the
				result, but the time of single step is also shortened)
		nofork -- setting it can disable creating a new thread
		radians -- use radians instead of degrees
		"""
		if self.isRunning():
			raise RuntimeError("step motor already running")
		pins = self._pins[::-1] if angle < 0 else self._pins
		angle = math.degrees(abs(angle)) if radians else abs(angle)
		steps = int(angle / 360 * self._fullRotation)
		if nofork:
			self._fullCycle(pins, steps, timeForRevolution, function)
		else:
			self._thread = threading.Thread(target=self._fullCycle, args=(pins, steps, timeForRevolution, function))
			self._thread.start()
	
	@staticmethod
	def setmode(mode=GPIO.defaultMode):
		"""Set the pin numbering mode."""
		GPIO.setmode(mode)
	
	def _delete(self):
		"""Delete a single stepper motor object.
		
		It is always executed by cleanup().
		"""
		global allMotors, allPins
		if self.isRunning():
			self.finish()
		GPIO.cleanup(self._pins)
		allMotors.remove(self)
		allPins.difference_update(self._pins)
		del self._fullRotation
		del self._pins
		del self._thread
	
	def _fullCycle(self, pins, steps, timeForRevolution, function):
		"""Function does all the dirty work in the process of rotation stepper motor.
		
		It is always executed by rotate().
		"""
		if function is None:
			stepDelay = timeForRevolution / steps / phases
		else:
			func, start, end = function
			transition = -1 if start > end else 1
			iterable = range(start, end, transition)
			values = [func(i + 0.5 * transition) for i in iterable]
			oneStepValue = sum(values) / steps
			timePeriod = timeForRevolution / len(iterable)
			# create a list containing number of cycles for each time period
			cycles, remainder = [], 0
			for value in values:
				integer = value // oneStepValue
				remainder += value / oneStepValue - integer
				if round(remainder) >= 1:
					integer += 1
					remainder -= 1
				cycles.append(int(integer))
			# compute the least step delay
			stepDelay = timePeriod / max(cycles) / phases
		
		if stepDelay < minimalStepDelay:
			raise ValueError("step delay is too small")
		
		if function is None:
			for i in range(steps):
				for pin in pins:
					GPIO.output(pin, True)
					time.sleep(stepDelay)
					GPIO.output(pin, False)
		else:
			for repetitions in cycles:
				if repetitions == 0:
					time.sleep(timePeriod)
				else:
					stepDelay = timePeriod / repetitions / phases
					for i in range(repetitions):
						for pin in pins:
							GPIO.output(pin, True)
							time.sleep(stepDelay)
							GPIO.output(pin, False)
