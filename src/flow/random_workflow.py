import random
from src.actions.search import strategy_find_work, strategy_recent_search, strategy_home_direct

def random_search_flow(page, keyword):
    strategies = [
        strategy_home_direct,
        strategy_find_work,
        strategy_recent_search,
    ]

    strategy = random.choice(strategies)

    print(f"[INFO] Using strategy: {strategy.__name__}")
    strategy(page, keyword)
