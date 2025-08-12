"""
Raft Fault - Raft Consensus Implementation for Gradysim with Fault Tolerance

A domain-independent, modular Raft consensus implementation designed for easy
integration with Gradysim simulations. Provides consensus with fault tolerance,
log replication, and active node-based majority calculation.
"""

from .raft_consensus import RaftConsensus
from .raft_config import RaftConfig, RaftMode
from .raft_state import RaftState
from .raft_message import (
    RequestVote, RequestVoteResponse,
    AppendEntries, AppendEntriesResponse
)
from .adapters import GradysimAdapter
from .failure_detection import FailureConfig, HeartbeatDetector

__version__ = "0.1.0"
__author__ = "Laércio Lucchesi"

# Define base exports
__all__ = [
    "RaftConsensus",
    "RaftConfig",
    "RaftMode",
    "RaftState",
    "RequestVote",
    "RequestVoteResponse",
    "AppendEntries",
    "AppendEntriesResponse",
    "GradysimAdapter",
    "FailureConfig",
    "HeartbeatDetector"
]

# Note: Example protocols are available in the examples files 