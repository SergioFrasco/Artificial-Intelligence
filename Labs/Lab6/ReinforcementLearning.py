import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def q_learning(env, episodes, epsilon, alpha, gamma):
    q_table = np.zeros((env.observation_space.n, env.action_space.n))
    rewards = []

    for _ in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0

        for _ in range(100):
            if np.random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(q_table[state, :])

            next_state, reward, done, _, _ = env.step(action)
            episode_reward += reward

            q_table[state, action] += alpha * (reward + gamma * np.max(q_table[next_state, :]) - q_table[state, action])
            state = next_state

            if done:
                break

        rewards.append(episode_reward)

    return rewards

def sarsa(env, episodes, epsilon, alpha, gamma):
    q_table = np.zeros((env.observation_space.n, env.action_space.n))
    rewards = []

    for _ in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0

        if np.random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state, :])

        for _ in range(100):
            next_state, reward, done, _, _ = env.step(action)
            episode_reward += reward

            if np.random.uniform(0, 1) < epsilon:
                next_action = env.action_space.sample()
            else:
                next_action = np.argmax(q_table[next_state, :])

            q_table[state, action] += alpha * (reward + gamma * q_table[next_state, next_action] - q_table[state, action])
            state = next_state
            action = next_action

            if done:
                break

        rewards.append(episode_reward)

    return rewards

env = gym.make('CliffWalking-v0')
episodes = 1000
epsilon = 0.1
alpha = 0.1
gamma = 0.99
runs = 10

q_learning_rewards = np.zeros((runs, episodes))
sarsa_rewards = np.zeros((runs, episodes))

for i in range(runs):
    q_learning_rewards[i] = q_learning(env, episodes, epsilon, alpha, gamma)
    sarsa_rewards[i] = sarsa(env, episodes, epsilon, alpha, gamma)

q_learning_avg_rewards = np.mean(q_learning_rewards, axis=0)
sarsa_avg_rewards = np.mean(sarsa_rewards, axis=0)

plt.plot(q_learning_avg_rewards, label='Q-Learning')
plt.plot(sarsa_avg_rewards, label='SARSA')
plt.xlabel('Episode')
plt.ylabel('Average Return')
plt.legend()
plt.show()