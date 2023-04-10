#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int execute_command(char* command) {
    int status = system(command);
    if (WIFEXITED(status)) {
        int exit_status = WEXITSTATUS(status);
        return exit_status;
    } else {
        return -1;
    }
}


int main() {
    char* myvar = getenv("MYVAR");
    if (myvar == NULL) {
        printf("MYVAR is not set\n");
        return 1;
    }
    printf("MYVAR=%s\n", myvar);

    char cmd[100];
    snprintf(cmd, sizeof(cmd), "echo %s", myvar);
    execute_command(cmd);

    return 0;
}

