# coding=utf-8
from __future__ import absolute_import

import re
import octoprint.plugin
import octoprint.filemanager
import octoprint.filemanager.util

class Unskew(octoprint.filemanager.util.LineProcessorStream):

	def __init__(self):
		self.xyerr = 1.0
		self.yzerr = 0.0
		self.zxerr = 0.0
		self.callen = 100.0
		self.xin = 0.0
		self.yin = 0.0
		self.zin = 0.0

		if not self.xyerr == 0:
			self.xytan = self.xyerr/callen
		else:
			self.xytan = 0.0

		if not self.yzerr == 0:
			self.yztan = self.yzerr/self.callen
		else:
			self.yztan = 0.0

		if not self.zxerr == 0:
			self.zxtan = self.zxerr/self.callen
		else:
			self.zxtan = 0.0
			
		self.xin = 0.0
		self.yin = 0.0
		self.zin = 0.0

	def process_line(self, line):
		gmatch = re.match(r'G[0-1]',line,re.I)
		if gmatch:

			# load the incoming X coordinate into a variable. Previous value will be used if new value is not found.
			xsrch = re.search(r'[xX]\d*\.*\d*',line,re.I)
			if xsrch: # if an X value is found
					self.xin = float(re.sub(r'[xX]','',xsrch.group())) # Strip the letter from the coordinate.

			# load the incoming Y coordinate into a variable. Previous value will be used if new value is not found.
			ysrch = re.search(r'[yY]\d*\.*\d*', line, re.I)
			if ysrch:
					self.yin = float(re.sub(r'[yY]','',ysrch.group())) # Strip the letter from the coordinate.

			# load the incoming Z coordinate into a variable. Previous value will be used if new value is not found.
			zsrch = re.search(r'[zZ]\d*\.*\d*', line, re.I)
			if zsrch:
					self.zin = float(re.sub(r'[zZ]','',zsrch.group())) # Strip the letter from the coordinate.

			# calculate the corrected/skewed XYZ coordinates
			xout = round(xin-yin*xytan,3)
			yout = round(yin-zin*yztan,3)
			xout = round(xout-zin*zxtan,3)
			zout = zin # Z coodinates must remain the same to prevent layers being tilted!

			lineout = line
			if xsrch:
					lineout = re.sub(r'[xX]\d*\.*\d*', 'X' + str(xout), lineout)

			if ysrch:
					lineout = re.sub(r'[yY]\d*\.*\d*', 'Y' + str(yout), lineout)

			if zsrch:
					lineout = re.sub(r'[zZ]\d*\.*\d*', 'Z' + str(zout), lineout)

			return lineout
		else:
			return line

def unskew_gcode(path, file_object, links=None, printer_profile=None, allow_overwrite=True, *args, **kwargs):
	if not octoprint.filemanager.valid_file_type(path, type="gcode"):
		return file_object

	import os
	name, _ = os.path.splitext(file_object.filename)
	if not name.endswith("_unskew"):
		return file_object

	return octoprint.filemanager.util.StreamWrapper(file_object.filename, Unskew(file_object.stream()))

__plugin_name__ = "Unskew"
__plugin_hooks__ = {
	"octoprint.filemanager.preprocessor": unskew_gcode
}