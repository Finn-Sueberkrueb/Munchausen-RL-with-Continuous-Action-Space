#import gym
#import numpy as np

from stable_baselines3 import SAC
from algos.msac import MSAC
import pybulletgym.envs
import os.path
import time
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env
from tensorboard import program
from sys import platform


RLalgo = MSAC
GymEnvironment = "AntPyBulletEnv-v0"
ModelName = "M-SAC_Ant"
TensorBoardGroup = "Ant"

if platform == "linux" or platform == "linux2":
    # linux
    print("Linux system")
    run_on_server = True
    TotalTimestepsTraining = 1000000
    NumberOfVisualizedFrames = 0
    VisualizeEnvironment = False
    Training = True
    device = 'cuda'

elif platform == "darwin":
    # OS X
    print("OS X system")
    run_on_server = False
    TotalTimestepsTraining = 6000
    NumberOfVisualizedFrames = 10 * 60  # 10 sec
    VisualizeEnvironment = True
    Training = True
    device = 'cpu'


evaluation_frequency = 1000
startTensorBoard = True


# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

class TensorboardCallback(BaseCallback):
    """
    Custom callback for plotting additional values in tensorboard.
    """

    def __init__(self, verbose=0):
        super(TensorboardCallback, self).__init__(verbose)

    def _on_step(self) -> bool:
        # Log scalar value (here a random variable)
        if len(self.training_env.envs[0].episode_rewards) > 1:
            self.logger.record('validation/reward', self.training_env.envs[0].episode_rewards[-1])

        return True



# load the PyBullet environment
env = make_vec_env(GymEnvironment)

eval_env = make_vec_env(GymEnvironment)

eval_callback = EvalCallback(eval_env, best_model_save_path=('./TrainedAgents/' + ModelName + '/'),
                                 log_path=('./TrainedAgents/' + ModelName + '/'), eval_freq=evaluation_frequency,
                                 deterministic=True, render=False)


print("Simulation environment created.")
if VisualizeEnvironment:
    env.render(mode="human")


# check if a model with the name already exists
if os.path.isfile("./TrainedAgents/" + ModelName + ".zip"):
    # load previously created model trained model
    model = RLalgo.load(("./TrainedAgents/" + ModelName), env, ent_coef=0.5, device=device, verbose=1, tensorboard_log=("./TensorBoard/" + TensorBoardGroup + "/"))
    print("Found previously created model.")
elif os.path.isfile("./TrainedAgents/best_model.zip"):
    # load previously created model trained model
    model = RLalgo.load(("./TrainedAgents/best_model"), env)#, ent_coef=0.5, device=device, verbose=1, tensorboard_log=("./TensorBoard/" + TensorBoardGroup + "/"))
    print("Found previously saved Best model.")
else:
    # create new model
    model = RLalgo("MlpPolicy", env, ent_coef=0.5, device=device, verbose=1, tensorboard_log=("./TensorBoard/" + TensorBoardGroup + "/"))
    print("New model created.")


# Start TensorBoard
if startTensorBoard:
    if run_on_server:
        tb = program.TensorBoard()
        tb.configure(argv=[None, '--bind_all', '--port', '8080', '--logdir', './TensorBoard/' + TensorBoardGroup + '/'])
        url = tb.launch()
        #os.system("tensorboard --bind_all --port 8080 --logdir ./TensorBoard/mSAC-Ant/")
        print("Access TensorBoard: http://34.91.222.181:8080")
    else:
        tb = program.TensorBoard()
        tb.configure(argv=[None, '--logdir', './TensorBoard/' + TensorBoardGroup + '/'])
        url = tb.launch()
        print("Access TensorBoard: http://localhost:6006")




if Training:
    print("Start training for " + str(TotalTimestepsTraining) + " timesteps.")
    model.learn(total_timesteps=TotalTimestepsTraining, log_interval=4, callback=eval_callback)
    model.save("./TrainedAgents/" + ModelName)



if not run_on_server:
    print("Run model for " + str(NumberOfVisualizedFrames) + " Frames.")
    frame = 0
    accumulated_reward = 0
    observation = env.reset()
    for i in range(NumberOfVisualizedFrames):
        time.sleep(0.02)
        action, states = model.predict(observation, deterministic=True)
        observation, reward, done, info = env.step(action)
        accumulated_reward += reward
        frame += 1
        env.render()
        if done:
            print("reward=%0.2f in %i frames" % (accumulated_reward, frame))
            frame = 0
            accumulated_reward = 0
            observation = env.reset()

env.close()
print("Program finished.")