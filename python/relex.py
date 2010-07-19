# ------------------------------------------------------------
# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# List of token names.   This is always required

tokens = (
'LPAREN',
'RPAREN',

'LBRACK',
'RBRACK',

'LBRACE',
'RBRACE',

'ASTERIK',
'PLUS',
'BAR',
'NUMBER',
'COMMA',
'OPT',
'OTHER'
)

# Regular expression rules for simple tokens
t_LPAREN = '\('
t_RPAREN = '\)'

t_LBRACK = '\['
t_RBRACK = '\]'

t_LBRACE = '{'
t_RBRACE = '}'

t_ASTERIK = '\*'
t_PLUS = '\+'
t_BAR = '\|'
t_COMMA = ','
t_OPT = '\?'

def t_NUMBER(t):
    '[0-9]+'
    return t

def t_OTHER(t):
    '[^][()|+*{}?, \t]'
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
