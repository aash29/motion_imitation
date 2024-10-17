"""Simple script for executing random actions on A1 robot."""

import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(os.path.dirname(currentdir))
os.sys.path.insert(0, parentdir)

from absl import app
from absl import flags
import numpy as np
from tqdm import tqdm
import pybullet as p  # pytype: disable=import-error
import pybullet_data as pd

from motion_imitation.envs import env_builder
from motion_imitation.robots import go1
from motion_imitation.robots import laikago
from motion_imitation.robots import robot_config

FLAGS = flags.FLAGS
flags.DEFINE_enum('robot_type', 'go1', ['go1'], 'Robot Type.')
flags.DEFINE_enum('motor_control_mode', 'Torque',
                  ['Torque', 'Position', 'Hybrid'], 'Motor Control Mode.')
flags.DEFINE_bool('on_rack', False, 'Whether to put the robot on rack.')
flags.DEFINE_string('video_dir', None,
                    'Where to save video (or None for not saving).')

ROBOT_CLASS_MAP = {'go1': go1.go1}

MOTOR_CONTROL_MODE_MAP = {
    'Torque': robot_config.MotorControlMode.TORQUE,
    'Position': robot_config.MotorControlMode.POSITION,
    'Hybrid': robot_config.MotorControlMode.HYBRID
}


def main(_):
  robot = ROBOT_CLASS_MAP[FLAGS.robot_type]
  motor_control_mode = MOTOR_CONTROL_MODE_MAP[FLAGS.motor_control_mode]
  env = env_builder.build_env(enable_rendering=True,
              num_action_repeat=20,
              reset_at_current_position=False,
              use_real_robot=False,
              realistic_sim=True)



  action_low, action_high = env.action_space.low, env.action_space.high
  action_median = (action_low + action_high) / 2.
  dim_action = action_low.shape[0]
  action_selector_ids = []


  for dim in range(dim_action):
    action_selector_id = p.addUserDebugParameter(paramName='dim{}'.format(dim),
                                                 rangeMin=action_low[dim],
                                                 rangeMax=action_high[dim],
                                                 startValue=action_median[dim])
    action_selector_ids.append(action_selector_id)

  if FLAGS.video_dir:
    log_id = p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, FLAGS.video_dir)


  #for _ in tqdm(range(800)):
  while 1:
    action = np.zeros(dim_action)
    for dim in range(dim_action):
      action[dim] = env.pybullet_client.readUserDebugParameter(action_selector_ids[dim])
    env.step(action)
    #env.render()





  if FLAGS.video_dir:
    p.stopStateLogging(log_id)


if __name__ == "__main__":
  app.run(main)
