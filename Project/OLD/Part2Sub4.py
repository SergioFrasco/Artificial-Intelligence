import chess

def compare_windows(states, window):
    result = []
    
    for state in states:
        board = chess.Board(state)
        window_list = [row.split(":") for row in window.split(";")]
        same = True
        for item in window_list:
            position = item[0]
            section = item[1]
            square = chess.parse_square(position)
            piece = board.piece_at(square)          
            if section == "?":
                if piece is not None:
                    same = False
                    break
            else:
                if piece is None or (piece.color == chess.WHITE and piece.symbol().upper() != section) or (piece.color == chess.BLACK and piece.symbol().lower() != section):
                    same = False
                    break
        
        if same:
            result.append(state)
            break

    return sorted(result)

def filter_states_with_window(states, window):
    consistent_states = []
    
    # Iterate through the potential states
    for state_fen in states:
        # Check if the state is consistent with the window observation
        if compare_windows([state_fen], window):  # Pass state_fen as a list
            consistent_states.append(state_fen)
    
    return consistent_states


# Read the number of states
num_states = int(input())

# Read the potential states
potential_states = [input() for _ in range(num_states)]

# Read the window description
window = input()

# Filter states consistent with the window observation
consistent_states = filter_states_with_window(potential_states, window)

# Sort the consistent states alphabetically
consistent_states.sort()

# Output the consistent states
for state in consistent_states:
    print(state)
