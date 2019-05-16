from os import getenv
import socket
import types
from colorama import init, Fore, Style

init(autoreset=True)
ATTENTION_STYLE = Fore.YELLOW + Style.BRIGHT
WARNING_STYLE = Fore.RED + Style.BRIGHT
SUCCESSFUL_STYLE = Fore.GREEN + Style.BRIGHT


class DebuggerModuleRequired(ImportError):
    pass


try:
    import pydevd_pycharm as pydevd
except ImportError:
    try:
        import pydevd
    except ImportError:
        try:
            import ptvsd
        except ImportError:
            raise DebuggerModuleRequired(WARNING_STYLE + 'pydevd for Pycharm or ptvsd for VSCode is required')

start_debugger = getenv('START_DEBUGGER', '')
host = getenv('DEBUGGER_HOST', '127.0.0.1')
port = int(getenv('DEBUGGER_PORT', '9000'))


def attach_pycharm(configure_func, call_immediately=False):
    '''
    Attaches PyCharm's remote debugging configuration

    :param configure_func: runs PyCharm's method to start the debugger. For example, ``lambda host, port: pydevd_pycharm.settrace(host, port=port, stdoutToServer=True, stderrToServer=True, suspend=False)``
    :type configure_func: types.FunctionType
    :param call_immediately: calls configure_func immediately because the logic to enable it is handled in the client code
    :type call_immediately: bool
    '''
    pydevd.settrace(host, port=port, stdoutToServer=True, stderrToServer=True)
    if start_debugger or call_immediately:
        s = socket.socket()

        try:
            print('\n\n' ' Attempting to communicate to the IDE')

            print(ATTENTION_STYLE + ' **IMPORTANT** ' + Style.RESET_ALL
                  + 'Remote debugger configuration in PyCharm MUST be run first')
            s.connect((host, port))
            s.close()

            print(' Attempting to attach debugger')
            configure_func(host, port)
        except socket.error:
            print(
                WARNING_STYLE + " Could not connect to {host}:{port}. "
                "{style}Ensure that you have a reverse port forward to {host}:{port}.\n\n".format(
                    host=host, port=port, style=ATTENTION_STYLE)
            )


def attach_vscode(configure_func, call_immediately=False):
    '''
    Attaches Visual Studio Code's remote debugging configuration

    :param configure_func: runs Visual Studio Code's method to start the debugger. For example, ``lambda host, port: ptvsd.enable_attach(address=(host, port), redirect_output=True)``
    :type configure_func: types.FunctionType
    :param call_immediately: calls configure_func immediately because the logic to enable it is handled in the client code
    :type call_immediately: bool
    '''
    if start_debugger or call_immediately:
        configure_func(host, port)
        print('\n\n' + SUCCESSFUL_STYLE + ' Now ready for the IDE to connect to the debugger')
        print(ATTENTION_STYLE + ' **IMPORTANT** ' + Style.RESET_ALL
              + 'Remote debugger configuration in VSCode can now be run')
        print(ATTENTION_STYLE + ' Ensure that you have a local port forward to {host}:{port}.\n\n'.format(
            host=host, port=port))
        ptvsd.wait_for_attach()
