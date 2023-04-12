
# You need to do:
#   - copy skel.py
#   - Modify extension and prompt settings
#   - create the html page inside ./src/templates/extension/<html_file>
#   - implement the method 'main()'
#
# See below for more info
# Remember also to add this module to the extension/__init__.py as described there
#


##############################
## Extension settings
############################
name = "Name of the extension"
description = "Description of the extension"

# which means that inside folder './src/templates/extension' there's the file diff_vuln.html
# so when the request "GET /extension?id_extns=<extension_id>" is done, the right response will return
html_file = "skel.html"

# extra settings to keep into 'extra's column extension schema
extra = {}

##############################
## Prompt settings
############################
prompt_name = "extns-prompt-{}".format(name)
prompt_description = "Read the extension's description"

char_separator="""EOF@#^#@"""
char_terminator="""EOF@#:#@\nEOF@#:#@"""
char_proj_name_holder="<@PROJ_NAME@>"
blacklist = None

git_url_project_http_form = "git_url_proj"
git_url_project = "@^GIT-URL^@"

extra_replacer = {
  git_url_project_http_form : git_url_project
}

assistant="Aa a security code auditor and expert security researcher, you are my assistant."

instruction="""I am analyzing the <@PROJ_NAME@> project which is hosted on @^GIT-URL^@. From now and on, I will upload the diff files as follows:

```
Title: <file-name>
Part: <file-part>
Text:
<file-content>
EOF@#^#@

```

With '<file-name>' as the full-path of the file, '<file-part>' as the content's file part number with '0' denoting the last part, and '<file-content>' as the content's file, and 'EOF@#^#@' as the separator to terminate a section. After i ended to upload source codes i will send the line:

```
EOF@#:#@
EOF@#:#@
```

After i do that print what the code is doing."""



## The method main should be extended as follows
def main(db_session, request_session, *args, **kwargs):
  """
    db_session      : Db session saved as WrapMongo class
    request_session : flask request object
  """
  pass


