from typing import Any, Dict, List, Optional, Tuple, Type, Union

import gym
import numpy as np
import torch as th
from torch.nn import functional as F

from stable_baselines3.common.buffers import ReplayBuffer
from stable_baselines3.common.noise import ActionNoise
from stable_baselines3 import SAC
from stable_baselines3.common.type_aliases import GymEnv, MaybeCallback, Schedule
from stable_baselines3.common.utils import polyak_update
from stable_baselines3.sac.policies import SACPolicy


class MSAC(SAC):
    """
    Munchausen Soft Actor-Critic (M-SAC)

    :param policy: The policy model to use (MlpPolicy, CnnPolicy, ...)
    :param env: The environment to learn from (if registered in Gym, can be str)
    :param learning_rate: learning rate for adam optimizer,
        the same learning rate will be used for all networks (Q-Values, Actor and Value function)
        it can be a function of the current progress remaining (from 1 to 0)
    :param buffer_size: size of the replay buffer
    :param learning_starts: how many steps of the model to collect transitions for before learning starts
    :param batch_size: Minibatch size for each gradient update
    :param tau: the soft update coefficient ("Polyak update", between 0 and 1)
    :param gamma: the discount factor
    :param train_freq: Update the model every ``train_freq`` steps. Alternatively pass a tuple of frequency and unit
        like ``(5, "step")`` or ``(2, "episode")``.
    :param gradient_steps: How many gradient steps to do after each rollout (see ``train_freq``)
        Set to ``-1`` means to do as many gradient steps as steps done in the environment
        during the rollout.
    :param action_noise: the action noise type (None by default), this can help
        for hard exploration problem. Cf common.noise for the different action noise type.
    :param replay_buffer_class: Replay buffer class to use (for instance ``HerReplayBuffer``).
        If ``None``, it will be automatically selected.
    :param replay_buffer_kwargs: Keyword arguments to pass to the replay buffer on creation.
    :param optimize_memory_usage: Enable a memory efficient variant of the replay buffer
        at a cost of more complexity.
        See https://github.com/DLR-RM/stable-baselines3/issues/37#issuecomment-637501195
    :param ent_coef: Entropy regularization coefficient. (Equivalent to
        inverse of reward scale in the original SAC paper.)  Controlling exploration/exploitation trade-off.
        Set it to 'auto' to learn it automatically (and 'auto_0.1' for using 0.1 as initial value)
    :param target_update_interval: update the target network every ``target_network_update_freq``
        gradient steps.
    :param target_entropy: target entropy when learning ``ent_coef`` (``ent_coef = 'auto'``)
    :param use_sde: Whether to use generalized State Dependent Exploration (gSDE)
        instead of action noise exploration (default: False)
    :param sde_sample_freq: Sample a new noise matrix every n steps when using gSDE
        Default: -1 (only sample at the beginning of the rollout)
    :param use_sde_at_warmup: Whether to use gSDE instead of uniform sampling
        during the warm up phase (before learning starts)
    :param create_eval_env: Whether to create a second environment that will be
        used for evaluating the agent periodically. (Only available when passing string for the environment)
    :param policy_kwargs: additional arguments to be passed to the policy on creation
    :param verbose: the verbosity level: 0 no output, 1 info, 2 debug
    :param seed: Seed for the pseudo random generators
    :param device: Device (cpu, cuda, ...) on which the code should be run.
        Setting it to auto, the code will be run on the GPU if possible.
    :param _init_setup_model: Whether or not to build the network at the creation of the instance
    :param munchausen_scaling: Munchausen log policy scaling coefficient [0, 1].
    :param munchausen_clipping_low: Munchausen term clipping coefficient low. limits the log-policy term,
        otherwise numerical problems may occur if the policy becomes too deterministic.
    :param munchausen_clipping_high: Munchausen term clipping coefficient high. limits the log-policy term,
        otherwise numerical problems may occur if the policy becomes too deterministic.
    :param munchausen_mode: To test different approaches
    """

    def __init__(
        self,
        policy: Union[str, Type[SACPolicy]],
        env: Union[GymEnv, str],
        learning_rate: Union[float, Schedule] = 3e-4,
        buffer_size: int = 1000000,  # 1e6
        learning_starts: int = 100,
        batch_size: int = 256,
        tau: float = 0.005,
        gamma: float = 0.99,
        train_freq: Union[int, Tuple[int, str]] = 1,
        gradient_steps: int = 1,
        action_noise: Optional[ActionNoise] = None,
        replay_buffer_class: Optional[ReplayBuffer] = None,
        replay_buffer_kwargs: Optional[Dict[str, Any]] = None,
        optimize_memory_usage: bool = False,
        ent_coef: Union[str, float] = "auto",
        target_update_interval: int = 1,
        target_entropy: Union[str, float] = "auto",
        use_sde: bool = False,
        sde_sample_freq: int = -1,
        use_sde_at_warmup: bool = False,
        tensorboard_log: Optional[str] = None,
        create_eval_env: bool = False,
        policy_kwargs: Dict[str, Any] = None,
        verbose: int = 0,
        seed: Optional[int] = None,
        device: Union[th.device, str] = "auto",
        _init_setup_model: bool = True,
        munchausen_scaling: float = 0.9,
        munchausen_clipping_low: float = -1.0,
        munchausen_clipping_high: float = 0.0, # TODO: How to choose the clipping values
        munchausen_mode: str = "default",
        dynamicshift_hyperparameter: float = 0.0
    ):

        super(MSAC, self).__init__(
            policy,
            env,
            learning_rate,
            buffer_size,
            learning_starts,
            batch_size,
            tau,
            gamma,
            train_freq,
            gradient_steps,
            action_noise,
            replay_buffer_class,
            replay_buffer_kwargs,
            optimize_memory_usage,
            ent_coef,
            target_update_interval,
            target_entropy,
            use_sde,
            sde_sample_freq,
            use_sde_at_warmup,
            tensorboard_log,
            create_eval_env,
            policy_kwargs,
            verbose,
            seed,
            device,
            _init_setup_model,
        )

        self.munchausen_scaling = munchausen_scaling
        self.munchausen_clipping_low = munchausen_clipping_low
        self.munchausen_clipping_high = munchausen_clipping_high
        self.munchausen_mode = munchausen_mode
        self.dynamicshift_hyperparameter = dynamicshift_hyperparameter

        self.log_prob_min = 1e9
        self.log_prob_max = -1e9

    def train(self, gradient_steps: int, batch_size: int = 64) -> None:
        # Update optimizers learning rate
        optimizers = [self.actor.optimizer, self.critic.optimizer]
        if self.ent_coef_optimizer is not None:
            optimizers += [self.ent_coef_optimizer]

        # Update learning rate according to lr schedule
        self._update_learning_rate(optimizers)

        ent_coef_losses, ent_coefs = [], []
        actor_losses, critic_losses = [], []

        for gradient_step in range(gradient_steps):
            # Sample replay buffer
            replay_data = self.replay_buffer.sample(batch_size, env=self._vec_normalize_env)

            # We need to sample because `log_std` may have changed between two gradient steps
            if self.use_sde:
                self.actor.reset_noise()

            # Action by the current actor for the sampled state
            actions_pi, log_prob = self.actor.action_log_prob(replay_data.observations)
            log_prob = log_prob.reshape(-1, 1)

            ent_coef_loss = None
            if self.ent_coef_optimizer is not None:
                # Important: detach the variable from the graph
                # so we don't change it with other losses
                # see https://github.com/rail-berkeley/softlearning/issues/60
                ent_coef = th.exp(self.log_ent_coef.detach())
                ent_coef_loss = -(self.log_ent_coef * (log_prob + self.target_entropy).detach()).mean()
                ent_coef_losses.append(ent_coef_loss.item())
            else:
                ent_coef = self.ent_coef_tensor

            ent_coefs.append(ent_coef.item())

            # Optimize entropy coefficient, also called
            # entropy temperature or alpha in the paper
            if ent_coef_loss is not None:
                self.ent_coef_optimizer.zero_grad()
                ent_coef_loss.backward()
                self.ent_coef_optimizer.step()

            with th.no_grad():
                # Select action according to policy
                next_actions, next_log_prob = self.actor.action_log_prob(replay_data.next_observations)
                # Compute the next Q values: min over all critics targets
                next_q_values = th.cat(self.critic_target(replay_data.next_observations, next_actions), dim=1)
                next_q_values, _ = th.min(next_q_values, dim=1, keepdim=True)
                # add entropy term
                next_q_values = next_q_values - ent_coef * next_log_prob.reshape(-1, 1)
                # ----- SAC -----
                # td error + entropy term
                # target_q_values = replay_data.rewards + (1 - replay_data.dones) * self.gamma * next_q_values
                # ----- M-SAC -----
                # ...
                log_prob_normalized = None

                # log prob based on actions and observations from the replay buffer
                actions_pi, replay_log_prob = self.actor.replay_action_log_prob(replay_data.actions, replay_data.observations)
                replay_log_prob = replay_log_prob.reshape(-1, 1)

                if (self.munchausen_mode == "no_clipping"):


                    next_munchausen_values = ent_coef * replay_log_prob
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None

                elif (self.munchausen_mode == "fix_scale"):
                    next_munchausen_values = replay_log_prob
                    next_munchausen_values = self.munchausen_scaling * th.clamp(next_munchausen_values,
                                                                                self.munchausen_clipping_low,
                                                                                self.munchausen_clipping_high)
                elif (self.munchausen_mode == "shift"):
                    # Test implementation shift in range [-1,0]
                    munchausen_shift = 30.0
                    next_munchausen_values = ent_coef * (replay_log_prob - munchausen_shift)
                    next_munchausen_values = self.munchausen_scaling * th.clamp(next_munchausen_values,
                                                                                self.munchausen_clipping_low,
                                                                                self.munchausen_clipping_high)
                elif (self.munchausen_mode == "dynamicshift"):
                    # As described in the final report. Has shown very good results on the HalfCheetah seed 1.
                    next_munchausen_values = ent_coef * (replay_log_prob - th.mean(replay_log_prob))
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None

                elif (self.munchausen_mode == "dynamicshift_hyper"):
                    # With hyperparameter for dynamic shift:
                    # -1 = dynamicshift_max
                    #  0 = dynamicshift_mean
                    #  1 = dynamicshift_min

                    if self.dynamicshift_hyperparameter <= 0.0:
                        next_munchausen_values = ent_coef * (replay_log_prob
                                                             - (1.0 + self.dynamicshift_hyperparameter) * th.mean(replay_log_prob)
                                                             + self.dynamicshift_hyperparameter * th.max(replay_log_prob))
                    else:
                        next_munchausen_values = ent_coef * (replay_log_prob
                                                             + (self.dynamicshift_hyperparameter - 1.0) * th.mean(replay_log_prob)
                                                             - self.dynamicshift_hyperparameter * th.min(replay_log_prob))


                    self.logger.record("munchausen/log_policy_shifted", next_munchausen_values/ent_coef)
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values


                elif (self.munchausen_mode == "dynamicmean_hyper"):
                    # With hyperparameter for dynamic shift mean:
                    #  0 = dynamicshift_mean

                    next_munchausen_values = ent_coef * (replay_log_prob - th.mean(replay_log_prob) + self.dynamicshift_hyperparameter)

                    self.logger.record("munchausen/log_policy_shifted", next_munchausen_values / ent_coef)
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None



                elif (self.munchausen_mode == "dynamicshift_median"):

                    next_munchausen_values = ent_coef * (replay_log_prob - th.median(replay_log_prob))
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None

                    self.logger.record("munchausen/log_policy_shifted_median", next_munchausen_values)

                elif (self.munchausen_mode == "dynamicshift_target_entropy"):

                    next_munchausen_values = ent_coef * (replay_log_prob - abs(self.target_entropy))
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None
                    self.logger.record("munchausen/target_entropy", self.target_entropy)
                    self.logger.record("munchausen/log_policy_shifted_target_entropy", next_munchausen_values)

                elif (self.munchausen_mode == "dynamicshift_max"):
                    # As described in the final report. Has shown very good results on the HalfCheetah seed 1.
                    next_munchausen_values = ent_coef * (replay_log_prob - th.max(replay_log_prob))
                    self.logger.record("munchausen/log_policy_shifted", next_munchausen_values/ent_coef)
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None

                elif (self.munchausen_mode == "dynamicshift_normalized"):
                    # New experimental approach
                    """                     
                    min_old = th.min(replay_log_prob)
                    max_old = th.max(replay_log_prob)
                    min_new = th.ones_like(min_old) * -1
                    max_new = th.zeros_like(min_old)
                    range_old = max_old - min_old
                    range_new = max_new - min_new
                    scale_factor = range_new / range_old
                    log_prob_normalized = min_new + (replay_log_prob - min_old) * scale_factor
                    next_munchausen_values = ent_coef * log_prob_normalized
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values
                    """
                    # New experimental approach 2
                    if (th.min(replay_log_prob) < self.log_prob_min):
                        self.log_prob_min = th.min(replay_log_prob)
                    if (th.max(replay_log_prob) > self.log_prob_max):
                        self.log_prob_max = th.max(replay_log_prob)
                    min_old = self.log_prob_min
                    max_old = self.log_prob_max
                    min_new = th.ones_like(min_old) * -1
                    max_new = th.zeros_like(min_old)
                    range_old = max_old - min_old
                    range_new = max_new - min_new
                    scale_factor = range_new / range_old
                    log_prob_normalized = min_new + (replay_log_prob - min_old) * scale_factor
                    next_munchausen_values = ent_coef * log_prob_normalized
                    next_munchausen_values = self.munchausen_scaling * next_munchausen_values

                    # For logging
                    self.munchausen_clipping_low = None
                    self.munchausen_clipping_high = None

                else :
                    # Default M-SAC
                    next_munchausen_values = ent_coef * replay_log_prob
                    next_munchausen_values = self.munchausen_scaling * th.clamp(next_munchausen_values,
                                                                                self.munchausen_clipping_low,
                                                                                self.munchausen_clipping_high)

                # td error + Munchausen term + entropy term
                target_q_values = replay_data.rewards + next_munchausen_values \
                                  + (1 - replay_data.dones) * self.gamma * next_q_values

            # Get current Q-values estimates for each critic network
            # using action from the replay buffer
            current_q_values = self.critic(replay_data.observations, replay_data.actions)

            # Compute critic loss
            critic_loss = 0.5 * sum([F.mse_loss(current_q, target_q_values) for current_q in current_q_values])
            critic_losses.append(critic_loss.item())

            # Optimize the critic
            self.critic.optimizer.zero_grad()
            critic_loss.backward()
            self.critic.optimizer.step()

            # Compute actor loss
            # Alternative: actor_loss = th.mean(log_prob - qf1_pi)
            # Mean over all critic networks
            q_values_pi = th.cat(self.critic.forward(replay_data.observations, actions_pi), dim=1)
            min_qf_pi, _ = th.min(q_values_pi, dim=1, keepdim=True)
            actor_loss = (ent_coef * log_prob - min_qf_pi).mean()
            actor_losses.append(actor_loss.item())

            # Optimize the actor
            self.actor.optimizer.zero_grad()
            actor_loss.backward()
            self.actor.optimizer.step()

            # Update target networks
            if gradient_step % self.target_update_interval == 0:
                polyak_update(self.critic.parameters(), self.critic_target.parameters(), self.tau)

        self._n_updates += gradient_steps

        # log the proportion that Munchausen has in the target q value
        entropy_scalamean = (th.mean(-ent_coef * next_log_prob.reshape(-1, 1)).data.numpy())
        self.logger.record("munchausen/entropy_scalamean", np.average(entropy_scalamean))
        entropy_mean = (th.mean(-next_log_prob.reshape(-1, 1)).data.numpy())
        self.logger.record("munchausen/entropy_mean", np.average(entropy_mean))
        self.logger.record("munchausen/munchausen_clipping_low", self.munchausen_clipping_low)
        self.logger.record("munchausen/munchausen_clipping_high", self.munchausen_clipping_high)
        self.logger.record("munchausen/munchausen_scaling", self.munchausen_scaling)
        self.logger.record("munchausen/next_munchausen_values", np.average(next_munchausen_values))
        self.logger.record("munchausen/munchausen_fraction", np.average((abs(next_munchausen_values) / target_q_values)))
        self.logger.record("munchausen/log_policy", log_prob)
        self.logger.record("munchausen/next_q_values", np.average(next_q_values))
        self.logger.record("munchausen/log_policy_normalized", log_prob_normalized)

        self.logger.record("train/n_updates", self._n_updates, exclude="tensorboard")
        self.logger.record("train/ent_coef", np.mean(ent_coefs))
        self.logger.record("train/actor_loss", np.mean(actor_losses))
        self.logger.record("train/critic_loss", np.mean(critic_losses))
        if len(ent_coef_losses) > 0:
            self.logger.record("train/ent_coef_loss", np.mean(ent_coef_losses))

    def learn(
        self,
        total_timesteps: int,
        callback: MaybeCallback = None,
        log_interval: int = 4,
        eval_env: Optional[GymEnv] = None,
        eval_freq: int = -1,
        n_eval_episodes: int = 5,
        tb_log_name: str = "M-SAC",
        eval_log_path: Optional[str] = None,
        reset_num_timesteps: bool = True,
    ) -> SAC:

        return super(MSAC, self).learn(
            total_timesteps=total_timesteps,
            callback=callback,
            log_interval=log_interval,
            eval_env=eval_env,
            eval_freq=eval_freq,
            n_eval_episodes=n_eval_episodes,
            tb_log_name=tb_log_name,
            eval_log_path=eval_log_path,
            reset_num_timesteps=reset_num_timesteps,
        )

    def _excluded_save_params(self) -> List[str]:
        return super(MSAC, self)._excluded_save_params() + ["actor", "critic", "critic_target"]
