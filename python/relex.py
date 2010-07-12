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
'ASTERIK',
'PLUS',
'BAR',
'OTHER'
)

# Regular expression rules for simple tokens
t_LPAREN = '\('
t_RPAREN = '\)'
t_LBRACK = '\['
t_RBRACK = '\]'
t_ASTERIK = '\*'
t_PLUS = '\+'
t_BAR = '\|'

def t_OTHER(t):
    '[^][()|+* \t]+'
    return t

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '{}'".format(t.value[0]))
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
