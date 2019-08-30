import inspect
from argparse import Namespace

import manimlib

LOW_QUALITY = "low"
MEDIUM_QUALITY = "medium"
HIGH_QUALITY = "high"
PRODUCTION_QUALITY = "production"

ARGS = dict(color=None,
            file='',
            file_name=None,
            high_quality=False,
            leave_progress_bars=True,
            livestream=False,
            low_quality=False,
            media_dir='',
            medium_quality=False,
            preview=True,
            quiet=False,
            resolution=None,
            frame_rate=None,
            save_as_gif=False,
            save_last_frame=False,
            save_pngs=False,
            scene_names=[],
            show_file_in_finder=False,
            sound=False,
            start_at_animation_number=None,
            tex_dir='',
            to_twitch=False,
            transparent=False,
            twitch_key=None,
            video_dir='',
            video_output_dir=None,
            write_all=False,
            write_to_movie=False)


def make_scene(scene,
               preview=True,
               frame_rate=None,
               video_dir="",
               tex_dir="",
               media_dir="",
               quality="low",
               **custom_args):
    """
    Allows for manim scenes to be built directly from python script instead of the terminal.
    The scene class is called directly, which allows easy debugging.
    :param scene: Scene to be rendered
    :param preview: Should the resulting video be opened in media player after it is finished?
    :param video_dir: Directory for video output
    :param tex_dir: Directory for tex output
    :param quality: "low", "medium", "high", "production"
    :param custom_args: Other arguments in ARGS dictionary
    """

    FORBIDDEN_CUSTOM_ARGS = [
        "file", "scene_names", "low_quality", "medium_quality", "high_quality",
    ]

    args = dict(ARGS)
    args["file"] = inspect.getfile(scene)
    args["scene_names"].append(scene.__name__)

    for arg in FORBIDDEN_CUSTOM_ARGS:
        custom_args.pop(arg, None)

    args.update({
        "video_dir": video_dir,
        "tex_dir": tex_dir,
        "media_dir": media_dir,
        "preview": preview,
        "frame_rate": frame_rate
    })

    quality = quality.lower()

    if quality == LOW_QUALITY:
        args["low_quality"] = True
    elif quality == MEDIUM_QUALITY:
        args["medium_quality"] = True
    elif quality == HIGH_QUALITY:
        args["high_quality"] = True

    args.update(custom_args)

    config = manimlib.config.get_configuration(Namespace(**args))
    manimlib.constants.initialize_directories(config)
    manimlib.extract_scene.main(config)
