from configuration import config

from tokenize import *
from typing import *
from io import BytesIO
import keyword
import re


class ETokenType :
	TEXT              = 0
	OPERATOR          = 1
	CONTROL_STATEMENT = 2
	KEYWORD           = 3
	CLASS             = 4
	CLASS_NAME        = 5
	CLASS_PARENT      = 6
	FUNCTION          = 7
	FUNCTION_NAME     = 8
	FUNCTION_ARG      = 9
	FUNCTION_ARGTYPE  = 10
	FUNCTION_ARGNAME  = 11
	TYPENAME          = 12
	METHOD            = 13
	MEMBER_VAR        = 14
	STRING            = 15
	NUMBER            = 16
	COMMENT           = 17
	NEWLINE           = 18
	BULITIN_STRING    = 101
	BUILTIN_FUNCTION  = 102
	OTHERS            = 257

	@staticmethod
	def to_name(token_type) :
		temp_hash = {
			0 : 'TEXT',
			1 : 'OPERATOR',
			2 : 'CONTROL_STATEMENT',
			3 : 'KEYWORD',
			4 : 'CLASS',
			5 : 'CLASS_NAME',
			6 : 'CLASS_PARENT',
			7 : 'FUNCTION',
			8 : 'FUNCTION_NAME',
			9 : 'FUNCTION_ARG',
			10 : 'FUNCTION_ARGTYPE',
			11 : 'FUNCTION_ARGNAME',
			12 : 'TYPENAME',
			13 : 'METHOD',
			14 : 'MEMBER_VAR',
			15 : 'STRING',
			16 : 'NUMBER',
			17 : 'COMMENT',
			18 : 'NEWLINE',
			101 : 'BULITIN_STRING',
			102 : 'BUILTIN_FUNCTION',
			257 : 'OTHERS'
		}

		return temp_hash[token_type]


class ETokenInfo :
	previous = ETokenType.TEXT

	def __init__(self, token:TokenInfo, token_type:int) :
		self.token = token
		self.type = token_type
		self.attr = {}

	def __str__(self) :
		return "ETokenInfo (type={} ({}), string={}, start={}, end={}, attributes={})".format(self.type, ETokenType.to_name(self.type), self.token.string.__repr__(), self.token.start, self.token.end, self.attr.__repr__())

	def SetAttribute(self, attr, value) :
		self.attr[attr] = value

	def GetAttribute(self, attr) :
		try :
			return self.attr[attr]
		except :
			return None


def parse(code:str) -> List[ETokenInfo] :
	tokens = __update_init(code)
	__update_Keyword(tokens)
	__update_FunctionName(tokens)
	__update_ClassName(tokens)
	__update_FunctionArgs(tokens)
	__update_ClassInheritance(tokens)
	__update_Literals(tokens)

	if config.env.debug :
		for t in tokens :
			print(t, t.token.type)

	return tokens


def __update_init(content:str) -> List[ETokenInfo] :
	content = content.replace('\r', '').replace('\t', '    ')
	tokens = tokenize(BytesIO(content.encode('UTF-8')).readline)
	etokens = []

	lines = ['']
	lines += content.split('\n')
	last_pos = (1, 0)

	for token in tokens :
		if token.type == ENCODING :
			continue

		if type(token) != TokenInfo :
			raise TypeError(type(token))

		if token.start != last_pos :
			if last_pos[0] == token.start[0] :
				t = TokenInfo(ETokenType.OTHERS, lines[last_pos[0]][last_pos[1]:token.start[1]], (last_pos[0], last_pos[1]), (last_pos[0], token.start[1]), lines[last_pos[0]])
				etokens.append(ETokenInfo(t, ETokenType.OTHERS))

			else :
				raise Exception('Exception occured')
				
				'''
				t = TokenInfo(ETokenType.OTHERS, lines[last_pos[0]][last_pos[1]+1:], (last_pos[0], last_pos[1]+1), (last_pos[0], len(line[last_pos[0]])), last_pos[0])
				etokens.append(ETokenInfo(t, ETokenType.OTHERS))

				for l in range(last_pos[0]+1, token.start[0]) :
					t = TokenInfo(ETokenType.OTHERS, lines[l], (l, 0), (l, len(line[l])), l)
					etokens.append(ETokenInfo(t, ETokenType.OTHERS))
				
				t = TokenInfo(ETokenType.OTHERS, lines[last_pos[0]][last_pos[1]+1:], (last_pos[0], last_pos[1]+1), (last_pos[0], len(line[last_pos[0]])), last_pos[0])
				etokens.append(ETokenInfo(t, ETokenType.OTHERS))
				'''

		if token.type == OP : etokens.append(ETokenInfo(token, ETokenType.OPERATOR))
		if token.type == STRING : etokens.append(ETokenInfo(token, ETokenType.STRING))
		if token.type == NUMBER : etokens.append(ETokenInfo(token, ETokenType.NUMBER))
		if token.type == COMMENT : etokens.append(ETokenInfo(token, ETokenType.COMMENT))
		if token.type == NAME : etokens.append(ETokenInfo(token, ETokenType.TEXT))
		if token.type == INDENT : etokens.append(ETokenInfo(token, ETokenType.STRING))
		if token.type == NEWLINE or token.type == NL :
			etokens.append(ETokenInfo(token, ETokenType.NEWLINE))
			last_pos = (token.end[0]+1, 0)
		else :
			last_pos = token.end
	return etokens


