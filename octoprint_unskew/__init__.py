# coding=utf-8
from __future__ import absolute_import

import re
import octoprint.plugin
import octoprint.filemanager
import octoprint.filemanager.util

class UnskewPlugin(octoprint.plugin.TemplatePlugin,
                   octoprint.plugin.SettingsPlugin):

	def get_settings_defaults(self):
		return dict(
			xyerr="0.0",
			yzerr="0.0",
			zxerr="0.0",
			callen="100.0"
		)

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_version(self):
		return self._plugin_version

	def unskew_coordinates(path, file_object, links=None, printer_profile=None, allow_overwrite=True, *args, **kwargs):

		if not octoprint.filemanager.valid_file_type(path, type="gcode"):
			return file_object

		xyerr = self._settings.get(["xyerr"])
		yzerr = self._settings.get(["yzerr"])
		zxerr = self._settings.get(["zxerr"])
		callen = self._settings.get(["callen"])

		if not xyerr == 0:
			xytan = xyerr/callen
		else:
			xytan = 0.0

		if not xytan == 0:
			self._logger.info("Unskew: The XY error is set to %s degrees" % xytan)

		if not yzerr == 0:
			yztan = yzerr/callen
		else:
			yztan = 0.0

		if not yztan == 0:
			self._logger.info("Unskew: The YZ error is set to %s degrees" % yztan)

		if not zxerr == 0:
			zxtan = zxerr/callen
		else:
			zxtan = 0.0

		if not zxtan == 0:
			self._logger.info("Unskew: The ZX error is set to %s degrees" % zxtan)

		xin = 0.0
		yin = 0.0
		zin = 0.0
		
		outfile = octoprint.filemanager.util.AbstractFileWrapper(file_object.filename)

		for line in file_object:
			# Check that the current 'line' is a move, if so the line is processed
			gmatch = re.match(r'G[0-1]',line,re.I)
			if gmatch:

				# load the incoming X coordinate into a variable. Previous value will be used if new value is not found.
				xsrch = re.search(r'[xX]\d*\.*\d*',line,re.I)
				if xsrch: # if an X value is found
						xin = float(re.sub(r'[xX]','',xsrch.group())) # Strip the letter from the coordinate.

				# load the incoming Y coordinate into a variable. Previous value will be used if new value is not found.
				ysrch = re.search(r'[yY]\d*\.*\d*', line, re.I)
				if ysrch:
						yin = float(re.sub(r'[yY]','',ysrch.group())) # Strip the letter from the coordinate.

				# load the incoming Z coordinate into a variable. Previous value will be used if new value is not found.
				zsrch = re.search(r'[zZ]\d*\.*\d*', line, re.I)
				if zsrch:
						zin = float(re.sub(r'[zZ]','',zsrch.group())) # Strip the letter from the coordinate.

				# calculate the corrected/skewed XYZ coordinates
				xout = round(xin-yin*xytan,3)
				yout = round(yin-zin*yztan,3)
				xout = round(xout-zin*zxtan,3)
				zout = zin # Z coodinates must remain the same to prevent layers being tilted!

				lineout = line
				if xsrch:
						lineout = re.sub(r'[xX]\d*\.*\d*', 'X' + str(xout), cmd)

				if ysrch:
						lineout = re.sub(r'[yY]\d*\.*\d*', 'Y' + str(yout), cmd)

				if zsrch:
						lineout = re.sub(r'[zZ]\d*\.*\d*', 'Z' + str(zout), cmd)

				outfile.write(lineout)
			else:
				outfile.write(line)

		return outfile

__plugin_name__ = "Unskew"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = UnskewPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
    "octoprint.filemanager.preprocessor": __plugin_implementation__.unskew_coordinates
	}
