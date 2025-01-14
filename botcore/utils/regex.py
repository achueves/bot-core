"""Common regular expressions."""

import re

DISCORD_INVITE = re.compile(
    r"(discord([.,]|dot)gg|"                     # Could be discord.gg/
    r"discord([.,]|dot)com(/|slash)invite|"      # or discord.com/invite/
    r"discordapp([.,]|dot)com(/|slash)invite|"   # or discordapp.com/invite/
    r"discord([.,]|dot)me|"                      # or discord.me
    r"discord([.,]|dot)li|"                      # or discord.li
    r"discord([.,]|dot)io|"                      # or discord.io.
    r"((?<!\w)([.,]|dot))gg"                     # or .gg/
    r")([/]|slash)"                              # / or 'slash'
    r"(?P<invite>[a-zA-Z0-9\-]+)",               # the invite code itself
    flags=re.IGNORECASE
)
"""
Regex for Discord server invites.

:meta hide-value:
"""

FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"        # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"    # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"                        # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all code inside the markup
    r"\s*"                                  # any more whitespace before the end of the code markup
    r"(?P=delim)",                          # match the exact same delimiter from the start again
    re.DOTALL | re.IGNORECASE               # "." also matches newlines, case insensitive
)
"""
Regex for formatted code, using Discord's code blocks.

:meta hide-value:
"""

RAW_CODE_REGEX = re.compile(
    r"^(?:[ \t]*\n)*"                       # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"                        # extract all the rest as code
    r"\s*$",                                # any trailing whitespace until the end of the string
    re.DOTALL                               # "." also matches newlines
)
"""
Regex for raw code, *not* using Discord's code blocks.

:meta hide-value:
"""
