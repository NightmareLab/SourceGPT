########################
# Author: Altin (tin-z)
#
# Description:
#  Analyze function calls and extract capabilities counters.
#  Capabilities is a term taken from capa (https://github.com/mandiant/capa)
#  A full set of capabilities can be found at https://github.com/mandiant/capa-rules
#
 
name = "software capabilities"
description = "Analyze function calls and extract capabilities counters. Capabilities is a term taken from capa (https://github.com/mandiant/capa), a full set of capabilities can be found at https://github.com/mandiant/capa-rules."


char_separator="""EOF@#^#@"""
char_terminator="""EOF@#:#@\nEOF@#:#@"""
char_proj_name_holder="<@PROJ_NAME@>"
blacklist = None

assistant="""As an expert malware analyst and exploit developer, you are my assistant."""

instruction="""I am inspecting the source code of the project "<@PROJ_NAME@>". From now and on, I will upload the source codes as follows:

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

After i do that you should analyze each file and based on the programming language used, which you can look from the file extension, you should update the following counters describing a particulare action done by some part of the code, and then you will provide a score out of 100 for 'malware' representing how sure you are that code does contain malware's source code, and 'exploit' representing how sure you are that code does contain exploit's source code.

The counter are these:
```
check for OutputDebugString error 
read and send data from client to server 
execute shell command and capture output 
receive data
send data
connect to HTTP server
send HTTP request
create pipe 
get socket status
receive data on socket
send data on socket
connect TCP socket 
encode data using Base64 
encode data using XOR
run as a service 
get common file path
read file 
write file
print debug messages
resolve DNS 
get hostname 
create a process with modified I/O handles and window 
create process 
create registry key 
create service 
create thread 
persist via Windows service 
```
"""


