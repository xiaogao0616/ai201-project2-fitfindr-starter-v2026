"""Local regression checks; model calls are mocked, not acceptance evaluations."""
from unittest.mock import patch

import agent
from tools import search_listings, create_fit_card, _size_matches
from utils.data_loader import get_empty_wardrobe


def main():
    assert _size_matches('m', 'S/M')
    assert not _size_matches('L', 'XL')
    assert not _size_matches('S', 'US 9')
    results = search_listings('graphic tee', size='M', max_price=30)
    assert results and all(item['price'] <= 30 for item in results)
    assert search_listings('astronaut', max_price=1) == []
    assert create_fit_card('  ', {}) == 'No outfit suggestion was available for this item.'
    with patch('agent.suggest_outfit', return_value='Outfit') as outfit, patch(
        'agent.create_fit_card', return_value='Card'
    ) as card:
        session = agent.run_agent('graphic tee under $30, size M', get_empty_wardrobe())
        assert session['error'] is None
        assert session['parsed'] == {'description': 'graphic tee', 'size': 'M', 'max_price': 30.0}
        assert outfit.call_args.args[0] is session['selected_item']
        assert outfit.call_args.args[1] is session['wardrobe']
        assert card.call_args.args == (session['outfit_suggestion'], session['selected_item'])
        assert session['fit_card'] == 'Card'
        outfit.reset_mock()
        card.reset_mock()
        session = agent.run_agent('rare astronaut costume under $1', get_empty_wardrobe())
        outfit.assert_not_called()
        card.assert_not_called()
        assert session['fit_card'] is None
        assert 'increasing the maximum price' in session['error']
    print('PASS: size and price filters, empty cases, session handoff, and early stop (mocked model).')


if __name__ == '__main__':
    main()
