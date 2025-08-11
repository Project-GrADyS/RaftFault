"""
Raft Lite - Lightweight Raft Consensus Implementation for Gradysim

A domain-independent, modular Raft consensus implementation designed for easy
integration with Gradysim simulations. Provides lightweight consensus without
log replication, focusing on consensus values only.

Main Features:
- Isolated and reusable consensus logic
- Domain-independent design
- Easy Gradysim integration
- Light Raft implementation (no log replication)
- Extensible for multiple consensus variables
- Modular architecture following SOLID principles
- Simple and intuitive interface
- Active node-based majority calculation
- Robust failure detection and recovery

Example Usage:
    from raft_fault import RaftConsensus, RaftConfig, GradysimAdapter
    
    # Configure consensus
    config = RaftConfig()
    config.set_election_timeout(150, 300)
    config.set_heartbeat_interval(50)
    config.add_consensus_variable("sequence", int)
    
    # Failure detection is automatically enabled in Fault-Tolerant mode
# No need to explicitly enable it
    
    # Create Gradysim adapter
    adapter = GradysimAdapter(provider)
    
    # Create consensus instance with adapter (simplified)
    consensus = RaftConsensus(
        config=config,
        adapter=adapter
    )
    
    # Use in your protocol
    consensus.start()
    
    # Check if we have quorum of active nodes
    if consensus.has_quorum():
        consensus.propose_value("sequence", 42)
    
    # Get detailed majority information
    majority_info = consensus.get_majority_info()
    print(f"Active nodes: {majority_info['active_nodes']}")
    print(f"Has quorum: {majority_info['has_majority']}")
    
    # Get node position from telemetry
    position = adapter.get_node_position(telemetry)
    print(f"Node position: {position}")
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

__version__ = "1.0.0"
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