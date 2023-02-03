class Impossible(Exception):
	""" Exception raised when an action is impossible to be performed.
	The reason is given as the exception message.
	"""
	
class QuitWithoutSaving(SystemExit):
	""" Can be raised to exit hte game without automatically saving. """
	
