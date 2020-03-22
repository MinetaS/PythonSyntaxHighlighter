from ParseCode import *
import json


def stob(string) :
	return string.lower() == 'true'

def HTMLEscape(text) :
	return text.replace('\t', ' ').replace(' ', '&nbsp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br />')

def HTMLStyle(text, style) :
	string = '<span style="color:{};">'.format(style['color']) + HTMLEscape(text) + '</span>'
	if stob(style['strike']) : string = '<s>{}</s>'.format(string)
	if stob(style['italic']) : string = '<i>{}</i>'.format(string)
	if stob(style['bold']) : string = '<b>{}</b>'.format(string)
	return string


class ColorizeTheme :
	def __init__(self, name) :
		self.name = name
		self.__Load('./themes/{}.json'.format(name))

	def __Load(self, filename) :
		with open(filename, 'r') as f :
			data = json.load(f)

		self.Control   = data['control']
		self.Keyword   = data['keyword']
		self.Function  = data['function']
		self.Type      = data['type']
		self.Variable  = data['variable']
		self.String    = data['string']
		self.RawString = data['string_raw']
		self.EscString = data['string_esc']
		self.Number    = data['number']
		self.Comment   = data['comment']


class Colorize :
	def __init__(self) :
		self.__Content = ''
		self.__Theme = 'dark_default'
		self.__ThemeObject = ColorizeTheme(self.__Theme)

		self.__LineNumber = 1
		self.__LineNumberEnabled = True

	def SetTheme(self, theme) :
		self.__Theme = theme
		self.__ThemeObject = ColorizeTheme(theme)
	
	def SetContent(self, content) :
		self.__Content = content

	def SetLineNumber(self, n) :
		self.__LineNumber = n

	def EnableLineNumber(self) :
		self.__LineNumberEnabled = True

	def DisableLineNumber(self) :
		self.__LineNumberEnabled = False

	def toHTML(self) :
		# Base Template ; wrap up with <div>, text contained in <table>
		HTML = ''
		HTML += '<div class="vscode-colorize" style="width:100%; position:relative !important; overflow:auto; color:#D4D4D4; font-size:14px; font-family:Consolas, \'Liberation Mono\', Menlo, Courier, monospace !important;">\n'
		HTML += '<table class="vscode-colorize" style="width:100%; margin:0; padding:0; border:none; border-radius:4px; background-color:#1E1E1E;" cellspacing="0" cellpadding="0">\n'
		HTML += '<tr>\n'

		# Line Numbering Feature
		lines = len(self.__Content.split('\n'))

		if self.__LineNumberEnabled :
			HTML += '<td style="width:{0}px; padding:6px; padding-left:14px; padding-right:14px;">\n'.format(len(str(self.__LineNumber+lines-1))*7+6)
			HTML += '<div style="margin:0; padding:0; word-break:normal; text-align:right; line-height:130%; color:#999999;">\n'

			for i in range(lines) :
				HTML += '{0}<br />'.format(i+1)

			HTML += '</div>\n'
			HTML += '</td>\n'

		# Colorize Code
		HTML += '<td style="padding:6px; padding-left: 6px; text-align:left;">\n'
		HTML += '<div style="margin:0; padding:0; line-height:130%; color:#D4D4D4;">'

		tokens = parse(self.__Content)

		for token in tokens :
			string = token.token.string

			if ( token.type == ETokenType.TEXT or
			     token.type == ETokenType.OPERATOR or
			     token.type == ETokenType.METHOD or
			     token.type == ETokenType.MEMBER_VAR or
			     token.type == ETokenType.NEWLINE or
			     token.type == ETokenType.OTHERS ) :
				HTML += HTMLEscape(string)

			if token.type == ETokenType.CONTROL_STATEMENT :
				HTML += HTMLStyle(string, self.__ThemeObject.Control)

			if ( token.type == ETokenType.KEYWORD or
			     token.type == ETokenType.FUNCTION or 
			     token.type == ETokenType.CLASS ) :
				HTML += HTMLStyle(string, self.__ThemeObject.Keyword)
			
			if ( token.type == ETokenType.CLASS_NAME or
			     token.type == ETokenType.CLASS_PARENT or
			     token.type == ETokenType.FUNCTION_ARGTYPE or
			     token.type == ETokenType.TYPENAME ) :
				HTML += HTMLStyle(string, self.__ThemeObject.Type)

			if ( token.type == ETokenType.FUNCTION_NAME or
			     token.type == ETokenType.BUILTIN_FUNCTION ) :
			    HTML += HTMLStyle(string, self.__ThemeObject.Function)

			if ( token.type == ETokenType.FUNCTION_ARG or
			     token.type == ETokenType.FUNCTION_ARGNAME or
			     token.type == ETokenType.BULITIN_STRING ) :
			    HTML += HTMLStyle(string, self.__ThemeObject.Variable)

			if token.type == ETokenType.COMMENT :
				HTML += HTMLStyle(string, self.__ThemeObject.Comment)

			if token.type == ETokenType.NUMBER :
				a = token.GetAttribute('nType')

				if a :
					HTML += HTMLStyle(a[1], self.__ThemeObject.Keyword) + HTMLStyle(string[2:], self.__ThemeObject.Number)
				else :
					HTML += HTMLStyle(string, self.__ThemeObject.Number)

			if token.type == ETokenType.STRING :
				prefix = token.GetAttribute('prefix')
				escapes = token.GetAttribute('escapes')
				brackets = token.GetAttribute('brackets')
				is_raw = False

				if prefix :
					HTML += HTMLStyle(prefix, self.__ThemeObject.Keyword)
					string = string[len(prefix):]
					is_raw = 'r' in prefix.lower()

				style = self.__ThemeObject.RawString if is_raw else self.__ThemeObject.String
				cut = []

				if escapes :
					cut += [(e[0], e[1], 1) for e in escapes]

				if brackets :
					cut += [(e[0], e[1], 2) for e in brackets]

				cut.sort()
				last_pos = 0
				
				for c in cut :
					if c[0] < last_pos : continue
					if c[2] == 1 : style2 = self.__ThemeObject.EscString
					elif c[2] == 2 : style2 = self.__ThemeObject.Keyword

					HTML += HTMLStyle(string[last_pos:c[0]], style)
					HTML += HTMLStyle(string[c[0]:c[1]], style2)

					last_pos = c[1]

				HTML += HTMLStyle(string[last_pos:], style)

		HTML += '</div>\n'
		HTML += '</td>\n'
		HTML += '</tr>\n'
		HTML += '</table>\n'
		HTML += '</div>'

		return HTML