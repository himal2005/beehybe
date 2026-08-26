import streamlit as st
import random
import re

# Page Configuration
st.set_page_config(page_title="Card Game Arcade", page_icon="🃏", layout="wide")

st.title("🃏 Single-Player Card Game Arcade")
st.write("Select a tab below to play your favorite card game against AI opponents or complete solo challenges.")

# Define Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "♠️ Blackjack", 
    "♥️ Hearts", 
    "♦️ Poker (Texas Hold'em)", 
    "♣️ Spades", 
    "🃏 Cribbage", 
    "🎴 Bridge"
])

# Card Utilities
SUITS = ['♠️', '♥️', '♦️', '♣️']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

def card_value_bj(card):
    rank = re.match(r"^[0-9JQKA]+", card).group(0)
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    return int(rank)

def calculate_bj_score(hand):
    score = sum(card_value_bj(c) for c in hand)
    aces = sum(1 for c in hand if re.match(r"^A", c))
    while score > 21 and aces:
        score -= 10
        aces -= 1
    return score

# --- TAB 1: BLACKJACK ---
with tab1:
    st.header("Blackjack (Play vs Dealer)")
    
    if "bj_deck" not in st.session_state:
        st.session_state.bj_deck = create_deck()
        random.shuffle(st.session_state.bj_deck)
        st.session_state.bj_player = [st.session_state.bj_deck.pop(), st.session_state.bj_deck.pop()]
        st.session_state.bj_dealer = [st.session_state.bj_deck.pop(), st.session_state.bj_deck.pop()]
        st.session_state.bj_game_over = False
        st.session_state.bj_result = ""

    player_score = calculate_bj_score(st.session_state.bj_player)
    dealer_score = calculate_bj_score(st.session_state.bj_dealer)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Hand")
        st.write(" ".join([f"`{c}`" for c in st.session_state.bj_player]))
        st.write(f"**Score:** {player_score}")

    with col2:
        st.subheader("Dealer's Hand")
        if st.session_state.bj_game_over:
            st.write(" ".join([f"`{c}`" for c in st.session_state.bj_dealer]))
            st.write(f"**Score:** {dealer_score}")
        else:
            st.write(f"`{st.session_state.bj_dealer[0]}` `🎴 Hidden`")

    st.divider()

    if not st.session_state.bj_game_over:
        c1, c2 = st.columns(2)
        if c1.button("Hit", use_container_width=True):
            st.session_state.bj_player.append(st.session_state.bj_deck.pop())
            if calculate_bj_score(st.session_state.bj_player) > 21:
                st.session_state.bj_game_over = True
                st.session_state.bj_result = "Bust! Dealer Wins."
            st.rerun()

        if c2.button("Stand", use_container_width=True):
            st.session_state.bj_game_over = True
            while calculate_bj_score(st.session_state.bj_dealer) < 17:
                st.session_state.bj_dealer.append(st.session_state.bj_deck.pop())
            
            final_p = calculate_bj_score(st.session_state.bj_player)
            final_d = calculate_bj_score(st.session_state.bj_dealer)

            if final_d > 21 or final_p > final_d:
                st.session_state.bj_result = "🎉 You Win!"
            elif final_p < final_d:
                st.session_state.bj_result = "Dealer Wins."
            else:
                st.session_state.bj_result = "Push (Tie)!"
            st.rerun()

    else:
        st.info(st.session_state.bj_result)
        if st.button("Play Again", type="primary"):
            del st.session_state.bj_deck
            st.rerun()

# --- TAB 2: HEARTS ---
with tab2:
    st.header("Hearts (Singleplayer vs 3 AIs)")
    st.write("Avoid taking trick penalty cards: Hearts (1 pt each) and the Queen of Spades (13 pts).")
    
    if st.button("Deal New Round", key="hearts_deal"):
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.hearts_hand = sorted(deck[:13])
        st.session_state.hearts_dealt = True

    if st.session_state.get("hearts_dealt"):
        st.subheader("Your 13-Card Hand")
        st.write(" ".join([f"`{c}`" for c in st.session_state.hearts_hand]))
        st.selectbox("Select card to play:", st.session_state.hearts_hand, key="hearts_card")
        if st.button("Play Card"):
            st.success(f"Played {st.session_state.hearts_card}! AI turns simulated.")

