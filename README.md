# RaftFault

A lightweight, fault-tolerant Raft consensus implementation designed for distributed systems and network simulations. **RaftFault** focuses on consensus values and leader election without log replication, making it perfect for scenarios where you need distributed coordination but not full state machine replication.

## **About GradySim**

**GrADyS-SIM NextGen** is a network simulation framework that enables you to create simulations capable of representing scenarios populated by network nodes that coexist in a simulated environment and can send messages to each other. The primary focuses of the simulator are usability and flexibility. RaftFault is designed to integrate seamlessly with GradySim, allowing you to test distributed consensus algorithms in realistic network simulation environments.

**Learn more about GradySim:**
- 📖 **Documentation**: [https://project-gradys.github.io/gradys-sim-nextgen/](https://project-gradys.github.io/gradys-sim-nextgen/)
- 🔗 **GitHub Repository**: [https://github.com/Project-GrADyS/gradys-sim-nextgen](https://github.com/Project-GrADyS/gradys-sim-nextgen)

##  **Raft Fault Key Features**

- **Fault-Tolerant Consensus**: Robust leader election with automatic recovery
- **Active Node Discovery**: Dynamic cluster size detection for accurate majority calculations
- **Heartbeat-Based Failure Detection**: Automatic detection of failed nodes
- **Massive Failure Recovery**: Recovers from scenarios where massive quantity of nodes fail
- **Scalable Architecture**: Works with any number of nodes (10, 50, 100+)
- **GradySim Integration**: Seamless integration with GrADyS-SIM NextGen simulation framework
- **No Log Replication**: Lightweight implementation focused on consensus values
- **Dynamic Majority Calculation**: Thresholds adapt to actual active nodes
- **Dual Operation Modes**: Classic Raft and Fault-Tolerant modes
- **Callback-Based Architecture**: Clean separation between consensus and platform
- **Active Node Information**: Real-time access to node information

##  **Table of Contents**

- [Overview](#overview)
- [Raft Timers and System Integration](#raft-timers-and-system-integration)
- [Key Innovations](#key-innovations)
- [Raft Operation Modes](#raft-operation-modes)
- [Setup and Installation](#setup-and-installation)
- [Quick Start](#quick-start)
- [GradySim Integration](#gradysim-integration)
- [Consensus Variables](#consensus-variables)
- [Active Node Discovery](#active-node-discovery)
- [Failure Detection](#failure-detection)

- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## **Overview**

RaftFault implements a **fault-tolerant distributed consensus** system based on the Raft algorithm, but optimized for scenarios where you need:

- **Distributed coordination** without full state machine replication
- **Leader election** with automatic failover
- **Consensus on values** (not log entries)
- **Robust failure recovery** even after massive node losses
- **Platform independence** through adapter pattern

### **What Makes RaftFault Special**

1. **Active Node Discovery**: Before elections, nodes discover the actual number of active peers
2. **Dynamic Majority**: Thresholds calculated based on discovered active nodes, not total nodes
3. **Massive Failure Recovery**: Can recover even when massive quantity of nodes fail
4. **Fast Recovery**: Discovery phase ensures quick leader election after failures
5. **Scalable**: Works with any cluster size without configuration changes
6. **Dual Modes**: Choose between Classic Raft and Fault-Tolerant operation
7. **Adapter Pattern**: Clean integration with any platform via callbacks

## **Raft Timers and System Integration**

### **⚠️ Important: Reserved Timer Names**

RaftFault uses specific timer names that are **exclusive to the system** and cannot be used for other purposes. Using these names for your own timers will cause conflicts and disrupt the consensus operation.

#### **Reserved Timer Names:**

1. **`"election_timeout"`** - Controls when a node should start an election
2. **`"heartbeat"`** - Controls leader heartbeat sending
3. **`"discovery_timeout_{node_id}_{term}"`** - Controls active node discovery timeout

#### **Timer Behavior:**

- **Election Timeout**: Randomized between `min_timeout` and `max_timeout` (e.g., 200-400ms)
- **Heartbeat**: Fixed interval defined by `heartbeat_interval` (e.g., 30ms)
- **Discovery Timeout**: Based on election timeout for active node discovery

#### **Configuration Example:**

```python
config = RaftConfig()
config.set_election_timeout(200, 400)  # 200-400ms randomized
config.set_heartbeat_interval(30)      # 30ms fixed interval
```

#### **⚠️ Warning:**

**DO NOT** use these timer names for your own timers:
```python
# ❌ WRONG - Will conflict with Raft system
adapter.schedule_timer("election_timeout", 1000)  # Conflicts with Raft
adapter.schedule_timer("heartbeat", 500)          # Conflicts with Raft

# ✅ CORRECT - Use different names
adapter.schedule_timer("my_custom_timer", 1000)   # Safe to use
adapter.schedule_timer("monitoring_timer", 500)   # Safe to use
```

### **Failure Detection (No Dedicated Timers)**

The failure detection system does **not** use dedicated timers. Instead, it operates based on:
- **Heartbeat counter**: Checks every N heartbeats (defined by `detection_interval`)
- **Timeout calculations**: Based on heartbeat interval or absolute values
- **Response tracking**: Monitors heartbeat responses from all nodes

```python
failure_config = config.get_failure_config()
failure_config.set_detection_interval(2)     # Check every 2 heartbeats
failure_config.set_heartbeat_timeout(4)      # 4× heartbeat_interval
```

## **Beyond Classic Raft: Essential Extensions**

### **1. Active Node Discovery System**

RaftFault introduces a **discovery phase** before elections that solves the fundamental problem of unknown cluster size after failures:

```python
# Traditional Raft: Uses fixed cluster size
majority = (total_nodes // 2) + 1  # Always uses total_nodes

# RaftFault: Discovers actual active nodes
discovered_active = discover_active_nodes()  # Dynamic discovery
majority = (discovered_active // 2) + 1     # Uses actual active nodes
```

**Benefits:**
-  **Accurate majority calculations** after failures
-  **Faster leader election** with correct thresholds
-  **Automatic adaptation** to cluster changes
-  **No manual configuration** needed

### **2. Massive Failure Recovery**

RaftFault can recover from scenarios that would break traditional Raft implementations:

```python
# Scenario: 10 nodes, 8 fail (including leader)
# Traditional Raft: Stuck - can't calculate majority
# RaftFault: Discovers 2 active nodes, calculates majority = 2, elects leader
```

### **3. Dynamic Cluster Adaptation**

The system automatically adapts to cluster changes:

```python
# Initial: 10 nodes active
# After failures: 3 nodes active
# RaftFault automatically adjusts majority threshold from 6 to 2
```

### **4. Callback-Based Architecture**

Clean separation between consensus logic and platform integration:

```python
# Adapter provides platform-specific callbacks
callbacks = {
    'send_message_callback': adapter.send_message,
    'schedule_timer_callback': adapter.schedule_timer,
    'get_current_time_callback': adapter.get_current_time
}

# Raft uses callbacks without knowing the platform
raft_node = RaftNode(node_id=1, config=config, callbacks=callbacks)
```

## **Raft Operation Modes**

RaftFault supports two distinct operation modes, allowing you to choose between classic Raft behavior and fault-tolerant enhancements:

### **Classic Raft Mode (`RaftMode.CLASSIC`)**

Classic Raft Mode implements the standard Raft protocol as specified by Ongaro and Ousterhout [1]. The only divergence in our system is replication: Raft-Fault targets agreement on consensus values rather than maintaining a replicated log.
[1] D. Ongaro and J. Ousterhout, “In Search of an Understandable Consensus Algorithm,” Proc. USENIX ATC, Philadelphia, PA, USA, Jun. 2014, pp. 305–319.

**Characteristics:**
-  **Fixed Cluster Size**: Uses total known nodes for all majority calculations
-  **Direct Elections**: No discovery phase - immediate election on timeout
-  **Standard Behavior**: Classic Raft consensus semantics
-  **Better Performance**: Lower overhead (no discovery phase)
-  **Deterministic**: Predictable behavior for static clusters
-  **Manual Failure Handling**: Requires manual cluster reconfiguration after failures

**Use Cases:**
- Static clusters with fixed, known node count
- Environments where performance is critical
- Systems requiring standard Raft semantics
- Scenarios with manual failure management

### **Fault-Tolerant Raft Mode (`RaftMode.FAULT_TOLERANT`)**

Enhanced Raft implementation with automatic fault tolerance and dynamic cluster adaptation.

**Characteristics:**
-  **Dynamic Active Node Detection**: Discovery phase before elections
-  **Adaptive Majority Calculation**: Uses active node count for thresholds
-  **Massive Failure Recovery**: Automatic recovery from massive quantity of node failures
-  **Self-Healing**: Automatic adaptation to cluster changes
-  **Fault Tolerance**: No manual intervention needed
-  **Active Node Information**: Real-time access to node information
-  **Discovery Overhead**: Small performance cost for discovery phase

**Use Cases:**
- Dynamic environments with node failures
- Distributed systems requiring high availability
- Scenarios with unpredictable node failures
- Systems that need automatic fault recovery

### **Configuration Examples**

#### **Classic Raft Mode Configuration**
```python
from raft_fault import RaftConfig, RaftMode

# Configure for classic Raft behavior
config = RaftConfig()
config.set_raft_mode(RaftMode.CLASSIC)
config.set_election_timeout(150, 300)
config.set_heartbeat_interval(50)

# Classic mode: Uses total known nodes for majority
# No discovery phase - direct elections
# Standard Raft semantics
```

#### **Fault-Tolerant Raft Mode Configuration**
```python
from raft_fault import RaftConfig, RaftMode

# Configure for fault-tolerant behavior
config = RaftConfig()
config.set_raft_mode(RaftMode.FAULT_TOLERANT)  # Default mode
config.set_election_timeout(200, 400)  # Longer timeouts for discovery
config.set_heartbeat_interval(50)

# Fault-tolerant mode: Uses active node discovery
# Dynamic majority calculations
# Automatic fault recovery
```

### **Mode Comparison**

| Feature | Classic Mode | Fault-Tolerant Mode |
|---------|--------------|---------------------|
| **Discovery Phase** | ❌ Disabled | ✅ Enabled |
| **Majority Calculation** | Fixed (total nodes) | Dynamic (active nodes) |
| **Failure Recovery** | ❌ Manual | ✅ Automatic |
| **Performance** | ✅ Faster | ⚡ Slight overhead |
| **Massive Failures** | ❌ Requires intervention | ✅ Auto-recovery |
| **Active Node Info** | ❌ Not available | ✅ Available |
| **Use Case** | Static clusters | Dynamic clusters |
| **Standard Raft** | ✅ Compliant | Enhanced |

### **Runtime Mode Detection**

```python
# Check current mode
if config.is_classic_mode():
    print("Running in Classic Raft mode")
    # No discovery, standard Raft behavior
elif config.is_fault_tolerant_mode():
    print("Running in Fault-Tolerant Raft mode")  
    # Discovery enabled, dynamic fault tolerance

# Get mode programmatically
current_mode = config.get_raft_mode()
print(f"Current mode: {current_mode.value}")
```

### **Choosing the Right Mode**

**Choose Classic Mode When:**
-  Cluster size is fixed and known
-  Performance is critical
-  Standard Raft behavior is required
-  Manual failure management is acceptable

**Choose Fault-Tolerant Mode When:**
-  Nodes may fail unexpectedly
-  Automatic fault recovery is needed
-  Cluster size varies dynamically
-  High availability is required
-  Active node information is needed

## **Setup and Installation**

It is recommended that this project uses a Python virtual environment to manage dependencies.

### **Virtual Environment Setup**

#### Windows
```bash
# Option 1: Use the script
activate_env.bat

# Option 2: Direct command
raft_env\Scripts\activate
```

#### Linux/macOS
```bash
# Option 1: Use the script
chmod +x activate_env.sh
./activate_env.sh

# Option 2: Direct command
source raft_env/bin/activate
```

### **Installing Dependencies**

After activating the virtual environment, install the dependencies:

```bash
pip install -r requirements.txt
```

### **Running the Project**

```bash
python main.py
```

### **Main Dependency**

- `gradysim` 0.7.3 - Simulation framework

## **Quick Start**

### **Basic Setup**

```python
from raft_fault import RaftConsensus, RaftConfig, RaftMode, GradysimAdapter

# 1. Configure consensus
config = RaftConfig()
config.set_election_timeout(150, 300)  # 150-300ms election timeout
config.set_heartbeat_interval(50)      # 50ms heartbeat interval
config.add_consensus_variable("sequence", int)
config.add_consensus_variable("leader_position", str)

# Choose operation mode
config.set_raft_mode(RaftMode.FAULT_TOLERANT)  # Default: fault-tolerant mode
# config.set_raft_mode(RaftMode.CLASSIC)      # Alternative: classic mode

# 2. Create adapter and consensus
adapter = GradysimAdapter(provider)
consensus = RaftConsensus(config=config, adapter=adapter)

# 3. Set known nodes and start
# Known nodes has to be the same as defined in the main simulation.
consensus.set_known_nodes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
consensus.start()

# 4. Use consensus
if consensus.is_leader():
    consensus.propose_value("sequence", 42)

# 5. Get committed values
value = consensus.get_committed_value("sequence")
```

### **Active Node Information (Fault-Tolerant Mode)**

```python
# Get detailed information about active nodes
active_info = consensus.get_active_nodes_info()

print(f"Active nodes: {active_info['active_nodes']}")
print(f"Total nodes: {active_info['total_nodes']}")
print(f"Failed nodes: {active_info['failed_nodes']}")
print(f"Mode: {active_info['mode']}")

# Check if we have quorum
if consensus.has_quorum():
    print("✅ Cluster has quorum")
else:
    print("❌ Cluster lacks quorum")
```

## **GradySim Integration**

### **Protocol Implementation**

```python
from gradysim.protocol.interface import IProtocol
from raft_fault import RaftConsensus, RaftConfig, RaftMode, GradysimAdapter

class RaftProtocol(IProtocol):
    def initialize(self):
        # Create adapter
        self.adapter = GradysimAdapter(self.provider)
        
        # Configure Raft consensus
        config = RaftConfig()
        config.set_election_timeout(150, 300)
        config.set_heartbeat_interval(50)
        config.add_consensus_variable("sequence", int)
        
        # Choose operation mode
        config.set_raft_mode(RaftMode.FAULT_TOLERANT)  # or RaftMode.CLASSIC

        # Configure failure detection parameters if RaftMode is FAULT_TOLERANT
        failure_config = config.get_failure_config()
        failure_config.set_failure_threshold(2)      # 2 failed heartbeats to mark as failed
        failure_config.set_recovery_threshold(3)     # 3 successful heartbeats to recover
        failure_config.set_detection_interval(2)     # Check every 2 heartbeats
        failure_config.set_heartbeat_timeout(4)      # 4× heartbeat_interval = 200ms timeout
        
        self.consensus = RaftConsensus(config=config, adapter=self.adapter)
        
        # Start consensus
        self.consensus.set_known_nodes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.consensus.start()
    
    def handle_timer(self, timer: str):
        # Forward timers to consensus
        if self.consensus:
        self.consensus.handle_timer(timer)
        
    def handle_packet(self, message: str):
        # Forward messages to consensus
        if self.consensus:
            self.consensus.handle_message(message)

    def handle_telemetry(self, telemetry: Telemetry) -> None:
        # Propose values if leader
        if self.consensus.is_leader():
            self.consensus.propose_value("sequence", 42)
    
    def finish(self):
        if self.consensus:
            # Stop consensus
            self.consensus.stop()
```

### **Adapter Features**

The `GradySimAdapter` provides comprehensive platform integration capabilities:

- **Communication**: Point-to-point and broadcast messaging
- **Timing**: Timer scheduling and cancellation
- **Node Information**: Dynamic node ID and position retrieval
- **Visualization**: Node coloring for debugging
- **Failure Detection**: Integration with heartbeat-based failure detection

#### **Communication Examples**

```python
# Point-to-point messaging
adapter.send_message("Hello from node 1", target_id=2)
adapter.send_message(json.dumps({"type": "heartbeat", "term": 5}), target_id=3)

# Broadcast messaging
adapter.send_broadcast("Election announcement")
adapter.send_broadcast(json.dumps({"type": "append_entries", "term": 5}))
```

#### **Timer Management Examples**

```python
# Schedule timers
adapter.schedule_timer("election_timeout", delay_ms=300)
adapter.schedule_timer("heartbeat", delay_ms=50)
adapter.schedule_timer("discovery_timeout", delay_ms=150)

# Cancel timers
adapter.cancel_timer("election_timeout")
adapter.cancel_timer("heartbeat")

# Get current time
current_time = adapter.get_current_time()
print(f"Current simulation time: {current_time}")
```

#### **Node Information Examples**

```python
# Get current node ID
node_id = adapter.get_node_id()
print(f"Current node ID: {node_id}")

# Get node position from telemetry
position = adapter.get_node_position(telemetry)
print(f"Node position: {position}")  # (x, y, z)

# Extract coordinates
x, y, z = position
print(f"X: {x}, Y: {y}, Z: {z}")
```

#### **Visualization Examples**

```python
# Paint current node
adapter.paint_node("blue")                # Paint current node blue
adapter.paint_node("green")               # Paint current node green

# Paint specific nodes
adapter.paint_node("red", node_id=1)      # Paint node 1 red
adapter.paint_node("yellow", node_id=5)   # Paint node 5 yellow
adapter.paint_node("purple", node_id=10)  # Paint node 10 purple

# Color coding for different states
if consensus.is_leader():
    adapter.paint_node("green")           # Leader = green
elif consensus.is_candidate():
    adapter.paint_node("yellow")          # Candidate = yellow
else:
    adapter.paint_node("blue")            # Follower = blue
```

#### **Available Colors**

The `paint_node()` method supports the following colors based on the GradySim color palette:

**Available Colors:**
- `"red"` - Red (255, 0, 0)
- `"blue"` - Blue (0, 0, 255)
- `"green"` - Green (0, 255, 0)
- `"yellow"` - Yellow (255, 255, 0)
- `"purple"` - Purple (255, 0, 255)
- `"cyan"` - Cyan (0, 255, 255)
- `"white"` - White (255, 255, 255)
- `"black"` - Black (0, 0, 0)

**Color Coding Examples:**

```python
# Raft state-based coloring
if consensus.is_leader():
    adapter.paint_node("green")           # Leader = green
elif consensus.is_candidate():
    adapter.paint_node("yellow")          # Candidate = yellow
else:
    adapter.paint_node("blue")            # Follower = blue

# Failure status coloring
if node_id in active_info['failed_nodes']:
    adapter.paint_node("red", node_id=node_id)      # Failed = red
elif node_id in active_info['active_nodes']:
    adapter.paint_node("green", node_id=node_id)    # Active = green
else:
    adapter.paint_node("black", node_id=node_id)    # Unknown = black

# Custom status coloring
adapter.paint_node("purple", node_id=leader_id)     # Special leader
adapter.paint_node("yellow", node_id=candidate_id)  # Election candidate
adapter.paint_node("cyan", node_id=observer_id)     # Observer node
adapter.paint_node("white", node_id=gateway_id)     # Gateway node
```

#### **Failure Detection Integration**

```python
# The adapter automatically integrates with failure detection
# No additional code needed - it's handled internally

# But you can monitor failure detection status
active_info = consensus.get_active_nodes_info()
if active_info['failed_nodes']:
    print(f"Failed nodes detected: {active_info['failed_nodes']}")
    
# Visual feedback for failed nodes
for node_id in active_info['failed_nodes']:
    adapter.paint_node("red", node_id=node_id)  # Failed nodes = red
```

#### **Node Failure Simulation**

RaftFault provides methods to manually simulate node failures for testing purposes:

```python
class RaftProtocol(IProtocol):
    def initialize(self):
        # ... existing initialization code ...
        
        # Schedule failure simulation after 3 seconds
        self.provider.schedule_timer("failure_simulation", 3000)
        
        # Schedule recovery simulation after 7 seconds
        self.provider.schedule_timer("recovery_simulation", 7000)
    
    def handle_timer(self, timer: str):
        if timer == "failure_simulation":
            # Simulate failure of specific nodes
            nodes_to_fail = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            for node_id in nodes_to_fail:
                self.consensus.set_simulation_active(node_id, False)
            print(f"Simulated failure of nodes: {nodes_to_fail}")
        
        elif timer == "recovery_simulation":
            # Simulate recovery of specific nodes
            nodes_to_recover = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            for node_id in nodes_to_recover:
                self.consensus.set_simulation_active(node_id, True)
            print(f"Simulated recovery of nodes: {nodes_to_recover}")
        
        # Forward other timers to consensus
        if self.consensus:
            self.consensus.handle_timer(timer)
    
    def handle_telemetry(self, telemetry: Telemetry) -> None:
        # Visual feedback based on simulation state
        if self.consensus.is_leader():
            self.adapter.paint_node("green", self.node_id)  # Leader = green
        elif self.consensus.is_simulation_active(self.node_id):
            self.adapter.paint_node("blue", self.node_id)   # Active = blue
        else:
            self.adapter.paint_node("red", self.node_id)    # Inactive = red
```

**Key Methods for Failure Simulation:**

- **`set_simulation_active(node_id, True)`**: Mark a node as active in simulation
- **`set_simulation_active(node_id, False)`**: Mark a node as inactive (failed) in simulation
- **`is_simulation_active(node_id)`**: Check if a node is currently active in simulation

**Important Notes:**
-  **Manual Control**: These methods provide manual control over node simulation state
-  **Testing Purposes**: Designed for testing failure scenarios and recovery mechanisms
-  **Visual Feedback**: Use with `paint_node()` for visual debugging
-  **Independent of Heartbeat**: Simulation state is separate from heartbeat-based failure detection
-  **Node-Specific**: Only affects the node if `node_id` matches the current node's ID


## **Consensus Variables**

RaftFault allows you to define and manage consensus variables that will be agreed upon across the cluster. Unlike traditional Raft implementations that focus on log replication, RaftFault is designed for **value consensus** - reaching agreement on specific variables.

### **Creating Consensus Variables**

Before using consensus variables, you must define them in the configuration:

```python
from raft_fault import RaftConfig

        config = RaftConfig()

# Define consensus variables with their types
config.add_consensus_variable("sequence", int)           # Integer variable
config.add_consensus_variable("leader_position", str)    # String variable
config.add_consensus_variable("temperature", float)      # Float variable
config.add_consensus_variable("is_active", bool)         # Boolean variable
config.add_consensus_variable("coordinates", dict)       # Dictionary variable
```

### **Supported Variable Types**

RaftFault supports all Python types that can be JSON serialized:

- **Primitive Types**: `int`, `float`, `str`, `bool`
- **Complex Types**: `dict`, `list`, `tuple`
- **None Values**: `None` is also supported
- **Custom Objects**: Any object that can be JSON serialized

### **Proposing Values (Leader Only)**

Only the current leader can propose new values for consensus variables:

```python
# Check if we're the leader before proposing
if consensus.is_leader():
    # Propose new values
    success = consensus.propose_value("sequence", 42)
    if success:
        print("✅ Value proposed successfully")
    else:
        print("❌ Failed to propose value")
    
    # Propose multiple values
    consensus.propose_value("leader_position", "north")
    consensus.propose_value("temperature", 25.5)
    consensus.propose_value("is_active", True)
    consensus.propose_value("coordinates", {"x": 10, "y": 20, "z": 5})
else:
    print("❌ Not the leader - cannot propose values")
```

### **Retrieving Committed Values**

All nodes (leader and followers) can retrieve committed values:

```python
# Get individual committed values
sequence_value = consensus.get_committed_value("sequence")
position_value = consensus.get_committed_value("leader_position")
temp_value = consensus.get_committed_value("temperature")

print(f"Sequence: {sequence_value}")
print(f"Position: {position_value}")
print(f"Temperature: {temp_value}")

# Handle None values (when variable hasn't been committed yet)
if sequence_value is not None:
    print(f"Sequence is: {sequence_value}")
        else:
    print("Sequence not yet committed")

# Get all committed values at once
all_values = consensus.get_all_committed_values()
print(f"All committed values: {all_values}")
```

### **Complete Example: Consensus Variable Workflow**

```python
from raft_fault import RaftConsensus, RaftConfig, GradysimAdapter

# 1. Configure consensus variables
config = RaftConfig()
config.set_election_timeout(150, 300)
config.set_heartbeat_interval(50)

# Define all variables you want to reach consensus on
config.add_consensus_variable("formation_center", dict)    # Formation center coordinates
config.add_consensus_variable("formation_radius", float)   # Formation radius
config.add_consensus_variable("formation_active", bool)    # Formation status
config.add_consensus_variable("leader_id", int)           # Current leader ID

# 2. Create consensus instance
adapter = GradysimAdapter(provider)
consensus = RaftConsensus(config=config, adapter=adapter)
consensus.set_known_nodes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
consensus.start()

# 3. Leader proposes values
if consensus.is_leader():
    # Propose formation parameters
    consensus.propose_value("formation_center", {"x": 100, "y": 200, "z": 50})
    consensus.propose_value("formation_radius", 25.5)
    consensus.propose_value("formation_active", True)
    consensus.propose_value("leader_id", consensus.get_leader_id())

# 4. All nodes retrieve committed values
formation_center = consensus.get_committed_value("formation_center")
formation_radius = consensus.get_committed_value("formation_radius")
formation_active = consensus.get_committed_value("formation_active")
leader_id = consensus.get_committed_value("leader_id")

print(f"Formation center: {formation_center}")
print(f"Formation radius: {formation_radius}")
print(f"Formation active: {formation_active}")
print(f"Leader ID: {leader_id}")
```

### **Best Practices for Consensus Variables**

#### **1. Variable Naming**
```python
# Use descriptive names
config.add_consensus_variable("formation_center", dict)     # ✅ Good
config.add_consensus_variable("fc", dict)                   # ❌ Avoid

# Use consistent naming conventions
config.add_consensus_variable("leader_position", str)       # ✅ snake_case
config.add_consensus_variable("formation_radius", float)    # ✅ snake_case
```

#### **2. Type Safety**
```python
# Always specify the correct type
config.add_consensus_variable("count", int)                 # ✅ Correct type
config.add_consensus_variable("count", str)                 # ❌ Wrong type

# Use appropriate types for your data
config.add_consensus_variable("coordinates", dict)          # ✅ Complex data
config.add_consensus_variable("is_enabled", bool)           # ✅ Boolean flag
```

#### **3. Error Handling**
```python
# Always check if consensus is ready
if not consensus.is_ready():
    print("❌ Consensus not ready")
    return

# Check if we're the leader before proposing
if not consensus.is_leader():
    print("❌ Not the leader - cannot propose")
    return

# Handle proposal failures
success = consensus.propose_value("sequence", 42)
if not success:
    print("❌ Failed to propose value - no quorum or not leader")

# Handle None values when retrieving
value = consensus.get_committed_value("sequence")
if value is None:
    print("⚠️ Variable not yet committed")
else:
    print(f"✅ Value: {value}")
```

#### **4. Performance Considerations**
```python
# Don't propose values too frequently
# Wait for previous proposals to be committed
if consensus.is_leader():
    # Check if previous value was committed
    current_value = consensus.get_committed_value("sequence")
    if current_value is not None:
        # Propose new value
        consensus.propose_value("sequence", current_value + 1)

# Use appropriate variable types for your use case
config.add_consensus_variable("large_data", dict)           # ✅ For complex data
config.add_consensus_variable("simple_flag", bool)          # ✅ For simple flags
```

### **Common Use Cases**

#### **Formation Control**
```python
config.add_consensus_variable("formation_center", dict)
config.add_consensus_variable("formation_radius", float)
config.add_consensus_variable("formation_active", bool)

# Leader proposes formation parameters
if consensus.is_leader():
    consensus.propose_value("formation_center", {"x": 100, "y": 200})
    consensus.propose_value("formation_radius", 25.0)
    consensus.propose_value("formation_active", True)
```

#### **Leader Election Tracking**
```python
config.add_consensus_variable("current_leader", int)
config.add_consensus_variable("leader_term", int)

# Leader updates its information
if consensus.is_leader():
    consensus.propose_value("current_leader", consensus.get_leader_id())
    consensus.propose_value("leader_term", consensus.get_current_term())
```

#### **System State Management**
```python
config.add_consensus_variable("system_mode", str)
config.add_consensus_variable("active_nodes_count", int)
config.add_consensus_variable("last_update_time", float)

# Leader proposes system state
if consensus.is_leader():
    consensus.propose_value("system_mode", "formation")
    consensus.propose_value("active_nodes_count", len(active_nodes))
    consensus.propose_value("last_update_time", time.time())
```

## **Active Node Discovery**

### **How It Works (Fault-Tolerant Mode)**

1. **Election Timeout**: When a node's election timeout expires
2. **Discovery Phase**: Node sends `DiscoveryHeartbeat` to all known nodes
3. **Response Collection**: Waits for `DiscoveryHeartbeatResponse` messages
4. **Active Count Calculation**: Counts responses + self = discovered active nodes
5. **Election with Correct Threshold**: Uses discovered count for majority calculation

### **Discovery Process**

```python
# 1. Election timeout triggers discovery
def _handle_election_timeout(self):
    if self.config.is_fault_tolerant_mode():
        self._discover_active_nodes_before_election()
    else:
        self._start_election()  # Direct election in classic mode

# 2. Send discovery heartbeats
def _discover_active_nodes_before_election(self):
    message = DiscoveryHeartbeat(self.current_term, self.node_id)
    for node_id in self._known_nodes:
        if node_id != self.node_id:
            self._send_message(message.to_json(), node_id)

# 3. Collect responses
def _handle_discovery_heartbeat_response(self, message, sender_id):
    self._discovery_responses.add(sender_id)

# 4. Start election with discovered count
def _start_election_with_discovered_count(self):
    discovered_active = len(self._discovery_responses) + 1
    majority_needed = (discovered_active // 2) + 1
    # Proceed with election using correct threshold
```

### **Active Node Information Sharing**

In Fault-Tolerant mode, the leader shares active node information with followers:

```python
# Leader includes active nodes list in AppendEntries
def _send_append_entries(self):
    active_nodes_list = list(self._get_active_nodes_for_majority())
    message = AppendEntries(
        term=self.current_term,
        leader_id=self.node_id,
        active_nodes_list=active_nodes_list  # Share active nodes
    )
    self._send_broadcast(message.to_json())

# Followers store the information
def _handle_append_entries(self, message, sender_id):
    if message.active_nodes_list:
        self._known_active_nodes_list = set(message.active_nodes_list)
        self._last_active_nodes_list_update = self._get_current_time()
```

## **Failure Detection**

### **Heartbeat-Based Detection**

RaftFault includes a failure detection system:

```python
from raft_fault.failure_detection import HeartbeatDetector, FailureConfig

# Configure failure detection
failure_config = FailureConfig()
failure_config.set_failure_threshold(3)      # 3 consecutive failures
failure_config.set_recovery_threshold(2)     # 2 consecutive successes
failure_config.set_detection_interval(2)     # Check every 2 heartbeats
failure_config.set_timeout_ms(120)           # 120ms timeout


```

### **Failure Detection Features**

- **Configurable Thresholds**: Adjust failure and recovery sensitivity
- **Callback Notifications**: Get notified of failures and recoveries
- **Performance Metrics**: Track detection latency and success rates
- **Automatic Integration**: Works seamlessly with Raft consensus
- **Node Failure Simulation**: Methods to simulate nodes as failed or inactive for testing purposes

## **Project Structure**

RaftFault is organized as a clean, modular Python package with clear separation of concerns. Here's the complete project structure:

```
RaftFault/
├── README.md                    # Project documentation
├── LICENSE.txt                  # MIT License
├── main.py                      # Example: GradySim simulation setup with RaftFault
├── protocol.py                  # Example: RaftFault protocol implementation for GradySim
├── requirements.txt             # Python dependencies
├── activate_env.bat             # Windows environment activation script
├── activate_env.sh              # Linux/macOS environment activation script
├── .gitignore                   # Git ignore rules
├── .gitattributes               # Git attributes for line ending normalization
├── raft_fault/                  # Main RaftFault package
│   ├── __init__.py             # Package exports and version
│   ├── raft_node.py            # Core Raft algorithm implementation
│   ├── raft_consensus.py       # Public facade for consensus operations
│   ├── raft_message.py         # Raft message classes and serialization
│   ├── raft_config.py          # Configuration management
│   ├── raft_state.py           # Raft state enums and constants
│   ├── adapters/               # Platform integration adapters
│   │   ├── __init__.py         # Adapter exports
│   │   ├── gradysim_adapter.py # GradySim platform adapter
│   │   └── README.md           # Adapter documentation
│   └── failure_detection/      # Failure detection system
│       ├── __init__.py         # Failure detection exports
│       ├── heartbeat_detector.py # Heartbeat-based failure detection
│       ├── failure_config.py   # Failure detection configuration
│       └── failure_state.py    # Failure state management
```
```

### **Core Components**

#### **📁 Root Level Files**

##### **📖 Documentation & Configuration**
- **`README.md`**: Comprehensive project documentation
- **`LICENSE.txt`**: MIT License for open source distribution
- **`requirements.txt`**: Python dependencies (gradysim only)
- **`activate_env.bat`**: Windows environment activation script
- **`activate_env.sh`**: Linux/macOS environment activation script

##### **🔧 Git Configuration**
- **`.gitignore`**: Git ignore rules for Python projects
- **`.gitattributes`**: Git attributes for line ending normalization across platforms

##### **🎯 Example Usage Files**
- **`main.py`**: **Complete example** of how to use RaftFault with GradySim
  - Sets up a GradySim simulation with 40 nodes
  - Demonstrates node positioning and cluster configuration
  - Shows how to integrate RaftFault with GradySim simulation framework
  - **Perfect starting point** for understanding RaftFault + GradySim integration

- **`protocol.py`**: **RaftFault protocol implementation** for GradySim
  - Implements the `RaftProtocol` class that extends GradySim's `IProtocol`
  - Shows how to create and configure RaftFault consensus
  - Demonstrates failure simulation and recovery scenarios
  - **Reference implementation** for building your own RaftFault protocols

#### **📁 `raft_fault/` - Main Package**

##### **Core Raft Implementation**
- **`raft_node.py`** (65KB): Complete Raft algorithm implementation
  - Leader election logic
  - Consensus value management
  - Active node discovery
  - State machine transitions
  - Message handling

- **`raft_consensus.py`** (27KB): Public API facade
  - User-friendly interface
  - High-level consensus operations
  - Error handling and validation
  - Integration with adapters

- **`raft_message.py`** (12KB): Message system
  - Raft message classes (RequestVote, AppendEntries, etc.)
  - JSON serialization/deserialization
  - Message validation and parsing

- **`raft_config.py`** (11KB): Configuration management
  - Raft mode selection (Classic/Fault-Tolerant)
  - Timeout and interval settings
  - Consensus variable definitions
  - Failure detection configuration

- **`raft_state.py`** (1.8KB): State definitions
  - RaftState enum (FOLLOWER, CANDIDATE, LEADER)
  - RaftMode enum (CLASSIC, FAULT_TOLERANT)
  - Constants and type definitions

##### **Platform Integration**
- **`adapters/`**: Platform-specific integration
  - **`gradysim_adapter.py`**: GradySim simulation framework adapter
  - **`README.md`**: Adapter documentation and usage guide
  - Callback-based architecture for platform independence

##### **Failure Detection System**
- **`failure_detection/`**: Heartbeat-based failure detection
  - **`heartbeat_detector.py`**: Core failure detection logic
  - **`failure_config.py`**: Failure detection configuration
  - **`failure_state.py`**: Failure state management and tracking
  - Automatic integration with Raft consensus

### **File Size Distribution**

| Component               | Size | Purpose                       |
|-------------------------|------|-------------------------------|
| `raft_node.py`          | 65KB | Core Raft implementation      |
| `raft_consensus.py`     | 27KB | Public API facade             |
| `raft_message.py`       | 12KB | Message system                |
| `raft_config.py`        | 11KB | Configuration management      |
| `README.md`             | 43KB | Documentation                 |
| `gradysim_adapter.py`   | ~8KB | Platform adapter              |
| `heartbeat_detector.py` | ~6KB | Failure detection             |
| `requirements.txt`      | ~1KB | Dependencies                  |
| `activate_env.bat`      | ~1KB | Windows activation script     |
| `activate_env.sh`       | ~1KB | Linux/macOS activation script |

### **Architecture Principles**

#### **Modular Design**
- **Separation of Concerns**: Each file has a specific responsibility
- **Clean Interfaces**: Well-defined APIs between components
- **Loose Coupling**: Components interact through interfaces, not direct dependencies

#### **Package Organization**
- **Public API**: `raft_consensus.py` provides the main interface
- **Core Logic**: `raft_node.py` contains the Raft algorithm
- **Configuration**: `raft_config.py` manages all settings
- **Platform Integration**: `adapters/` handles different platforms
- **Failure Detection**: `failure_detection/` provides fault tolerance

#### **Import Structure**
```python
# Main package exports
from raft_fault import RaftConsensus, RaftConfig, RaftMode, GradysimAdapter

# Core components (internal use)
from raft_fault.raft_node import RaftNode
from raft_fault.raft_message import RequestVote, AppendEntries
from raft_fault.failure_detection import HeartbeatDetector
```

### **Development Guidelines**

#### **Adding New Features**
1. **Core Logic**: Add to `raft_node.py` for algorithm changes
2. **Public API**: Extend `raft_consensus.py` for new user features
3. **Configuration**: Update `raft_config.py` for new settings
4. **Messages**: Add to `raft_message.py` for new message types
5. **Adapters**: Create new adapter in `adapters/` for new platforms

#### ** Code Organization**
- **Single Responsibility**: Each file has one clear purpose
- **Consistent Naming**: Follow Python naming conventions
- **Documentation**: All public APIs are documented
- **Type Hints**: Used throughout for better IDE support

#### ** Testing Strategy**
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **Platform Tests**: Test with different adapters
- **Performance Tests**: Measure consensus performance

This structure provides a solid foundation for the RaftFault consensus system while maintaining clarity and extensibility for future development.

## **Architecture**

### **Component Overview**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RaftConsensus │    │    RaftNode     │    │  GradySimAdapter│
│   (Facade)      │◄──►│   (Core Logic)  │◄──►│   (Platform)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RaftConfig    │    │HeartbeatDetector│    │   GradySim      │
│   (Settings)    │    │   (Internal)    │    │   (Simulation)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Component Relationships:**
- **RaftConsensus**: Public facade for consensus operations
- **RaftNode**: Core Raft algorithm implementation
- **GradySimAdapter**: Platform integration layer
- **RaftConfig**: Configuration and settings management
- **HeartbeatDetector**: Internal failure detection (Fault-Tolerant mode only)
- **GradySim**: Simulation framework

### **Callback Pattern**

The system uses callbacks for platform independence:

```python
# Adapter provides callbacks
callbacks = {
    'send_message_callback': adapter.send_message,
    'send_broadcast_callback': adapter.send_broadcast,
    'schedule_timer_callback': adapter.schedule_timer,
    'cancel_timer_callback': adapter.cancel_timer,
    'get_current_time_callback': adapter.get_current_time,
    'get_node_id_callback': adapter.get_node_id,
    'get_node_position_callback': adapter.get_node_position
}

# Raft uses callbacks without knowing the platform
raft_node = RaftNode(node_id=1, config=config, callbacks=callbacks)
```

### **Message Flow**

1. **Consensus Request**: `RaftConsensus.propose_value()`
2. **Internal Processing**: `RaftNode` processes the request
3. **Platform Communication**: Uses callbacks to send messages
4. **Response Handling**: Processes responses via callbacks
5. **State Update**: Updates consensus state and notifies callers

## **API Reference**

### **Core Classes**

#### **RaftConsensus**
Main facade for consensus operations.

```python
# Initialization
consensus = RaftConsensus(config=config, adapter=adapter)

# Basic operations
consensus.start()                                    # Start consensus
consensus.stop()                                     # Stop consensus
consensus.propose_value("var", value)               # Propose value (leader only)
consensus.get_committed_value("var")                # Get committed value
consensus.is_leader()                               # Check if leader
consensus.get_leader_id()                           # Get current leader ID

# Active node information (Fault-Tolerant mode)
consensus.get_active_nodes_info()                   # Get detailed active node info
consensus.has_quorum()                              # Check if cluster has quorum
consensus.get_majority_info()                       # Get majority calculation info

# Node management
consensus.set_known_nodes([1, 2, 3, 4, 5])         # Set known nodes
consensus.get_failed_nodes()                        # Get failed nodes
consensus.get_active_nodes()                        # Get active nodes
consensus.set_simulation_active(node_id, True)     # Set node as active in simulation
consensus.set_simulation_active(node_id, False)    # Set node as inactive in simulation
consensus.is_simulation_active(node_id)            # Check if node is active in simulation
```

#### **RaftConfig**
Configuration management for consensus behavior.

```python
# Basic configuration
config = RaftConfig()
config.set_election_timeout(150, 300)              # Set election timeout range
config.set_heartbeat_interval(50)                  # Set heartbeat interval
config.add_consensus_variable("var", int)          # Add consensus variable

# Mode configuration
config.set_raft_mode(RaftMode.FAULT_TOLERANT)      # Set operation mode
config.is_classic_mode()                           # Check if classic mode
config.is_fault_tolerant_mode()                    # Check if fault-tolerant mode
config.get_raft_mode()                             # Get current mode

# Failure detection (automatically enabled in Fault-Tolerant mode)
failure_config.set_failure_threshold(2)      # 2 failed heartbeats to mark as failed
failure_config.set_recovery_threshold(3)     # 3 successful heartbeats to recover
failure_config.set_detection_interval(2)     # Check every 2 heartbeats
failure_config.set_heartbeat_timeout(4)      # 4× heartbeat_interval = 200ms timeout
```

#### **GradySimAdapter**
Platform adapter for GradySim integration.

```python
# Initialization
adapter = GradysimAdapter(provider)

# Communication
adapter.send_message(message, target_id)           # Send point-to-point message
adapter.send_broadcast(message)                    # Send broadcast message

# Timing
adapter.schedule_timer(timer_name, delay_ms)       # Schedule timer
adapter.cancel_timer(timer_name)                   # Cancel timer
adapter.get_current_time()                         # Get current time

# Node information
adapter.get_node_id()                              # Get current node ID
adapter.get_node_position(telemetry)               # Get node position

# Visualization
adapter.paint_node(color, node_id)                 # Paint node for debugging

# Callbacks
callbacks = adapter.get_callbacks()                # Get all callbacks
```

### **Enums and Constants**

#### **RaftMode**
```python
RaftMode.CLASSIC           # Classic Raft behavior
RaftMode.FAULT_TOLERANT    # Fault-tolerant behavior (default)
```

#### **RaftState**
```python
RaftState.FOLLOWER         # Follower state
RaftState.CANDIDATE        # Candidate state
RaftState.LEADER           # Leader state
```

### **Message Classes**

RaftFault uses internal message classes for communication between nodes. **These messages are completely transparent to users** and are handled automatically by the system based on the configured operation mode.

```python
# Election messages (used in both modes)
RequestVote(term, candidate_id, last_log_index, last_log_term)
RequestVoteResponse(term, vote_granted)

# Consensus messages (used in both modes)
AppendEntries(term, leader_id, prev_log_index, prev_log_term, entries, leader_commit)
AppendEntriesResponse(term, success)

# Discovery messages (used only in Fault-Tolerant mode)
DiscoveryHeartbeat(term, node_id)
DiscoveryHeartbeatResponse(term, node_id, is_active)
```

**Important Notes:**
-  **Transparent to Users**: You never need to create or handle these messages directly
-  **Automatic Handling**: The system automatically sends and processes messages based on the current mode
-  **Mode-Aware**: In Classic mode, discovery messages are not used
-  **Internal Implementation**: These are implementation details, not part of the public API
-  **JSON Serialization**: Messages are automatically serialized/deserialized for network transmission

**Example of Automatic Message Handling:**
```python
# User only needs to configure and use the consensus API
config = RaftConfig()
config.set_raft_mode(RaftMode.FAULT_TOLERANT)  # System automatically uses discovery messages
consensus = RaftConsensus(config=config, adapter=adapter)

# The system automatically handles all message types internally
consensus.start()  # Discovery messages sent automatically in Fault-Tolerant mode
consensus.propose_value("var", 42)  # Consensus messages handled automatically
```

## **Best Practices**

### **Configuration Guidelines**

#### **Election Timeouts**
```python
# For stable networks
config.set_election_timeout(150, 300)    # 150-300ms

# For unstable networks
config.set_election_timeout(200, 400)    # 200-400ms

# For very unstable networks
config.set_election_timeout(300, 600)    # 300-600ms
```

#### **Heartbeat Intervals**
```python
# Standard interval
config.set_heartbeat_interval(50)        # 50ms

# For high-frequency updates
config.set_heartbeat_interval(25)        # 25ms

# For low-frequency updates
config.set_heartbeat_interval(100)       # 100ms
```

#### **Failure Detection**
```python
# Get failure detection configuration
failure_config = config.get_failure_config()

# Threshold Configuration
failure_config.set_failure_threshold(3)      # 3 consecutive failures to mark as failed
failure_config.set_recovery_threshold(2)     # 2 consecutive successes to recover
failure_config.set_detection_interval(2)     # Check every 2 heartbeats

# Timeout Configuration (Two Options)

# Option 1: Relative timeout (multiplier of heartbeat_interval)
failure_config.set_heartbeat_timeout(4)      # 4× heartbeat_interval = 200ms timeout

# Option 2: Absolute timeout (independent of heartbeat_interval)
failure_config.set_absolute_timeout(150)     # 150ms absolute timeout

# Conservative Detection (High reliability, slower detection)
failure_config.set_failure_threshold(5)      # 5 consecutive failures
failure_config.set_recovery_threshold(3)     # 3 consecutive successes
failure_config.set_detection_interval(3)     # Check every 3 heartbeats
failure_config.set_heartbeat_timeout(6)      # 6× heartbeat_interval = 300ms timeout

# Aggressive Detection (Fast detection, may have false positives)
failure_config.set_failure_threshold(2)      # 2 consecutive failures
failure_config.set_recovery_threshold(1)     # 1 consecutive success
failure_config.set_detection_interval(1)     # Check every heartbeat
failure_config.set_absolute_timeout(100)     # 100ms absolute timeout

# Balanced Detection (Recommended default)
failure_config.set_failure_threshold(3)      # 3 consecutive failures
failure_config.set_recovery_threshold(2)     # 2 consecutive successes
failure_config.set_detection_interval(2)     # Check every 2 heartbeats
failure_config.set_heartbeat_timeout(4)      # 4× heartbeat_interval = 200ms timeout

# Timeout Configuration Details:
# - set_heartbeat_timeout(multiplier): Timeout = multiplier × heartbeat_interval
# - set_absolute_timeout(ms): Fixed timeout independent of heartbeat_interval
# - Only one timeout method can be active at a time
# - Minimum recommended timeout: 100ms to avoid false positives
```

### **Mode Selection**

#### **Use Classic Mode When:**
- Cluster size is fixed and known
- Performance is critical
- Standard Raft behavior is required
- Manual failure management is acceptable

#### **Use Fault-Tolerant Mode When:**
- Nodes may fail unexpectedly
- Automatic fault recovery is needed
- Cluster size varies dynamically
- High availability is required
- Active node information is needed

### **Error Handling**

```python
# Always check if consensus is ready
if consensus.is_ready():
    # Proceed with operations
    pass

# Handle leader-only operations
if consensus.is_leader():
    success = consensus.propose_value("var", value)
    if not success:
        print("Failed to propose value")

# Check quorum before critical operations
if consensus.has_quorum():
    # Proceed with critical operation
    pass
else:
    print("No quorum available")
```

### **Performance Optimization**

```python
# Use appropriate timeouts for your network
config.set_election_timeout(150, 300)    # Match network characteristics

# Failure detection is automatically enabled in Fault-Tolerant mode
# No need to explicitly enable it

# Use broadcast when possible
adapter.send_broadcast(message)          # More efficient than multiple sends

# Monitor active nodes in fault-tolerant mode
active_info = consensus.get_active_nodes_info()
print(f"Active nodes: {len(active_info['active_nodes'])}")
```

## **Troubleshooting**

### **⚠️ Known Issue: Fault Tolerance Communication Range**

**Important Warning**: When RaftFault is operating in **Fault-Tolerant Mode** (`RaftMode.FAULT_TOLERANT`) and the communication range is not large enough to reach all nodes in the swarm, the system may not converge to stability and consecutive elections may be triggered repeatedly.

**Problem Description:**
- In Fault-Tolerant mode, nodes perform active node discovery before elections
- When communication range is limited, the network may form multiple disconnected clusters
- **Edge nodes** that can be reached by multiple clusters simultaneously become a critical issue
- These edge nodes may receive conflicting election requests from different clusters
- This leads to incorrect majority calculations and failed leader elections
- The system may enter a cycle of repeated elections without reaching consensus
- **Most likely cause**: Edge nodes being simultaneously accessible by multiple clusters, creating conflicting consensus states

**Current Status:**
This is an **open research problem** for which a complete solution is not yet known. The issue occurs in distributed systems where:
- Nodes have limited communication range
- The network topology creates disconnected components
- The consensus algorithm requires global knowledge for proper operation

**Impact:**
- ❌ System may not converge to a stable leader
- ❌ Consecutive election cycles may occur
- ❌ Consensus values may not be committed
- ❌ Performance degradation due to constant re-elections

**Workarounds:**
1. **Increase Communication Range**: Ensure all nodes can communicate with each other
2. **Use Classic Mode**: Switch to `RaftMode.CLASSIC` for scenarios with limited communication range
3. **Network Topology Design**: Design network topology to ensure full connectivity

**Call for Contributions:**
This remains an **open research challenge** in distributed consensus algorithms. We invite researchers and developers to:

-  **Research Solutions**: Investigate novel approaches to consensus in limited-range networks
-  **Propose Algorithms**: Develop new consensus algorithms for disconnected networks
-  **Test Scenarios**: Create test cases and benchmarks for this problem
-  **Document Solutions**: Share findings and potential solutions
-  **Collaborate**: Work together to find a robust solution

**Contact for Contributions:**
If you have ideas, solutions, or want to contribute to solving this problem, please contact:
- **Email**: [llucchesi@inf.puc-rio.br](mailto:llucchesi@inf.puc-rio.br)
- **Subject**: "RaftFault - Fault Tolerance Communication Range Issue"

### **Common Issues**

#### **1. No Leader Elected**
```python
# Check if nodes are properly configured
print(f"Known nodes: {consensus.get_known_nodes()}")
print(f"Active nodes: {consensus.get_active_nodes()}")

# Check election timeouts
config = consensus.get_configuration()
print(f"Election timeout: {config['election_timeout']}")

# Check if cluster has quorum
if consensus.has_quorum():
    print("Cluster has quorum")
else:
    print("Cluster lacks quorum - add more nodes")
```

#### **2. Values Not Committing**
```python
# Check if we're the leader
if not consensus.is_leader():
    print("Not the leader - cannot propose values")

# Check if we have quorum
if not consensus.has_quorum():
    print("No quorum - cannot commit values")

# Check consensus variables
variables = consensus.get_consensus_variables()
print(f"Available variables: {list(variables.keys())}")
```

#### **3. High Election Frequency**
```python
# Increase election timeout
config.set_election_timeout(300, 600)    # Longer timeouts

# Increase heartbeat frequency
config.set_heartbeat_interval(25)        # More frequent heartbeats

# Check network stability
failed_nodes = consensus.get_failed_nodes()
print(f"Failed nodes: {failed_nodes}")
```

#### **4. Performance Issues**
```python
# Check active node count
active_info = consensus.get_active_nodes_info()
print(f"Active nodes: {len(active_info['active_nodes'])}")

# Check failure detection metrics
metrics = consensus.get_failure_detection_metrics()
print(f"Detection latency: {metrics['detection_latency_ms']}ms")

# Consider switching to classic mode for better performance
config.set_raft_mode(RaftMode.CLASSIC)
```

### **Debugging Tips**

#### **Enable Logging**
```python
config = RaftConfig()
config.enable_logging(True)
config.set_log_level("DEBUG")
```

#### **Monitor Node States**
```python
# Get detailed state information
state_info = consensus.get_state_info()
print(f"Current state: {state_info['state']}")
print(f"Current term: {state_info['current_term']}")
print(f"Leader ID: {state_info['leader_id']}")
```

#### **Check Network Connectivity**
```python
# In fault-tolerant mode, check active nodes
active_info = consensus.get_active_nodes_info()
print(f"Active nodes: {active_info['active_nodes']}")
print(f"Failed nodes: {active_info['failed_nodes']}")

# Check majority calculation
majority_info = consensus.get_majority_info()
print(f"Majority needed: {majority_info['majority_needed']}")
print(f"Has majority: {majority_info['has_majority']}")
```

### **Performance Monitoring**

```python
# Get consensus statistics
stats = consensus.get_statistics()
print(f"Proposals made: {stats['proposals_made']}")
print(f"Values committed: {stats['values_committed']}")
print(f"Election attempts: {stats['election_attempts']}")

# Get failure detection metrics
metrics = consensus.get_failure_detection_metrics()
print(f"Detection latency: {metrics['detection_latency_ms']}ms")
print(f"Success rate: {metrics['success_rate_percent']}%")
```

## **Version Information**

- **Current Version**: 0.1.0
- **Python Compatibility**: 3.7+
- **GradySim Compatibility**: 0.7.3+
- **License**: MIT License

## **Contributing**

Contributions are welcome! We appreciate any help in improving RaftFault. Here's how you can contribute:

### **How to Contribute**

#### **1. Fork the Repository**
1. Go to the [RaftFault repository](https://github.com/Project-GrADyS/RaftFault)
2. Click the "Fork" button in the top-right corner
3. This creates a copy of the repository in your GitHub account

#### **2. Clone Your Fork**
```bash
git clone https://github.com/your-username/RaftFault.git
cd RaftFault
```

#### **3. Set Up Development Environment**
```bash
# Create and activate virtual environment
python -m venv raft_env
source raft_env/bin/activate  # On Windows: raft_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **4. Create a Feature Branch**
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

#### **5. Make Your Changes**
- Write your code following the existing style
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

#### **6. Test Your Changes**
```bash
# Run the example
python main.py

# If you have tests, run them
python -m pytest tests/
```

#### **7. Commit Your Changes**
```bash
git add .
git commit -m "Add descriptive commit message"
```

#### **8. Push to Your Fork**
```bash
git push origin feature/your-feature-name
```

#### **9. Create a Pull Request**
1. Go to your fork on GitHub
2. Click "Compare & pull request" for your branch
3. Fill in the pull request template:
   - **Title**: Brief description of changes
   - **Description**: Detailed explanation of what was changed and why
   - **Type**: Bug fix, Feature, Documentation, etc.
   - **Testing**: How you tested your changes

### **Contribution Guidelines**

#### **Code Style**
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

#### **Documentation**
- Update README.md if you add new features
- Add docstrings to new functions and classes
- Include usage examples for new functionality

#### **Testing**
- Add tests for new features
- Ensure existing tests still pass
- Test edge cases and error conditions

#### **Pull Request Process**
1. **Small Changes**: Keep pull requests focused on a single feature or fix
2. **Clear Description**: Explain what was changed and why
3. **Reference Issues**: Link to any related issues or discussions
4. **Screenshots**: Include screenshots for UI changes if applicable

### **Areas for Contribution**

#### **High Priority**
-  **Research Solutions**: Investigate the fault tolerance communication range issue
-  **Test Scenarios**: Create comprehensive test cases
-  **Performance Optimization**: Improve consensus performance
-  **Bug Fixes**: Fix any issues you encounter

#### **Medium Priority**
-  **Documentation**: Improve existing documentation
-  **Code Refactoring**: Improve code structure and readability
-  **Platform Support**: Add support for other simulation platforms
-  **Monitoring**: Add better monitoring and debugging tools

#### **Low Priority**
-  **UI Improvements**: Enhance visualization features
-  **Examples**: Create additional usage examples
-  **Code Analysis**: Improve code quality and coverage

### **Getting Help**

If you need help with your contribution:
- Open an issue to discuss your idea
- Ask questions in the issue comments
- Contact the maintainer: [llucchesi@inf.puc-rio.br](mailto:llucchesi@inf.puc-rio.br)

### **Code of Conduct**

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's coding standards

## **Contact**

For questions, suggestions, or collaboration opportunities, please contact the project author:

- **Author**: Laércio Lucchesi
- **Laboratory**: LAC - Laboratory for Advanced Collaboration 
- **Department**: Computer Science
- **University**: PUC-Rio / Pontifical Catholic University of Rio de Janeiro
- **Location**: Rio de Janeiro - RJ - Brazil
- **Email**: [llucchesi@inf.puc-rio.br](mailto:llucchesi@inf.puc-rio.br)



## **License**

This project is licensed under the MIT License - see the LICENSE file for details.