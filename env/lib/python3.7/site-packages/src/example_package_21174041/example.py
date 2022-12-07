def calcFine(returnDate, today):
    fine = 0
    if returnDate <= today:
        fine += 5 * (today - returnDate).days
        return fine