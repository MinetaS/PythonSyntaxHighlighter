from ColorizeCode import *
from ParseCode import *

from configuration import config

import argparse
import hashlib
import json
import keyword
import sys


class OptionError(Exception) :
	def __init__(self, msg) :
		super().__init__(msg)


def ParseArguments(obj:Colorize) -> tuple :
	parser = argparse.ArgumentParser(prog='PythonSyntaxHighlighter', description='Highlight python code in HTML.')
	parser.add_argument('file', help='Specify a file.')
	parser.add_argument('-s', '--style', help='load and apply a style theme to the code', metavar='style')
	parser.add_argument('-l', '--linestart', default=1, type=int, help='disable line numbering feature', metavar='line_start')
	parser.add_argument('--nolinenumber', action='store_true', help='disable line numbering feature')
	parser.add_argument('--debug', action='store_true', help='print all tokens')
	args = parser.parse_args()

	# load code text
	try :
		with open(args.file, 'r') as f :
			content = f.read()
			obj.SetContent(content)
			h = hashlib.md5(content.encode()).hexdigest()
	except FileNotFoundError :
		print("Error: File {} doesn't exist.".format(args.file))
		exit()

	# load theme
	if args.style :
		try :
			obj.SetTheme(args.style)
		except FileNotFoundError :
			print("Error: Theme {0} doesn't exist. (./themes/{0}.json)".format(args.style))
			exit()

	# line number base
	if args.linestart :
		obj.SetLineNumber(args.linestart)

		if args.nolinenumber :
			print('Warning: Option --nolinenumber is enabled. This option will be ignored in result.')

	# no line numbering
	if args.nolinenumber :
		obj.DisableLineNumber()

	# debug option
	if args.debug :
		config.env.debug = True

	return h


if __name__ == '__main__' :
	obj = Colorize()
	h = ParseArguments(obj)

	with open('result_{0}.html'.format(h), 'w') as f :
		f.write(obj.toHTML())