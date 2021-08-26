import random




def hits_target(deck, target):
    coins = 0
    hand = random.sample(deck, 5)
    remaining_cards = deck.copy()
    for card in hand:
        remaining_cards.remove(card)

    while 'p' in hand:
        hand.remove('p')
        draw = random.sample(remaining_cards, 1)
        hand += draw
        remaining_cards.remove(*draw)
        coins += 1

    if sum(hand) + coins >= target:
        return True


    coins = 0
    hand = random.sample(remaining_cards, 5)
    for card in hand:
        remaining_cards.remove(card)

    while 'p' in hand:
        hand.remove('p')
        coins += 1
        draw = random.sample(remaining_cards, 1)
        hand += draw
        remaining_cards.remove(*draw)

    return sum(hand) + coins >= target

def main(deck, target, count=1000000):
    print(deck)
    result = 0
    for i in range(count):
        if hits_target(deck, target):
            result += 1
    return result / count

if __name__ == '__main__':
    #deck = [1]*7 + [0]*3 + [2]*2
    deck = [1]*7 + [0]*3 + [2]*3
    print(main(deck, 6))
    deck = [1]*7 + [0]*3 + [2]*2 + ['p']
    print(main(deck, 6))


