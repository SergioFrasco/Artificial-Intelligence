import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

# Function to perform Q-learning
def q_learning(env, episodes, epsilon, alpha, gamma):
    # Initialize Q-table with zeros
    q_table = np.zeros((env.observation_space.n, env.action_space.n))
    # Store rewards for each episode
    rewards = []

    # Loop through episodes
    for _ in range(episodes):
        # Reset environment to start a new episode
        state, _ = env.reset()
        # Initialize episode variables
        done = False
        episode_reward = 0

        # Loop through steps within the episode
        for _ in range(100):
            # Exploration-exploitation trade-off
            if np.random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()  # Choose a random action
            else:
                action = np.argmax(q_table[state, :])  # Choose action with highest Q-value

            # Take a step in the environment
            next_state, reward, done, _, _ = env.step(action)
            episode_reward += reward

            # Update Q-value using the Q-learning update rule
            q_table[state, action] += alpha * (reward + gamma * np.max(q_table[next_state, :]) - q_table[state, action])
            state = next_state

            # Break if episode is finished
            if done:
                break

        rewards.append(episode_reward)

    return rewards

# Function to perform SARSA
def sarsa(env, episodes, epsilon, alpha, gamma):
    q_table = np.zeros((env.observation_space.n, env.action_space.n))
    rewards = []

    for _ in range(episodes):
        state, _ = env.reset()
        done = False
        episode_reward = 0

        # Choose action for the first step
        if np.random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state, :])

        for _ in range(100):
            # Take a step in the environment
            next_state, reward, done, _, _ = env.step(action)
            episode_reward += reward

            # Choose next action using epsilon-greedy policy
            if np.random.uniform(0, 1) < epsilon:
                next_action = env.action_space.sample()
            else:
                next_action = np.argmax(q_table[next_state, :])

            # Update Q-value using SARSA update rule
            q_table[state, action] += alpha * (reward + gamma * q_table[next_state, next_action] - q_table[state, action])
            state = next_state
            action = next_action

            # Break if episode is finished
            if done:
                break

        rewards.append(episode_reward)

    return rewards

# Initialize environment and parameters
env = gym.make('CliffWalking-v0')
episodes = 1000
epsilon = 0.1
alpha = 0.1
gamma = 0.99
runs = 10

# Initialize arrays to store rewards
q_learning_rewards = np.zeros((runs, episodes))
sarsa_rewards = np.zeros((runs, episodes))

# Run multiple iterations to get average rewards
for i in range(runs):
    q_learning_rewards[i] = q_learning(env, episodes, epsilon, alpha, gamma)
    sarsa_rewards[i] = sarsa(env, episodes, epsilon, alpha, gamma)

# Calculate average rewards across all runs
q_learning_avg_rewards = np.mean(q_learning_rewards, axis=0)
sarsa_avg_rewards = np.mean(sarsa_rewards, axis=0)

# Plot average rewards over episodes for both algorithms
plt.plot(q_learning_avg_rewards, label='Q-Learning')
plt.plot(sarsa_avg_rewards, label='SARSA')
plt.xlabel('Episode')
plt.ylabel('Average Return')
plt.legend()
plt.show()
