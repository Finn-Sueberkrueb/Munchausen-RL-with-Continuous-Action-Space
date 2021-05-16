import gym
import pybulletgym 
import numpy as np

from stable_baselines3 import SAC
from algos.msac import MSAC

env = gym.make("InvertedPendulumPyBulletEnv-v0")
# env.render()

# train new agent
model = SAC("MlpPolicy", env, verbose=1, tensorboard_log="./trained_agents/sac_invertedPendulum/tensorboard/")
# load last trained agent
# model = SAC.load("./trained_agents/sac_invertedPendulum", env, verbose=1, tensorboard_log="./trained_agents/sac_invertedPendulum_tensorboard")
model.learn(total_timesteps=5000, log_interval=4)
model.save("./trained_agents/sac_invertedPendulum")

print("replay trained agent")
obs = env.reset()
while True:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    env.render()
    if done:
      obs = env.reset()