"""Linux subreaper keeps even fast-exiting launchers' orphaned descendants in owned scope."""
# Linux prctl is available through the standard library, with no new dependency.
import ctypes
# Original process identity and signals are checked through kernel start ticks.
import os
# Explicit signals never match process names or unrelated groups.
import signal
# Only an argv list is launched, inheriting the already bounded pipes/environment.
import subprocess
# Command-line arguments preserve exact caller values without a shell.
import sys
# A small cleanup allowance handles asynchronous process exit after SIGKILL.
import time
# Reuse the settled portfolio's verified ancestry/start-time ownership primitives.
from portfolio_external import owned_descendants,process_tick,process_live

# The wrapper remains alive when a native/Codex launcher exits before its descendants.
def main(argv):
    """Run argv under a Linux subreaper; return main exit code after owned-child cleanup.

    Args executable argv list, e.g. ['python','-V']. Inherits raw pipes and env,
    owns only its new descendants. prctl/cleanup failure exits nonzero rather
    than returning success while background work survives. No repository writes.
    """
    # Adopt orphaned descendants into this fresh, dedicated launcher rather than system init.
    libc=ctypes.CDLL(None,use_errno=True)
    # PR_SET_CHILD_SUBREAPER=36 is the Linux process-ownership facility, not a permission bypass.
    if libc.prctl(36,1,0,0,0)!=0:
        # Unsupported isolation is a real failed execution, never an unsupervised fallback.
        raise OSError(ctypes.get_errno(),'cannot establish owned descendant subreaper')
    # The outer controller's start_new_session owns this wrapper and all of its children.
    owner=os.getpid()
    # Incarnation identity prevents reused PIDs from becoming cleanup targets.
    tick=process_tick(owner)
    # Main command retains the wrapper session, while native MPI may create descendant sessions.
    child=subprocess.Popen(argv)
    # The outer owned_process timeout handles a blocked main command and this entire descendant tree.
    code=child.wait()
    # Reparented orphans are still descendants of this live subreaper after main exit.
    descendants=owned_descendants(owner,tick)
    # Stop any live background work even after a nominally successful launcher exit.
    for pid,incarnation in reversed(descendants):
        # Verify the observed owned incarnation immediately before signaling it.
        if process_live(pid,incarnation):
            # Short-lived exits are harmless, never a reason for kill-by-name.
            try:
                # Force only residual work after the main command already terminated.
                os.kill(pid,signal.SIGKILL)
            # Already exited children have no surviving work to terminate.
            except ProcessLookupError:
                # Continue cleanup of other actual owned children.
                pass
    # Reap adopted orphans and let killed processes reach terminal state within a bounded interval.
    deadline=time.monotonic()+.3
    # Only the captured incarnations can establish a remaining-live-process failure.
    while time.monotonic()<deadline:
        # Reaping uses only children of this dedicated new wrapper.
        try:
            # WNOHANG cannot block indefinitely on a child in shutdown.
            reaped,status=os.waitpid(-1,os.WNOHANG)
        # No child remains; all numerical/model work is gone.
        except ChildProcessError:
            # Normal completion has no need to wait out the cleanup allowance.
            break
        # A live child gets a brief scheduling interval before another bounded observation.
        if reaped==0:
            # This is cleanup time, included in the outer end-to-end deadline.
            time.sleep(.005)
    # A still-running owned child is an operational failure rather than false successful cleanup.
    if any(process_live(pid,incarnation) for pid,incarnation in descendants):
        # The outer controller retains this failure and its raw stderr.
        raise RuntimeError('owned orphan remains live after bounded cleanup')
    # Shell-style signal exit mapping preserves the actual failed main-command semantics.
    return code if code>=0 else 128-code

# This is a trusted process wrapper, never a candidate hook or recursive controller.
if __name__=='__main__':
    # No source mutation, solver selection or model call occurs outside the supplied argv.
    raise SystemExit(main(sys.argv[1:]))
