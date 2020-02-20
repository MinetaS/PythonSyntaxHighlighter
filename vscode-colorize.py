from io import BytesIO
from tokenize import *
import hashlib
import json
import keyword
import sys

class Colorize_Theme :
	def __init__(self, name) :
		self.__Name = name
		self.__Load('./themes/{0}.json'.format(name))

	def __Load(self, filename) :
		with open(filename, 'r') as f :
			data = json.load(f)

		self.Comment   = data['comment']
		self.Control   = data['control']
		self.Keyword   = data['keyword']
		self.ClassName = data['classname']
		self.FuncName  = data['funcname']
		self.Argument  = data['argument']
		self.String    = data['string']
		self.Number    = data['number']

class Colorize :
	def __init__(self) :
		self.__Theme = 'dark_default'
		self.__LineNumber = True
		self.__Content = ''

		self.ThemeObject = Colorize_Theme(self.__Theme)

		# Color: 1=argument, 2=classname, 3=funcname, 4=keyword
		self.__builtins__color_1 = ['__builtins__', '__name__', '__doc__', '__package__', '__spec__', '__debug__']
		self.__builtins__color_2 = ['bool', 'bytearray', 'bytes', 'classmethod', 'complex', 'dict', 'float', 'frozenset', 'property', 'int', 'list', 'object', 'set', 'slice', 'staticmethod', 'str', 'super', 'tuple', 'type', 'BaseException', 'Exception', 'TypeError', 'StopAsyncIteration', 'StopIteration', 'GeneratorExit', 'SystemExit', 'KeyboardInterrupt', 'ImportError', 'ModuleNotFoundError', 'OSError', 'EnvironmentError', 'IOError', 'EOFError', 'RuntimeError', 'RecursionError', 'NotImplementedError', 'NameError', 'UnboundLocalError', 'AttributeError', 'SyntaxError', 'IndentationError', 'TabError', 'LookupError', 'IndexError', 'KeyError', 'ValueError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError', 'UnicodeTranslateError', 'AssertionError', 'ArithmeticError', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemError', 'ReferenceError', 'MemoryError', 'BufferError', 'Warning', 'UserWarning', 'DeprecationWarning', 'PendingDeprecationWarning', 'SyntaxWarning', 'RuntimeWarning', 'FutureWarning', 'ImportWarning', 'UnicodeWarning', 'BytesWarning', 'ResourceWarning', 'ConnectionError', 'BlockingIOError', 'BrokenPipeError', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError', 'IsADirectoryError', 'NotADirectoryError', 'InterruptedError', 'PermissionError', 'ProcessLookupError', 'TimeoutError']
		self.__builtins__color_3 = ['__import__', 'abs', 'all', 'any', 'ascii', 'bin', 'breakpoint', 'callable', 'chr', 'compile', 'delattr', 'dir', 'divmod', 'eval', 'exec', 'format', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 'input', 'isinstance', 'issubclass', 'iter', 'len', 'locals', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'print', 'repr', 'round', 'setattr', 'sorted', 'sum', 'vars', 'memoryview', 'enumerate', 'filter', 'map', 'range', 'reversed', 'zip', 'open', 'quit', 'exit', 'copyright', 'credits', 'license', 'help', '_']
		self.__builtins__color_4 = ['None', 'Ellipsis', 'NotImplemented', 'False', 'True', 'self']

		# Control statements
		self.__controls = ['as', 'assert', 'break', 'continue', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'if', 'import', 'nonlocal', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']

	def SetTheme(self, theme) :
		self.__Theme = theme
		self.ThemeObject = Colorize_Theme(theme)
	
	def SetContent(self, content) :
		self.__Content = content

	def EnableLineNumber(self) :
		self.__LineNumber = True

	def DisableLineNumber(self) :
		self.__LineNumber = False

	def toHTML(self) :
		lines = self.__Content.replace('\r', '').split('\n')

		HTML = ''
		HTML += '<div class="vscode-colorize" style="width:100%; position:relative !important; overflow:auto; color:#D4D4D4; font-size:14px; font-family:Consolas, \'Liberation Mono\', Menlo, Courier, monospace !important;">\n'
		HTML += '<table class="vscode-colorize" style="width:100%; margin:0; padding:0; border:none; border-radius:4px; background-color:#1E1E1E;" cellspacing="0" cellpadding="0">\n'
		HTML += '<tr>\n'

		if self.__LineNumber :
			HTML += '<td style="width:{0}px; padding:6px; padding-left:14px; padding-right:14px;">\n'.format(len(str(len(lines)))*7+6)
			HTML += '<div style="margin:0; padding:0; word-break:normal; text-align:right; line-height:130%; color:#999999;">\n'

			for i in range(len(lines)) :
				HTML += '{0}<br />\n'.format(i+1)

			HTML += '</div>\n'
			HTML += '</td>\n'

		HTML += '<td style="padding:6px; padding-left: 6px; text-align:left;">\n'
		HTML += '<div style="margin:0; padding:0; line-height:130%; white-space:pre; color:#D4D4D4;">'

		tokens = tokenize(BytesIO(self.__Content.encode('UTF-8')).readline)

		last_pos = (0, 0)

		is_func_begin = False
		is_func_args = False
		is_classname = False
		is_funcname = False
		check_bracket = 0

		for token in tokens :
			#print(token)
			if token.start[0] <= len(lines) :
				if token.start[0] == last_pos[0] : HTML += lines[last_pos[0]-1][last_pos[1]:token.start[1]].replace('\t', '    ')
				elif token.start[0] > 1 : HTML += lines[last_pos[0]-1][last_pos[1]:].replace('\t', '    ')+lines[token.start[0]-1][:token.start[1]].replace('\t', '    ')

			last_pos = token.end

			if token.type == NEWLINE or token.type == NL :
				HTML += token.string

			if token.type == INDENT :
				HTML += token.string.replace('\t', '    ')

			if token.type == OP :
				HTML += token.string

				if is_func_begin and is_func_args and token.string == '(' :
					check_bracket += 1
				elif is_func_begin and token.string == '(' :
					is_func_args = True

				if is_func_begin and is_func_args and token.string == ')' :
					if check_bracket == 0 :
						is_func_begin = False
						is_func_args = False
					else :
						check_bracket -= 1

			if token.type == NUMBER :
				t = '<span style="color:{0};">'.format(self.ThemeObject.Number['color'])+token.string+'</span>'
				if self.ThemeObject.Number['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
				if self.ThemeObject.Number['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
				if self.ThemeObject.Number['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
				HTML += t

			if token.type == COMMENT :
				t = '<span style="color:{0};">'.format(self.ThemeObject.Comment['color'])+token.string+'</span>'
				if self.ThemeObject.Comment['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
				if self.ThemeObject.Comment['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
				if self.ThemeObject.Comment['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
				HTML += t

			if token.type == STRING :
				t = '<span style="color:{0};">'.format(self.ThemeObject.String['color'])+token.string+'</span>'
				if self.ThemeObject.String['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
				if self.ThemeObject.String['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
				if self.ThemeObject.String['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
				HTML += t

			if token.type == NAME :
				if (is_func_begin and is_func_args) or token.string in self.__builtins__color_1 :
					t = '<span style="color:{0};">'.format(self.ThemeObject.Argument['color'])+token.string+'</span>'
					if self.ThemeObject.Argument['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
					if self.ThemeObject.Argument['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
					if self.ThemeObject.Argument['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
					HTML += t

				elif keyword.iskeyword(token.string) and token.string in self.__controls :
					t = '<span style="color:{0};">'.format(self.ThemeObject.Control['color'])+token.string+'</span>'
					if self.ThemeObject.Control['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
					if self.ThemeObject.Control['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
					if self.ThemeObject.Control['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
					HTML += t

				elif keyword.iskeyword(token.string) or token.string in self.__builtins__color_4 :
					t = '<span style="color:{0};">'.format(self.ThemeObject.Keyword['color'])+token.string+'</span>'
					if self.ThemeObject.Keyword['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
					if self.ThemeObject.Keyword['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
					if self.ThemeObject.Keyword['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
					HTML += t
					
					if token.string == 'class' : is_classname = True
					if token.string == 'def' :
						is_func_begin = True
						is_funcname = True

				elif is_classname or token.string in self.__builtins__color_2 :
					t = '<span style="color:{0};">'.format(self.ThemeObject.ClassName['color'])+token.string+'</span>'
					if self.ThemeObject.ClassName['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
					if self.ThemeObject.ClassName['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
					if self.ThemeObject.ClassName['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
					HTML += t

					if is_classname : is_classname = False

				elif is_funcname or token.string in self.__builtins__color_3 :
					t = '<span style="color:{0};">'.format(self.ThemeObject.FuncName['color'])+token.string+'</span>'
					if self.ThemeObject.FuncName['strike'].lower() == 'true' : t = '<s>{0}</s>'.format(t)
					if self.ThemeObject.FuncName['italic'].lower() == 'true' : t = '<i>{0}</i>'.format(t)
					if self.ThemeObject.FuncName['bold'].lower() == 'true' : t = '<b>{0}</b>'.format(t)
					HTML += t

					if is_funcname : is_funcname = False

				else :
					HTML += token.string

		#HTML = HTML.rstrip()
		HTML += '</div>\n'
		HTML += '</td>\n'
		HTML += '</tr>\n'
		HTML += '</table>\n'
		HTML += '</div>'

		return HTML

class OptionError(Exception) :
	def __init__(self, msg) :
		super().__init__(msg)

def ParseArguments(obj:Colorize) -> tuple :
	if len(sys.argv) == 1 :
		print('Usage: {0} [filename] (options)'.format(sys.argv[0]))
		return None

	with open(sys.argv[1], 'r') as f :
		content = f.read()
		h = hashlib.md5(content.encode()).hexdigest()

	obj.SetContent(content)

	args = sys.argv[2:]

	for arg_index in range(len(args)) :
		arg = args[arg_index]
		val = None
		t = arg.find('=')

		if t != -1 :
			val = arg[t+1:]
			arg = arg[:t]

		if arg == '--nolinenumber' :
			obj.DisableLineNumber()
			continue

		if arg == '--style' :
			if val == None :
				raise OptionError('The value of \'style\' argument isn\'t specified')

			obj.SetTheme(val)
			continue

		raise OptionError('Unknown argument \'{0}\''.format(arg))

	return sys.argv[1], h

if __name__ == '__main__' :
	obj = Colorize()
	filename, h = ParseArguments(obj)
	a = {}

	with open('result_{0}.html'.format(h), 'w') as f :
		f.write(obj.toHTML())