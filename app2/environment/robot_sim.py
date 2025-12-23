import gymnasium as gym
import pybullet as pb
import numpy as np
from gymnasium import spaces
from typing import Any, Dict, Optional, Tuple, Union

class RobotSimEnv(gym.Env):
    """
    PyBullet-based robot simulation environment following gymnasium.Env interface.
    
    Parameters:
        config (dict): Configuration dictionary containing:
            - "simulation": {
                  "render_mode": "human" for GUI or "headless" (default)
                  "timestep": Physics simulation timestep (default=1/240)
              }
            - "robot": {
                  "urdf_path": Path to robot URDF file
                  "base_position": [x, y, z] (default=[0,0,0])
                  "base_orientation": [x,y,z,w] quaternion (default=[0,0,0,1])
              }
            - "domain_randomization": {
                  "enable": True/False (default=False)
                  "friction_range": [min, max] (default=[0.5,1.5])
                  "mass_range": [min, max] (default=[0.8,1.2])
              }
            - "safety": {
                  "joint_limits": True/False (default=True)
                  "max_episode_steps": Maximum steps per episode (default=1000)
              }
            - "observation_space": gym.Space definition
            - "action_space": gym.Space definition
    """
    
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 60}
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.sim_config = config.get("simulation", {})
        self.robot_config = config.get("robot", {})
        self.dr_config = config.get("domain_randomization", {})
        self.safety_config = config.get("safety", {})
        
        # Initialize simulation
        self.render_mode = self.sim_config.get("render_mode", "headless")
        self.physics_client = self._init_simulation()
        self.timestep = self.sim_config.get("timestep", 1/240)
        pb.setTimeStep(self.timestep, self.physics_client)
        
        # Load robot
        self.robot_id = self._load_robot()
        self._setup_joints()
        
        # Initialize spaces
        self.action_space = config.get("action_space", self._default_action_space())
        self.observation_space = config.get("observation_space", self._default_observation_space())
        
        # Safety and episode management
        self.max_episode_steps = self.safety_config.get("max_episode_steps", 1000)
        self.step_count = 0
        self._safety_enabled = self.safety_config.get("joint_limits", True)
        
        # Domain randomization
        self._dr_enabled = self.dr_config.get("enable", False)
        self._randomize_environment()

    def _init_simulation(self) -> int:
        """Initialize PyBullet physics client."""
        if self.render_mode == "human":
            client = pb.connect(pb.GUI)
            pb.configureDebugVisualizer(pb.COV_ENABLE_GUI, 0)
        else:
            client = pb.connect(pb.DIRECT)
        pb.setGravity(0, 0, -9.8, physicsClientId=client)
        pb.setAdditionalSearchPath(pybullet_data.getDataPath())
        return client

    def _load_robot(self) -> int:
        """Load robot URDF into simulation."""
        urdf_path = self.robot_config["urdf_path"]
        base_pos = self.robot_config.get("base_position", [0, 0, 0])
        base_orn = self.robot_config.get("base_orientation", [0, 0, 0, 1])
        return pb.loadURDF(
            urdf_path,
            basePosition=base_pos,
            baseOrientation=base_orn,
            useFixedBase=True,
            physicsClientId=self.physics_client
        )

    def _setup_joints(self):
        """Identify controllable joints and their properties."""
        num_joints = pb.getNumJoints(self.robot_id, self.physics_client)
        self.controllable_joints = []
        self.joint_limits = []
        
        for i in range(num_joints):
            joint_info = pb.getJointInfo(self.robot_id, i, self.physics_client)
            if joint_info[2] in [pb.JOINT_REVOLUTE, pb.JOINT_PRISMATIC]:
                self.controllable_joints.append(i)
                self.joint_limits.append((joint_info[8], joint_info[9]))
        
        self.num_controllable_joints = len(self.controllable_joints)

    def _default_action_space(self) -> spaces.Box:
        """Create default action space if not provided in config."""
        return spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.num_controllable_joints,),
            dtype=np.float32
        )

    def _default_observation_space(self) -> spaces.Box:
        """Create default observation space (joint positions + velocities)."""
        low = np.array([lim[0] for lim in self.joint_limits] + 
                       [-np.inf] * self.num_controllable_joints, dtype=np.float32)
        high = np.array([lim[1] for lim in self.joint_limits] + 
                        [np.inf] * self.num_controllable_joints, dtype=np.float32)
        return spaces.Box(low=low, high=high, dtype=np.float32)

    def _randomize_environment(self):
        """Apply domain randomization if enabled."""
        if not self._dr_enabled:
            return
            
        friction_range = self.dr_config.get("friction_range", [0.5, 1.5])
        mass_range = self.dr_config.get("mass_range", [0.8, 1.2])
        
        # Randomize friction
        for joint_index in self.controllable_joints:
            pb.changeDynamics(
                self.robot_id,
                joint_index,
                lateralFriction=np.random.uniform(*friction_range),
                physicsClientId=self.physics_client
            )
        
        # Randomize masses
        for link_index in range(-1, pb.getNumJoints(self.robot_id, self.physics_client)):
            mass = pb.getDynamicsInfo(self.robot_id, link_index, self.physics_client)[0]
            new_mass = mass * np.random.uniform(*mass_range)
            pb.changeDynamics(
                self.robot_id,
                link_index,
                mass=new_mass,
                physicsClientId=self.physics_client
            )

    def _get_obs(self) -> np.ndarray:
        """Retrieve current observation (joint states)."""
        joint_states = pb.getJointStates(
            self.robot_id,
            self.controllable_joints,
            physicsClientId=self.physics_client
        )
        positions = [state[0] for state in joint_states]
        velocities = [state[1] for state in joint_states]
        return np.concatenate([positions, velocities]).astype(np.float32)

    def _check_safety(self) -> Tuple[bool, bool]:
        """Check safety constraints and termination conditions."""
        terminated = False
        truncated = False
        
        # Joint limit violation
        if self._safety_enabled:
            joint_states = pb.getJointStates(
                self.robot_id,
                self.controllable_joints,
                physicsClientId=self.physics_client
            )
            positions = [state[0] for state in joint_states]
            for pos, (low, high) in zip(positions, self.joint_limits):
                if pos <= low or pos >= high:
                    terminated = True
                    break
        
        # Max episode steps
        self.step_count += 1
        if self.step_count >= self.max_episode_steps:
            truncated = True
            
        return terminated, truncated

    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None
             ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        pb.resetSimulation(self.physics_client)
        self.robot_id = self._load_robot()
        self._setup_joints()
        self._randomize_environment()
        self.step_count = 0
        
        # Reset robot to initial configuration
        for joint_index in self.controllable_joints:
            pb.resetJointState(
                self.robot_id,
                joint_index,
                targetValue=0,
                targetVelocity=0,
                physicsClientId=self.physics_client
            )
        
        return self._get_obs(), {}

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one timestep of the environment."""
        # Apply control action
        pb.setJointMotorControlArray(
            self.robot_id,
            self.controllable_joints,
            pb.TORQUE_CONTROL,
            forces=action,
            physicsClientId=self.physics_client
        )
        
        # Step simulation
        pb.stepSimulation(self.physics_client)
        
        # Get observation
        obs = self._get_obs()
        
        # Check safety constraints
        terminated, truncated = self._check_safety()
        
        # Placeholder reward
        reward = 0.0
        
        return obs, reward, terminated, truncated, {}

    def render(self) -> Optional[np.ndarray]:
        """Render the environment."""
        if self.render_mode == "rgb_array":
            width, height = 640, 480
            view_matrix = pb.computeViewMatrix([2, 2, 2], [0, 0, 0], [0, 0, 1])
            proj_matrix = pb.computeProjectionMatrixFOV(60, width/height, 0.1, 10.0)
            _, _, rgb, _, _ = pb.getCameraImage(
                width,
                height,
                view_matrix,
                proj_matrix,
                physicsClientId=self.physics_client
            )
            return np.array(rgb)[:, :, :3]
        return None

    def close(self) -> None:
        """Clean up resources."""
        if self.physics_client >= 0:
            pb.disconnect(self.physics_client)
        super().close()

# Required for URDF loading
import pybullet_data