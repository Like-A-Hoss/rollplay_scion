def narrative_scale(scale:int):
    #this function takes in the scale factor and returns the narrative action sucess muliplier used
    if scale == 0:
        return 1
    elif scale == 1:
        return 2
    elif scale == 2:
        return 5
    elif scale == 3:
        return 10
    elif scale == 4:
        return 100
    elif scale == 5:
        return 200
    elif scale == 6:
        return 1000

def dramatic_scale(scale:int):
    #this function takes in the scale factor and returns the dramatic action enhancement bonus used
    if scale == 0:
        return 0
    elif scale == 1:
        return 2
    elif scale == 2:
        return 4
    elif scale == 3:
        return 6
    elif scale == 4:
        return 8
    elif scale == 5:
        return 12
    elif scale == 6:
        return 16
    
def calculate_final_scale(scale1:int, scale2:int):
    #this function takes in the scale factors of two opposing sides and returns the final scale factor and which side gets the bonus
    final_scale = scale1 - scale2
    if final_scale < 0:
        return abs(final_scale), "opponent"
    else:
        return final_scale, "player"