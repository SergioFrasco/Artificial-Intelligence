import reconchess as rc
import os

from reconchess.bots.random_bot import RandomBot
from reconchess.bots.trout_bot import TroutBot
from reconchess.bots.attacker_bot import AttackerBot
from RandomSensing import RandomSensingAgent
from ImprovedAgentWorking import ImprovedAgent

# Define the environment variable for Stockfish
STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

# Check if the Stockfish environment variable exists
if STOCKFISH_ENV_VAR not in os.environ:
    raise KeyError(
        'Require an environment variable called "{}" pointing to the Stockfish executable'.format(
            STOCKFISH_ENV_VAR))

# Make sure there is actually a file
stockfish_path = os.environ[STOCKFISH_ENV_VAR]
if not os.path.exists(stockfish_path):
    raise ValueError('No Stockfish executable found at "{}"'.format(stockfish_path))
import subprocess

def run_match(bot1_path, bot2_path, num_matches):
    bot1_wins = 0
    bot2_wins = 0

    for i in range(num_matches):
        print(f"Match {i+1}:")
        result = subprocess.run(["rc-bot-match", bot1_path, bot2_path], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()

        if ("white" in output_lines[-1]):
            bot1_score = 1
            bot2_score = 0
        elif ("black" in output_lines[-1]):
            bot1_score = 0
            bot2_score = 1
        else:
            print("Error, no winner")
            continue

        if bot1_score > bot2_score:
            bot1_wins += 1
        elif bot1_score < bot2_score:
            bot2_wins += 1
        
        print(f"So far: White - {bot1_wins} Black - {bot2_wins}")

    return bot1_wins, bot2_wins

# Paths to the bots' Python files
bot1_path = "reconchess.bots.trout_bot"
bot2_path = "ImprovedAgentWorking.py"

# Number of matches to run
num_matches = 20

# Run matches
bot1_wins, bot2_wins = run_match(bot1_path, bot2_path, num_matches)

# Print results
print(f"Bot 1 wins: {bot1_wins}")
print(f"Bot 2 wins: {bot2_wins}")
