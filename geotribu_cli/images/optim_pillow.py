#! python3  # noqa: E265

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from pathlib import Path
from typing import Optional

# 3rd party
try:
    from PIL import Image
    from PIL.ImageOps import contain

    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# package
from geotribu_cli.constants import GeotribuDefaults

# ############################################################################
# ########## GLOBALS #############
# ################################

logger = logging.getLogger(__name__)
defaults_settings = GeotribuDefaults()

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def pil_redimensionner_image(
    image_path_or_url: Path,
    output_folder: Path,
    largeur_max_paysage: int = 1000,
    hauteur_max_portrait: int = 600,
) -> Optional[Path]:
    """Redimensionne l'image dont le chemin est passé en entrée en tenant compte d'une
    contrainte de largeur max pour les images orientées paysage (largeur > hauteur) et
    une hauteur max pour les images orientées portrait (hauteur > largeur).

    Args:
        image_path_or_url: chemin ou URL vers l'image
        output_folder: chemin du dossier de sortie
        largeur_max_paysage: largeur maximum pour une image orientée paysage.
            Defaults to 1000.
        hauteur_max_portrait: hauteur maximum pour une image orientée portrait.
            Defaults to 600.

    Returns:
        path to the resized image.
    """
    # Ouvrir l'image
    try:
        img = Image.open(image_path_or_url)
    except Exception as err:
        logger.error(f"Impossible de lire l'image {image_path_or_url}. Trace : {err}")
        return None

    # Vérifier le rapport hauteur/largeur de l'image
    rapport_hauteur_largeur = img.height / img.width

    if rapport_hauteur_largeur > 1:
        # L'image est en mode portrait
        logger.info(f"{image_path_or_url} est orientée PORTRAIT")
        nouvelle_hauteur = min(hauteur_max_portrait, img.height)
        nouvelle_taille = (
            int(nouvelle_hauteur / rapport_hauteur_largeur),
            nouvelle_hauteur,
        )
    else:
        logger.info(f"{image_path_or_url} est orientée PAYSAGE (ou carrée)")
        # L'image est en mode paysage ou carré
        nouvelle_largeur = min(largeur_max_paysage, img.width)
        nouvelle_taille = (
            nouvelle_largeur,
            int(nouvelle_largeur * rapport_hauteur_largeur),
        )

    # Redimensionner l'image
    new_img = contain(img, nouvelle_taille)

    # sauvegarder l'image
    output_filepath = output_folder.joinpath(
        f"{image_path_or_url.stem}_resized_{new_img.width}x"
        f"{new_img.height}{image_path_or_url.suffix}"
    )
    output_filepath.parent.mkdir(parents=True, exist_ok=True)
    new_img.save(output_filepath)
    new_img.close()

    return output_filepath
