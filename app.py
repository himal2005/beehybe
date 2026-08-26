import streamlit as st
import random
import re
import time

# Page Configuration
st.set_page_config(page_title="Card Game Arcade", page_icon="🃏", layout="wide")

# Custom CSS for Animations, Styled Card Chips, and Layout
st.markdown("""
<style>
    /* Card Flip & Slide Animations */
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .card-chip {
        display: inline-block;
        background-color: #ffffff;
        color: #1e1e1e;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px;
        font-weight: bold;
        font-size: 1.2rem;
        box-shadow: 2px 3px 5px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease-out;
    }
    
    .card-red {
        color: #d9534f !important;
    }
    
    .card-black {
        color: #292b2c !important;
    }
    
    .card-hidden {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: #ffffff !important;
        border-color: #ffffff;
    }
    
    .winner-badge {
        animation: pulse 1s infinite;
        background-color: #28a745;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Audio Helper for Interactive Sounds
def play_sound(sound_type):
    sound_urls = {
        "deal": "https://www.soundjay.com/misc/sounds/card-flip-1.mp3",
        "win": "https://www.soundjay.com/human/sounds/applause-01.mp3",
        "lose": "https://www.soundjay.com/misc/sounds/fail-buzzer-01.mp3"
    }
    url = sound_urls.get(sound_type)
    if url:
        st.markdown(f'<audio src="{url}" autoplay style="display:none;"></audio>', unsafe_allow_html=True)

# Helper function to render styled HTML cards
def render_card(card_str):
    if card_str == "HIDDEN":
        return '<span class="card-chip card-hidden">🎴 ???</span>'
    
    is_red = "♥️" in card_str or "♦️" in card_str
    color_class = "card-red" if is_red else "card-black"
    return f'<span class="card-chip {color_class}">{card_str}</span>'

def render_hand(hand):
    return " ".join([render_card(c) for c in hand])

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

# App Header
st.title("🃏 Interactive Card Game Arcade")
st.write("Experience smooth animations, interactive dealing, and real-time feedback across games.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "♠️ Blackjack", 
    "♥️ Hearts", 
    "♦️ Poker (Texas Hold'em)", 
    "♣️ Spades", 
    "🃏 Cribbage", 
    "🎴 Bridge"
])

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
        st.markdown(render_hand(st.session_state.bj_player), unsafe_allow_html=True)
        st.metric(label="Your Current Score", value=player_score)

    with col2:
        st.subheader("Dealer's Hand")
        if st.session_state.bj_game_over:
            st.markdown(render_hand(st.session_state.bj_dealer), unsafe_allow_html=True)
            st.metric(label="Dealer Score", value=dealer_score)
        else:
            dealer_display = [st.session_state.bj_dealer[0], "HIDDEN"]
            st.markdown(render_hand(dealer_display), unsafe_allow_html=True)
            st.metric(label="Dealer Score", value="?")

    st.divider()

    if not st.session_state.bj_game_over:
        c1, c2 = st.columns(2)
        if c1.button("💥 Hit", use_container_width=True, type="primary"):
            play_sound("deal")
            st.session_state.bj_player.append(st.session_state.bj_deck.pop())
            if calculate_bj_score(st.session_state.bj_player) > 21:
                st.session_state.bj_game_over = True
                st.session_state.bj_result = "Bust! Dealer Wins."
            st.rerun()

        if c2.button("✋ Stand", use_container_width=True):
            st.session_state.bj_game_over = True
            
            # Dealer Turn with Animated Delay
            with st.status("Dealer drawing cards...", expanded=True) as status:
                while calculate_bj_score(st.session_state.bj_dealer) < 17:
                    time.sleep(0.6)
                    st.session_state.bj_dealer.append(st.session_state.bj_deck.pop())
                    st.write(f"Dealer draws: {st.session_state.bj_dealer[-1]}")
                status.update(label="Dealer finished drawing!", state="complete")
            
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
        if "Win" in st.session_state.bj_result:
            st.balloons()
            play_sound("win")
            st.markdown(f'<div class="winner-badge">{st.session_state.bj_result}</div>', unsafe_allow_html=True)
        else:
            play_sound("lose")
            st.error(st.session_state.bj_result)

        st.write("")
        if st.button("🔄 Play Again", type="primary"):
            del st.session_state.bj_deck
            st.rerun()

# --- TAB 2: HEARTS ---
with tab2:
    st.header("Hearts (Singleplayer vs 3 AIs)")
    st.write("Avoid taking trick penalty cards: Hearts (1 pt each) and the Queen of Spades (13 pts).")
    
    if st.button("🎴 Deal New Round", key="hearts_deal"):
        with st.spinner("Shuffling and dealing 13 cards to all 4 players..."):
            time.sleep(0.5)
            play_sound("deal")
            deck = create_deck()
            random.shuffle(deck)
            st.session_state.hearts_hand = sorted(deck[:13])
            st.session_state.hearts_dealt = True

    if st.session_state.get("hearts_dealt"):
        st.subheader("Your 13-Card Hand")
        st.markdown(render_hand(st.session_state.hearts_hand), unsafe_allow_html=True)
        
        st.write("")
        card_to_play = st.selectbox("Select card to play:", st.session_state.hearts_hand, key="hearts_card")
        if st.button("🎯 Play Card"):
            with st.status("Simulating AI player moves...", expanded=True) as status:
                time.sleep(0.4)
                st.write("West plays 4♠️")
                time.sleep(0.4)
                st.write("North plays 8♠️")
                time.sleep(0.4)
                st.write("East plays K♠️")
                status.update(label="Trick complete!", state="complete")
            st.success(f"You played {card_to_play}! Trick won by East.")

# --- TAB 3: POKER ---
with tab3:
    st.header("Texas Hold'em Poker")
    
    if st.button("🎴 Deal New Poker Hand", key="poker_deal"):
        play_sound("deal")
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.poker_hole = [deck.pop(), deck.pop()]
        st.session_state.poker_community = [deck.pop() for _ in range(5)]
        st.session_state.poker_stage = 1

    if "poker_hole" in st.session_state:
        st.subheader("Your Hole Cards")
        st.markdown(render_hand(st.session_state.poker_hole), unsafe_allow_html=True)
        
        st.subheader("Community Cards")
        stage = st.session_state.poker_stage
        comm = st.session_state.poker_community
        visible_comm = comm[:3] if stage == 1 else (comm[:4] if stage == 2 else comm)
        
        st.markdown(render_hand(visible_comm), unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns(2)
        if stage < 3 and c1.button("🪙 Check / Call", use_container_width=True):
            with st.spinner("Revealing next community card..."):
                time.sleep(0.4)
                play_sound("deal")
                st.session_state.poker_stage += 1
                st.rerun()
        if c2.button("🏳️ Fold", use_container_width=True):
            st.warning("You folded. Deal a new hand to play again.")

# --- TAB 4: SPADES ---
with tab4:
    st.header("Spades")
    bid = st.slider("Enter your bid for this round:", min_value=0, max_value=13, value=3)
    
    if st.button("🎴 Start Hand", key="spades_start"):
        play_sound("deal")
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.spades_hand = sorted(deck[:13])
        st.session_state.spades_started = True

    if st.session_state.get("spades_started"):
        st.subheader("Your Hand")
        st.markdown(render_hand(st.session_state.spades_hand), unsafe_allow_html=True)
        st.info(f"Target Bid Set: **{bid} tricks**")

# --- TAB 5: CRIBBAGE ---
with tab5:
    st.header("Cribbage")
    
    if st.button("🎴 Deal Cribbage Hand", key="crib_deal"):
        play_sound("deal")
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.crib_hand = deck[:6]
        st.session_state.crib_starter = deck[6]

    if "crib_hand" in st.session_state:
        st.subheader("Your 6 Cards")
        st.markdown(render_hand(st.session_state.crib_hand), unsafe_allow_html=True)
        st.write("**Starter Card:**")
        st.markdown(render_card(st.session_state.crib_starter), unsafe_allow_html=True)
        
        st.write("")
        discards = st.multiselect("Select 2 cards for the crib:", st.session_state.crib_hand, max_selections=2)
        if len(discards) == 2 and st.button("🔒 Confirm Discards"):
            remaining = [c for c in st.session_state.crib_hand if c not in discards]
            st.success("Hand locked in! Cards sent to crib.")
            st.markdown(render_hand(remaining), unsafe_allow_html=True)

# --- TAB 6: BRIDGE ---
with tab6:
    st.header("Contract Bridge")
    
    col_a, col_b = st.columns(2)
    with col_a:
        contract = st.selectbox("Select Bidding Contract Level:", ["1", "2", "3", "4", "5", "6", "7"])
    with col_b:
        suit_bid = st.selectbox("Select Trump Suit:", ["♣️ Clubs", "♦️ Diamonds", "♥️ Hearts", "♠️ Spades", "No Trump"])
    
    if st.button("🎴 Deal Bridge Hand", key="bridge_deal"):
        play_sound("deal")
        deck = create_deck()
        random.shuffle(deck)
        st.session_state.bridge_hand = sorted(deck[:13])
        st.session_state.bridge_started = True

    if st.session_state.get("bridge_started"):
        st.subheader("Your Hand")
        st.markdown(render_hand(st.session_state.bridge_hand), unsafe_allow_html=True)
        st.success(f"Contract Set: **{contract} {suit_bid}**")
