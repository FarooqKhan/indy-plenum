import pytest

from stp_core.loop.eventually import eventually
from plenum.test import waits
from plenum.test.checkpoints.helper import chkChkpoints
from plenum.test.helper import sendReqsToNodesAndVerifySuffReplies


def testCheckpointCreated(chkFreqPatched, looper, txnPoolNodeSet, client1,
                          wallet1, client1Connected, reqs_for_checkpoint):
    """
    After requests less than `CHK_FREQ`, there should be one checkpoint
    on each replica. After `CHK_FREQ`, one checkpoint should become stable
    """
    # Send one batch less so checkpoint is not created
    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1,
                                        reqs_for_checkpoint-(chkFreqPatched.Max3PCBatchSize), 1)
    # Deliberately waiting so as to verify that not more than 1 checkpoint is
    # created
    looper.runFor(2)
    chkChkpoints(txnPoolNodeSet, 1)

    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1, chkFreqPatched.Max3PCBatchSize, 1)

    timeout = waits.expectedTransactionExecutionTime(len(txnPoolNodeSet))
    looper.run(eventually(chkChkpoints, txnPoolNodeSet, 1, 0, retryWait=1, timeout=timeout))


def testOldCheckpointDeleted(chkFreqPatched, looper, txnPoolNodeSet, client1,
                             wallet1, client1Connected, reqs_for_checkpoint):
    """
    Send requests more than twice of `CHK_FREQ`, there should be one new stable
    checkpoint on each replica. The old stable checkpoint should be removed
    """
    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1,
                                        numReqs=2*reqs_for_checkpoint,
                                        fVal=1)

    sendReqsToNodesAndVerifySuffReplies(looper, wallet1, client1,
                                        numReqs=1,
                                        fVal=1)

    timeout = waits.expectedTransactionExecutionTime(len(txnPoolNodeSet))
    looper.run(eventually(chkChkpoints, txnPoolNodeSet, 2, 0, retryWait=1, timeout=timeout))
