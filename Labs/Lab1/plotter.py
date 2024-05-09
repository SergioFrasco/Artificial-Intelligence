import pandas as pd
import matplotlib.pyplot as plt

# Load data from Excel into DataFrame
df = pd.read_excel('outputFinal.xlsx')
print(df.columns)

# Plotting
plt.figure(figsize=(10, 6))  # Set the figure size

# Plot line for Algorithm 1
plt.plot(df['Solution'], df['BFS'], label='BFS')

# Plot line for Algorithm 2
plt.plot(df['Solution'], df['A*-h1'], label='A*-h1')

# Plot line for Algorithm 3
plt.plot(df['Solution'], df['A*-h2'], label='A*-h2')

# Add labels and title
plt.xlabel('Solution Depth')
plt.ylabel('Nodes Expanded')
plt.title('Performance of Algorithms')
plt.legend()  # Add legend

plt.yscale('log')
# Show plot
plt.grid(True)  # Add grid
plt.show()
