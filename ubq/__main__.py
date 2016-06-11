import os
import signal
import subprocess

        
def get_other_selves():
    """Get the PIDs of other invocations of the current process (i.e. that 
    were started with the same command and arguments).
    
    Only processes owned by the same user are returned.
        
    "Other invocations" are determined in a best-effort manner. It is assumed 
    the ps executable conforms to POSIX.1-2004; since various aspects of the 
    its output are "implementation-defined" or "unspecified", how precise the
    match is depends on how much of the of the original command and arguments
    is preserved in the output.
    
    """
    my_uid = os.getuid()
    my_pid = os.getpid()
    
    processes = subprocess.check_output(
        'ps -o pid= -o args= -u'.split() + [str(my_uid)])
    processes = (l.lstrip().partition(b' ') for l in processes.splitlines())
    processes = dict((int(pid), args) for pid, _, args in processes)
    
    my_args = processes.pop(my_pid)
    
    return [pid for pid, args in processes.items() if args == my_args]
    

def main():
    other = None
    for other in get_other_selves():
        os.kill(other, signal.SIGUSR1)
    if not other:
        from ubq._ubq import main
        main()

    
if __name__ == '__main__':
    main()

