def verify_lisence_key(key):
    global score
    score = 0

    check_digit = key[3]
    check_digit_count = 0

    chunks = key.split("-")
    for chunk in chunks:
        if len(chunk) != 4:
            return False
        
        for char in chunk:
            if char==check_digit:
                check_digit_count += 1
            # add the score
            score += ord(char)
    print("score: ", score)
    # check for rules
    if score > 1984 and score < 2034 and check_digit_count==4:
        return True
    return False