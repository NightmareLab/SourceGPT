# Adding an extension to SourceGPT


 - (1) Go inside folder `src/extension` copy and paste `skel.py` as `<you-extension.py>`

 - (2) Redefine what you need, and add extra db arguments inside the variable 'extra'

   * (2.1) The code that will be executed after you trigger a request from the front-end to the extension api must be declared inside the function `main()`
    
   * (2.2) The front-end file used as your extension's front-end is pointed by the variable 'html_file', which will point to a html file declared inside the folder `./src/templates/extension`

   * (2.3) Write the extension's fornt-end file

 - (3) Now modify the `src/extension/__init__.py` by adding your extension to the 'extns_list' list

 - (4) If you need to add actions (e.g. git clone etc.) write the code inside the folder `src/actions/`



Html pages expect the following arguments:
 - prompt_model : which is the prompt model entry on db
 - extension_model : which is the extension model entry on db
 - status : latest operation status