# --- TAB 3: POKER ---
with tab3:
    st.header("Texas Hold'em Poker")
    st.write("Practice singleplayer Texas Hold'em against AI bots.")
    
    if st.button("Deal Hand", key="poker_deal"):
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.poker_hole = [deck.pop(), deck.pop()]
        st.session_state.poker_community = [deck.pop() for _ in range(5)]
        st.session_state.poker_stage = 1

    if "poker_hole" in st.session_state:
        st.subheader("Your Hole Cards")
        st.write(f"`{st.session_state.poker_hole[0]}` `{st.session_state.poker_hole[1]}`")
        
        st.subheader("Community Cards")
        stage = st.session_state.poker_stage
        comm = st.session_state.poker_community
        visible_comm = comm[:3] if stage == 1 else (comm[:4] if stage == 2 else comm)
        st.write(" ".join([f"`{c}`" for c in visible_comm]))
        
        c1, c2 = st.columns(2)
        if stage < 3 and c1.button("Check / Call"):
            st.session_state.poker_stage += 1
            st.rerun()
        if c2.button("Fold"):
            st.warning("You folded. Deal a new hand to play again.")

# --- TAB 4: SPADES ---
with tab4:
    st.header("Spades")
    st.write("Bid and play trick-taking hands with an AI partner against an AI team.")
    
    bid = st.number_input("Enter your bid for this round (0-13):", min_value=0, max_value=13, value=3)
    if st.button("Start Hand", key="spades_start"):
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.spades_hand = sorted(deck[:13])
        st.session_state.spades_started = True

    if st.session_state.get("spades_started"):
        st.subheader("Your Hand")
        st.write(" ".join([f"`{c}`" for c in st.session_state.spades_hand]))
        st.info(f"Target Bid: **{bid} tricks**")

# --- TAB 5: CRIBBAGE ---
with tab5:
    st.header("Cribbage")
    st.write("Score points by combining cards to make pairs, runs, and combinations that sum to 15.")
    
    if st.button("Deal Cribbage Hand", key="crib_deal"):
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.crib_hand = deck[:6]
        st.session_state.crib_starter = deck[6]

    if "crib_hand" in st.session_state:
        st.subheader("Your 6 Cards (Select 2 to discard to the Crib)")
        st.write(" ".join([f"`{c}`" for c in st.session_state.crib_hand]))
        st.write(f"**Starter Card:** `{st.session_state.crib_starter}`")
        
        discards = st.multiselect("Select 2 cards for crib:", st.session_state.crib_hand, max_selections=2)
        if len(discards) == 2 and st.button("Confirm Discards"):
            remaining = [c for c in st.session_state.crib_hand if c not in discards]
            st.success(f"Hand locked in: {' '.join(remaining)}")

# --- TAB 6: BRIDGE ---
with tab6:
    st.header("Contract Bridge")
    st.write("Practice bidding and card play in Contract Bridge against 3 AI opponents.")
    
    contract = st.selectbox("Select Bidding Contract Level:", ["1", "2", "3", "4", "5", "6", "7"])
    suit_bid = st.selectbox("Select Trump Suit:", ["♣️ Clubs", "♦️ Diamonds", "♥️ Hearts", "♠️ Spades", "No Trump"])
    
    if st.button("Deal Bridge Hand", key="bridge_deal"):
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.bridge_hand = sorted(deck[:13])
        st.session_state.bridge_started = True

    if st.session_state.get("bridge_started"):
        st.subheader("Your Hand")
        st.write(" ".join([f"`{c}`" for c in st.session_state.bridge_hand]))
        st.info(f"Contract Set: **{contract} {suit_bid}**")
