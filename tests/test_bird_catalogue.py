import unittest
from chirpecho.chirp.labels import bird_labels
from chirpecho.web.portraits import profile


class BirdCatalogueTests(unittest.TestCase):
    def test_accepts_outside_birds_and_preserves_catalogue_names(self):
        labels = ['Turdus merula_Common Blackbird',
                  'Cardinalis cardinalis_Northern Cardinal',
                  'Canis lupus_Gray Wolf', 'Noise_Noise',
                  'Human non_vocal Human non-vocal',
                  'Dryophytes avivoca_Bird-voiced Treefrog',
                  'Dog_Dog', 'Engine_Engine', 'invalid']
        self.assertEqual(bird_labels(labels), {
            0: 'Eurasian Blackbird',
            1: 'Cardinalis cardinalis_Northern Cardinal',
        })

    def test_outside_bird_has_readable_name_and_pending_status(self):
        item = profile('Cardinalis cardinalis_Northern Cardinal', True)
        self.assertFalse(item['in_catalogue'])
        self.assertIsNone(item['number'])
        self.assertIsNone(item['portrait'])
        self.assertEqual(item['name'], 'Northern Cardinal')
        self.assertEqual(item['scientific'], 'Cardinalis cardinalis')
        self.assertIn('add this bird to the catalogue', item['note'])

    def test_adding_species_resolves_existing_raw_model_label(self):
        item = profile('Turdus merula_Eurasian Blackbird', True)
        self.assertTrue(item['in_catalogue'])
        self.assertEqual(item['number'], 1)


if __name__ == '__main__':
    unittest.main()
