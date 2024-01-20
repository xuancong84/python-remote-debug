# Python Remote Debug

This is a tutorial on how to setup a convenient Python remote debugging (the debug server approach) for VSCode. The setup makes the launch process fully automated as if running the debugger locally.

## Basic Principles:
Firstly, it is important to understand the basic principle of how remote debug server debugging works, it consists of three basic steps:
1. Ensure local repository and remote repository files are synchronized, you can use `sshfs` to mount "the project folder on the server" onto "some local folder mount point" without copying over files. The command line is `sshfs <username>@<server-IP>:<remote-folder> <local-folder>`
2. On the server side, launch the debug server using Python pip package `debugpy`, and listen on a chosen port number (not blocked by firewall)
3. On the local side, perform attach remote debugger to the chosen port number, and then start debugging

## Basic Steps:
In practice, the detailed steps are as follows:
1. We typically use `sshfs` to ssh-mount the remote folder onto some local folder. So you need to make sure you can SSH the server from your local machine.
2. On the server, make sure the pip package `debugpy` is installed, and run `python -m debugpy --listen xxx.xxx.xxx.xxx:12345 --wait-for-client your-python-code.py`, where xxx.xxx.xxx.xxx is the server IP address that your local machine has direct access to, 12345 can be any chosen port on the server that is not blocked by any firewall, and `your-python-code.py` is the Python program that you want to debug.
3. On the local machine, run VSCode to open the project folder; in `run and debug` tab, click `create a launch.json file`, select `Python` and then `Remote Attach`, type in the server IP address and the debugger listening port, and then edit the `launch.json` accordingly:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "xxx.xxx.xxx.xxx:12345",
                "port": 12345
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "."
                }
            ],
            "preLaunchTask": "prepare",
            "justMyCode": true
        }
    ]
}
```
Take note of the project's root folder mapping between local and remote, and add a new entry `"preLaunchTask": "prepare"` into `launch.json` .

## Add pre-launch task to automate the launch process
To simply the launch process into a single click, you will need to create a pre-launch task that does Step 1 and 2. In the `terminal` menu, click `configure tasks...`, and choose `create tasks.json file from template`, and select `others`. Edit `tasks.json` as follows:
```
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "prepare",
            "type": "shell",
            "command": "ssh xxx.xxx.xxx.xxx 'cd projects/test-debug-server/; python -m debugpy --listen xxx.xxx.xxx.xxx:12345 --wait-for-client your-python-code.py 1>/dev/null 2>/dev/null' & while ! ssh xxx.xxx.xxx.xxx netstat -tnl | grep :12345; do sleep 0.1; done"
        }
    ]
}
```
where all symbols are defined in the same way as in Step 2 above. The full command consists of two parts: 1. launch the remote debug server via ssh and set it to background; 2. wait for the debug port to be ready. Take note that `1>/dev/null 2>/dev/null` is neccessary if your program has STDOUT/STDERR output.

## X11 tunneling for GUI
If you need to use Python graphics libraries like `matplotlib` to plot charts, you will need X11 tunneling via SSH. To do so:
1. In another terminal, SSH to the remote server with X11 forwarding enabled, `ssh -YC xxx.xxx.xxx.xxx`
2. In that terminal, get the DISPLAY port number, `echo $DISPLAY`, it will be typically something like `localhost:0.0`
3. Modify the 2nd command in `tasks.json` from:
```
ssh xxx.xxx.xxx.xxx 'cd projects/test-debug-server/; python -m debugpy --listen xxx.xxx.xxx.xxx:12345 --wait-for-client your-python-code.py 1>/dev/null 2>/dev/null'
```
into
```
ssh -YC xxx.xxx.xxx.xxx 'cd projects/test-debug-server/; DISPLAY=localhost:0.0 python -m debugpy --listen xxx.xxx.xxx.xxx:12345 --wait-for-client your-python-code.py 1>/dev/null 2>/dev/null'
```
with the correct DISPLAY environment variable.

Remember, as long as you want to display something via X11 tunnel in remote debugging, that SSH session in the separate terminal must be kept running.
