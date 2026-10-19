"""
PA 4 dependency: paste in YOUR OWN completed PA 2 lexer.py here.

This is the same file from PA 2's repo -- copy your own working
tokenize() implementation over this stub before starting parser.py.
Every PA repo is independent (no shared filesystem across repos), so
each pipeline stage bundles its own copy of the prior stages.

Complete tokenize() below. See the assignment, Part B,
for the full requirements. Must use a single compiled master regex
with named groups -- not a hand-rolled character-by-character loop.
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    type: str
    lexeme: str
    line: int


class LexError(Exception):
    pass


_MASTER_RE = re.compile(
    r"(?P<NUMBER>\d+)|"
    r"(?P<IDENT>[a-zA-Z][a-zA-Z0-9]*)|"
    r"(?P<WHITESPACE>\s+)|"
    r"(?P<COMMENT>#.*)|"
    r"(?P<PLUS>\+)|"
    r"(?P<MINUS>-)|"
    r"(?P<STAR>\*)|"
    r"(?P<SLASH>/)|"
    r"(?P<LPAREN>\()|"
    r"(?P<RPAREN>\))|"
    r"(?P<ASSIGN>=)|"
    r"(?P<SEMI>;)"
    )

def tokenize(source: str) -> List[Token]:
    """
    Convert `source` into a list of Token objects, ending in an EOF
    token with an empty lexeme. Recognize NUMBER, IDENT, LET, PLUS,
    MINUS, STAR, SLASH, LPAREN, RPAREN, ASSIGN, SEMI. Discard
    whitespace and '#'-prefixed comments without emitting tokens for
    them. Track 1-indexed line numbers. Raise LexError (with the
    offending character and line) on unrecognized input.
    """
    tokens =[]
    line_num = 1
    pos = 0
    length = len(source)
    
    while pos < length:
        match = _MASTER_RE.match(source, pos)
        
        if not match:
            raise LexError(f"Unrecognized character '{source[pos]}' at line {line_num}")
            
        type_str = match.lastgroup
        lexeme = match.group()
        
        # Requirement 9: Keyword disambiguation check
        if type_str == "IDENT" and lexeme == "let":
            type_str = "LET"
            
        # Requirement 8: Discard whitespace and comments
        if type_str != "WHITESPACE" and type_str != "COMMENT":
            tokens.append(Token(type_str, lexeme, line_num))
            
        # Requirement 7: Track line numbers
        line_num += lexeme.count('\n')
        
        # Advance the position index
        pos = match.end()
        
    tokens.append(Token("EOF", "", line_num))
    
    return tokens