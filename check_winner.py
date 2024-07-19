def check_winner(board):
    winning_combinations = [
        (0, 1, 2),  # Row 1
        (3, 4, 5),  # Row 2
        (6, 7, 8),  # Row 3
        (0, 3, 6),  # Column 1
        (1, 4, 7),  # Column 2
        (2, 5, 8),  # Column 3
        (0, 4, 8),  # Diagonal 1
        (2, 4, 6)   # Diagonal 2
    ]

    for (a, b, c) in winning_combinations:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return { "winner": board[a], "winning_combination": (a, b, c) }  # Return the winner ('X' or 'O') and the indices of the winning combination

    if all(space is not None for space in board):
        return "tie game"  # Return "tie game" if all spaces are filled but no winner

    return None
