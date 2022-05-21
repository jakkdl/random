"""Calculate the probability of outcomes of a 4-game match given two glicko mu's and the First Player Advantage"""

def win_probs(mu_diff, fpa):
    a = 1/(1+math.e**-mu_diff)
    f = fpa

    a1 = a*f/(a*f + (1-a)*(1-f))
    a2 = a*(1-f)/(a*(1-f) + (1-a)*f)
    b1 = 1-a2
    b2 = 1-a1

    p = {}
    p['4-0'] = a1**2*a2**2
    p['3-1'] = 2 * (a1**2*a2*b1 + a1*a2**2*b2)
    p['2-2'] = a1**2*b1**2 + a2**2*b2**2 + 4*a1*a2*b1*b2
    p['1-3'] = 2 * (b1**2*b2*a1 + b1*b2**2*a2)
    p['0-4'] = b1**2*b2**2

    for res,prob in p.items():
        print(f'{res}: {100*prob:5.2f}%')
