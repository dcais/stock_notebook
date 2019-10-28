def get_strategy_pool():
    pool = []
    pool.append({
        'name': 'turtle55',
        'ctx': {
            'long_period': 55,
            'short_period': 20,
        }
    })
    pool.append({
        'name': "turtle20",
        'ctx': {
            'long_period': 20,
            'short_period': 10,
        }
    })
    pool.append({
        'name': "adosc",
        'ctx': {
        }
    })
    return pool
