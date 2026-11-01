#! python3

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_images_duplicates
    # for specific test
    python -m unittest tests.test_images_duplicates.TestImagesDuplicates.test_group_by_dimensions_finds_candidates
"""

# standard library
import unittest
from unittest.mock import patch

# project
from geotribu_cli.images.images_duplicates import (
    find_duplicate_images,
    group_images_by_dimensions,
)

# ############################################################################
# ########## Fixtures #############
# #################################

# Simule le contenu de images_dict issu de l'index CDN
SAMPLE_IMAGES_DICT = {
    # Groupe 1 : trois images de même dimensions → 2+ candidats
    "logos-icones/qgis.png": [200, 200],
    "logos-icones/qgis_copie.png": [200, 200],
    "logos-icones/qgis_backup.png": [200, 200],
    # Groupe 2 : deux images de même dimensions
    "articles/2023/carte.png": [800, 533],
    "articles/2024/carte_dupliquee.png": [800, 533],
    # Image unique (pas de doublon)
    "internal/logo-geotribu.png": [512, 512],
    # Image unique d'une dimension différente
    "logos-icones/postgis.png": [300, 300],
}

# ############################################################################
# ########## Classes #############
# ################################


class TestImagesDuplicates(unittest.TestCase):
    """Tests pour la détection des images en doublon dans le CDN."""

    # -- Tests de group_images_by_dimensions -----------------------------------

    def test_group_by_dimensions_finds_candidates(self):
        """Vérifie que le groupement par dimensions détecte bien les candidats."""
        groups = group_images_by_dimensions(SAMPLE_IMAGES_DICT)

        # On doit trouver 2 groupes (qgis×3 et carte×2), pas celui à 1 seul élément
        self.assertEqual(len(groups), 2)

    def test_group_by_dimensions_correct_members(self):
        """Vérifie que chaque groupe contient les bons chemins."""
        groups = group_images_by_dimensions(SAMPLE_IMAGES_DICT)

        # Le groupe 200×200 doit contenir les 3 variantes qgis
        qgis_group = groups.get((200, 200))
        self.assertIsNotNone(qgis_group)
        self.assertEqual(len(qgis_group), 3)
        self.assertIn("logos-icones/qgis.png", qgis_group)
        self.assertIn("logos-icones/qgis_copie.png", qgis_group)
        self.assertIn("logos-icones/qgis_backup.png", qgis_group)

        # Le groupe 800×533 doit contenir les 2 cartes
        carte_group = groups.get((800, 533))
        self.assertIsNotNone(carte_group)
        self.assertEqual(len(carte_group), 2)

    def test_group_by_dimensions_excludes_unique_images(self):
        """Vérifie que les images uniques (512×512 et 300×300) sont exclues."""
        groups = group_images_by_dimensions(SAMPLE_IMAGES_DICT)

        self.assertNotIn((512, 512), groups)
        self.assertNotIn((300, 300), groups)

    def test_group_by_dimensions_empty_input(self):
        """Vérifie le comportement avec un dict vide."""
        groups = group_images_by_dimensions({})
        self.assertEqual(groups, {})

    def test_group_by_dimensions_no_duplicates(self):
        """Vérifie qu'on renvoie un dict vide si toutes les images sont uniques."""
        unique_images = {
            "a.png": [100, 100],
            "b.png": [200, 200],
            "c.png": [300, 300],
        }
        groups = group_images_by_dimensions(unique_images)
        self.assertEqual(groups, {})

    # -- Tests de find_duplicate_images (sans check_content) ------------------

    def test_find_duplicates_without_content_check(self):
        """Sans --check-content, on retourne les candidats par dimensions."""
        duplicates = find_duplicate_images(
            images_dict=SAMPLE_IMAGES_DICT,
            cdn_base_url="https://cdn.geotribu.fr/",
            cdn_base_path="img",
            check_content=False,
        )

        # On attend 2 groupes (qgis et carte)
        self.assertEqual(len(duplicates), 2)
        # Chaque groupe doit avoir au moins 2 éléments
        for group in duplicates:
            self.assertGreaterEqual(len(group), 2)

    def test_find_duplicates_no_candidates(self):
        """Vérifie le comportement quand il n'y a aucun doublon."""
        unique_images = {
            "a.png": [100, 200],
            "b.png": [300, 400],
        }
        duplicates = find_duplicate_images(
            images_dict=unique_images,
            cdn_base_url="https://cdn.geotribu.fr/",
            cdn_base_path="img",
            check_content=False,
        )
        self.assertEqual(duplicates, [])

    # -- Tests de find_duplicate_images (avec check_content) ------------------

    @patch("geotribu_cli.images.images_duplicates.compute_remote_image_hash")
    def test_find_true_duplicates_with_same_hash(self, mock_hash):
        """Avec --check-content, deux images avec le même hash → vrai doublon."""

        # On simule que qgis.png et qgis_copie.png ont le même hash
        # mais qgis_backup.png a un hash différent (c'est une autre image)
        def fake_hash(url: str, **kwargs) -> str:
            if "qgis_backup" in url:
                return "hash_different_aaa"
            if "qgis" in url:
                return "hash_identique_bbb"
            if "carte" in url:
                return "hash_carte_ccc"
            return "hash_inconnu"

        mock_hash.side_effect = fake_hash

        duplicates = find_duplicate_images(
            images_dict=SAMPLE_IMAGES_DICT,
            cdn_base_url="https://cdn.geotribu.fr/",
            cdn_base_path="img",
            check_content=True,
        )

        # qgis.png et qgis_copie.png sont de vrais doublons
        # qgis_backup.png est différent → non inclus
        # carte.png et carte_dupliquee.png : même hash → vrais doublons
        self.assertEqual(len(duplicates), 2)

        flat_duplicates = [path for group in duplicates for path in group]
        self.assertIn("logos-icones/qgis.png", flat_duplicates)
        self.assertIn("logos-icones/qgis_copie.png", flat_duplicates)
        # qgis_backup a un hash différent : il ne doit PAS être dans les doublons
        self.assertNotIn("logos-icones/qgis_backup.png", flat_duplicates)

    @patch("geotribu_cli.images.images_duplicates.compute_remote_image_hash")
    def test_find_no_true_duplicates_when_hashes_differ(self, mock_hash):
        """Même dimensions mais hash différents → pas de vrai doublon."""
        # Chaque image a un hash unique, malgré les mêmes dimensions
        mock_hash.side_effect = lambda url, **kwargs: f"unique_hash_{url}"

        duplicates = find_duplicate_images(
            images_dict=SAMPLE_IMAGES_DICT,
            cdn_base_url="https://cdn.geotribu.fr/",
            cdn_base_path="img",
            check_content=True,
        )

        self.assertEqual(duplicates, [])

    @patch("geotribu_cli.images.images_duplicates.compute_remote_image_hash")
    def test_hash_failure_does_not_crash(self, mock_hash):
        """Si le calcul de hash échoue pour une image, on continue sans planter."""
        # La première image retourne None (échec réseau par exemple)
        mock_hash.side_effect = [None, "hash_ok_111", "hash_ok_111"]

        duplicates = find_duplicate_images(
            images_dict={
                "img_a.png": [100, 100],
                "img_b.png": [100, 100],
                "img_c.png": [100, 100],
            },
            cdn_base_url="https://cdn.geotribu.fr/",
            cdn_base_path="img",
            check_content=True,
        )

        # img_a a échoué → ignorée. img_b et img_c ont le même hash → 1 groupe
        self.assertEqual(len(duplicates), 1)
        self.assertIn("img_b.png", duplicates[0])
        self.assertIn("img_c.png", duplicates[0])


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
