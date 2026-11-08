"""Fixed collection-game tiers, not conservation or local occurrence ratings."""
TIERS = {
    'common': dict(label='Common', stars='★', color='#84958a'),
    'uncommon': dict(label='Uncommon', stars='★★', color='#4c9b68'),
    'rare': dict(label='Rare', stars='★★★', color='#4e8ccf'),
    'epic': dict(label='Epic', stars='★★★★', color='#a16bd3'),
    'legendary': dict(label='Legendary', stars='★★★★★', color='#dca639'),
    'unranked': dict(label='Unranked', stars='◇', color='#84958a'),
}
# Stable, deliberately authored game tiers in field-guide order.
BIRD_TIERS = (
    'common','common','common','common','common','uncommon','common','uncommon',
    'uncommon','common','common','common','common','common','common','uncommon',
    'uncommon','common','common','common','uncommon','rare','uncommon','rare',
    'uncommon','uncommon','rare','rare','uncommon','rare','rare','rare',
    'uncommon','common','uncommon','epic','uncommon','uncommon','rare','common',
    'rare','rare','epic','epic','legendary','legendary','epic','common',
    'uncommon','uncommon','common','common','uncommon','uncommon','common','rare',
)
BIRD_TIERS += ('rare', 'rare', 'uncommon', 'epic', 'rare', 'uncommon', 'uncommon', 'uncommon')
BIRD_TIERS += ('legendary', 'rare', 'rare', 'epic', 'rare')
BIRD_TIERS += ('uncommon',)
BAT_TIERS = (
    'common','uncommon','rare','uncommon','rare','uncommon',
    'uncommon','rare','rare','epic','legendary','legendary',
    'rare','legendary','epic','epic','legendary','legendary',
    'epic','legendary','epic','rare','epic','legendary',
)


def rarity_for(engine, number=None):
    ranks = BIRD_TIERS if engine == 'bird' else BAT_TIERS
    key = ranks[number-1] if number is not None and 1 <= number <= len(ranks) else 'unranked'
    return dict(TIERS[key], key=key)