def __update_Keyword(tokens:List[ETokenInfo]) :
	__controls = ['as', 'assert', 'break', 'continue', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'if', 'import', 'nonlocal', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
	__builtins__names = ['__builtins__', '__name__', '__doc__', '__package__', '__spec__', '__debug__', '__all__']
	__builtins__types = ['bool', 'bytearray', 'bytes', 'classmethod', 'complex', 'dict', 'float', 'frozenset', 'property', 'int', 'list', 'object', 'set', 'slice', 'staticmethod', 'str', 'super', 'tuple', 'type', 'BaseException', 'Exception', 'TypeError', 'StopAsyncIteration', 'StopIteration', 'GeneratorExit', 'SystemExit', 'KeyboardInterrupt', 'ImportError', 'ModuleNotFoundError', 'OSError', 'EnvironmentError', 'IOError', 'EOFError', 'RuntimeError', 'RecursionError', 'NotImplementedError', 'NameError', 'UnboundLocalError', 'AttributeError', 'SyntaxError', 'IndentationError', 'TabError', 'LookupError', 'IndexError', 'KeyError', 'ValueError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError', 'UnicodeTranslateError', 'AssertionError', 'ArithmeticError', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemError', 'ReferenceError', 'MemoryError', 'BufferError', 'Warning', 'UserWarning', 'DeprecationWarning', 'PendingDeprecationWarning', 'SyntaxWarning', 'RuntimeWarning', 'FutureWarning', 'ImportWarning', 'UnicodeWarning', 'BytesWarning', 'ResourceWarning', 'ConnectionError', 'BlockingIOError', 'BrokenPipeError', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError', 'IsADirectoryError', 'NotADirectoryError', 'InterruptedError', 'PermissionError', 'ProcessLookupError', 'TimeoutError']
	__builtins__functions = ['__import__', 'abs', 'all', 'any', 'ascii', 'bin', 'breakpoint', 'callable', 'chr', 'compile', 'delattr', 'dir', 'divmod', 'eval', 'exec', 'format', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id', 'input', 'isinstance', 'issubclass', 'iter', 'len', 'locals', 'max', 'min', 'next', 'oct', 'ord', 'pow', 'print', 'repr', 'round', 'setattr', 'sorted', 'sum', 'vars', 'memoryview', 'enumerate', 'filter', 'map', 'range', 'reversed', 'zip', 'open', 'quit', 'exit', 'copyright', 'credits', 'license', 'help']
	__builtins__keywords = ['None', 'Ellipsis', 'NotImplemented', 'False', 'True', 'self', 'and', 'or', 'in', 'def', 'class']

	for token in tokens :
		if token.type == ETokenType.TEXT :
			if token.token.string in __controls :
				token.type = ETokenType.CONTROL_STATEMENT
			elif token.token.string in __builtins__names :
				token.type = ETokenType.BULITIN_STRING
			elif token.token.string in __builtins__types :
				token.type = ETokenType.TYPENAME
			elif token.token.string in __builtins__functions :
				token.type = ETokenType.BUILTIN_FUNCTION
			elif token.token.string in __builtins__keywords :
				token.type = ETokenType.KEYWORD


def __update_FunctionName(tokens:List[ETokenInfo]) :
	previous_type = -1

	for token in tokens :
		if token.type == ETokenType.OTHERS :
			continue

		if token.token.string == 'def' :
			token.type = ETokenType.FUNCTION

		if previous_type == ETokenType.FUNCTION :
			token.type = ETokenType.FUNCTION_NAME

		if token.type != ETokenType.OTHERS :
			previous_type = token.type


def __update_ClassName(tokens:List[ETokenInfo]) :
	previous_type = -1

	for token in tokens :
		if token.type == ETokenType.OTHERS :
			continue

		if token.token.string == 'class' :
			token.type = ETokenType.CLASS

		if previous_type == ETokenType.CLASS :
			token.type = ETokenType.CLASS_NAME

		if token.type != ETokenType.OTHERS :
			previous_type = token.type


def __update_FunctionArgs(tokens:List[ETokenInfo]) :
	__builtins__types = ['bool', 'bytearray', 'bytes', 'classmethod', 'complex', 'dict', 'float', 'frozenset', 'property', 'int', 'list', 'object', 'set', 'slice', 'staticmethod', 'str', 'super', 'tuple', 'type', 'BaseException', 'Exception', 'TypeError', 'StopAsyncIteration', 'StopIteration', 'GeneratorExit', 'SystemExit', 'KeyboardInterrupt', 'ImportError', 'ModuleNotFoundError', 'OSError', 'EnvironmentError', 'IOError', 'EOFError', 'RuntimeError', 'RecursionError', 'NotImplementedError', 'NameError', 'UnboundLocalError', 'AttributeError', 'SyntaxError', 'IndentationError', 'TabError', 'LookupError', 'IndexError', 'KeyError', 'ValueError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError', 'UnicodeTranslateError', 'AssertionError', 'ArithmeticError', 'FloatingPointError', 'OverflowError', 'ZeroDivisionError', 'SystemError', 'ReferenceError', 'MemoryError', 'BufferError', 'Warning', 'UserWarning', 'DeprecationWarning', 'PendingDeprecationWarning', 'SyntaxWarning', 'RuntimeWarning', 'FutureWarning', 'ImportWarning', 'UnicodeWarning', 'BytesWarning', 'ResourceWarning', 'ConnectionError', 'BlockingIOError', 'BrokenPipeError', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionRefusedError', 'ConnectionResetError', 'FileExistsError', 'FileNotFoundError', 'IsADirectoryError', 'NotADirectoryError', 'InterruptedError', 'PermissionError', 'ProcessLookupError', 'TimeoutError']

	function_begin = False
	function_pt_begin = False
	function_pt_depth = 0
	is_argtype = False
	is_restype = False

	pt_depth = 0

	for i in range(len(tokens)) :
		token = tokens[i]

		if token.type == ETokenType.OTHERS :
			continue

		if token.token.type == NEWLINE :
			function_begin = False
			continue

		if token.type == ETokenType.FUNCTION :
			function_begin = True
			continue

		# parse function definition line
		if token.type == ETokenType.OPERATOR and token.token.string == '->' :
			is_restype = True
			continue

		if is_restype :
			is_restype = False
			if token.token.string in __builtins__types :
					token.type = ETokenType.FUNCTION_ARGTYPE

		if function_begin :
			if token.type == ETokenType.OPERATOR and token.token.string == '(' :
				if not function_pt_begin :
					function_pt_begin = True
				else :
					function_pt_depth += 1
				continue

			if token.type == ETokenType.OPERATOR and token.token.string == ')' :
				if function_pt_depth == 0 :
					function_pt_begin = False
				else :
					function_pt_depth -= 1
				continue

			if function_pt_begin :
				if is_argtype :
					is_argtype = False
					if token.token.string in __builtins__types :
						token.type = ETokenType.FUNCTION_ARGTYPE
				elif function_pt_depth == 0 and token.type == ETokenType.TEXT :
					token.type = ETokenType.FUNCTION_ARG
				if function_pt_depth == 0 and token.token.string == ':' :
					is_argtype = True

		# parse function usage line
		if not function_begin :
			if token.type == ETokenType.OPERATOR and token.token.string == '(' :
				pt_depth += 1
				continue

			if token.type == ETokenType.OPERATOR and token.token.string == ')' :
				pt_depth -= 1
				continue

			if pt_depth > 0 :
				is_argname = False

				for t in tokens[i+1:] :
					if t.type == ETokenType.OTHERS :
						continue
					if t.type == ETokenType.OPERATOR and t.token.string == '=' :
						is_argname = True
						break
					break

				if is_argname :
					token.type = ETokenType.FUNCTION_ARGNAME


def __update_ClassInheritance(tokens:List[ETokenInfo]) :
	class_begin = False
	class_pt_begin = False
	class_pt_depth = 0

	for token in tokens :
		if token.type == ETokenType.OTHERS :
			continue

		if token.token.type == NEWLINE :
			function_begin = False
			continue

		if token.type == ETokenType.CLASS :
			class_begin = True

		if class_begin :
			if token.type == ETokenType.OPERATOR and token.token.string == '(' :
				if not class_pt_begin :
					class_pt_begin = True
				else :
					class_pt_depth += 1
				continue

			if token.type == ETokenType.OPERATOR and token.token.string == ')' :
				if class_pt_depth == 0 :
					class_pt_begin = False
				else :
					class_pt_depth -= 1
				continue

			if class_pt_begin and class_pt_depth == 0 and token.type == ETokenType.TEXT :
				token.type = ETokenType.CLASS_PARENT


def __int_find_escseq(string:str) -> List[Tuple[int, int, str]] :
	result = []
	table = [r'\\\\', r"\\'", r'\\"', r'\\a', r'\\b', r'\\f', r'\\n', r'\\r', r'\\t', r'\\v', r'\\[0-8]{3}', r'\\x[A-Fa-f0-9]{2}', r'\\N\{[A-Za-z0-9_]+\}', r'\\u[A-Fa-f0-9]{4}', r'\\U[A-Fa-f0-9]{8}']
	names = ['backslash', 'single_quote', 'double_quote', 'bell', 'backspace', 'formfeed', 'linefeed', 'carriage_return', 'horizontal_tab', 'vertical_tab', 'octal_char', 'hex_char', 'named_unicode', '16bit_char', '32bit_char']

	length = len(string)
	pos = 0

	while pos < length :
		f = None

		for i in range(len(table)) :
			entry = table[i]
			pattern = re.compile(entry)
			f = pattern.match(string[pos:])

			if f :
				interval = f.span()
				result.append((interval[0]+pos, interval[1]+pos, names[i]))
				pos += interval[1]
				break

		if not f :
			pos += 1

	return result


def __int_find_brackets(string:str) -> List[Tuple[int, int]] :
	result = []

	length = len(string)
	pos = 0

	# stop scanning when an invalid bracket is found
	while pos < length :
		pattern = re.compile(r'{[A-Za-z0-9_]*}')
		pattern_inv = re.compile(r'{.*}')
		f = pattern.match(string[pos:])
		f_inv = pattern_inv.match(string[pos:])

		if f :
			interval = f.span()
			result.append((interval[0]+pos, interval[1]+pos))
			pos += interval[1]
		elif not f and f_inv :
			break
		else :
			pos += 1

	return result


def __update_Literals(tokens:List[ETokenInfo]) :
	for token in tokens :
		if token.type == ETokenType.NUMBER :
			if token.token.string.startswith('0x') : token.SetAttribute('nType', ('hex', '0x'))
			if token.token.string.startswith('0o') : token.SetAttribute('nType', ('oct', '0o'))
			if token.token.string.startswith('0b') : token.SetAttribute('nType', ('bin', '0b'))

		if token.type == ETokenType.STRING :
			string = token.token.string

			for i in range(len(string)) :
				if string[i] == "'" or string[i] == '"' :
					prefixes = ['b', 'r', 'u', 'f', 'fr', 'rf', 'br', 'rb']
					prefix = string[:i]
					string = string[i:]

					if prefix.lower() in prefixes :
						token.SetAttribute('prefix', prefix)

					break

			escapes = __int_find_escseq(string)

			if len(escapes) > 0 :
				token.SetAttribute('escapes', escapes)

			brackets = __int_find_brackets(string)

			if len(brackets) > 0 :
				token.SetAttribute('brackets', brackets)