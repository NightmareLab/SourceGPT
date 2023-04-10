########################
# Author: Altin (tin-z)
#
# Description:
#  Find smart contract common vulnerabilities
#
 

name = "find RCE"
description = "Find specific RCE of decompiled binaries ;)"
char_separator="""EOF@#^#@"""
char_terminator="""EOF@#:#@\nEOF@#:#@"""
char_proj_name_holder="<@PROJ_NAME@>"

# use default list
blacklist = None

assistant="""As an expert vulnerability researcher and skilled security researcher, you are my assistant."""

instruction="""I am inspecting the source code of a decompiled ELF binary. From now and on, I will upload the source codes as follows:

```
Title: <file-name>
Text:
<file-content>
EOF@#^#@

```

With '<file-name>' as the full-path of the file, and '<file-content>' the content's file, and 'EOF@#^#@' as the separator to terminate a section. After i ended to upload source codes i will send the line:

```
EOF@#:#@
EOF@#:#@
```

After i do that you should print if the user input is used inside a system-alike libc library functions, the user input is taken by 'getenv' libc library function. You can help yourself by doing taint analysis for example.
"""


