import os
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path


def get_save_dir(config_path):
    """Determine the path where the experimental results will be saved."""
    parts = str(config_path).split('/')
    i = parts.index('experiments')
    root_dir = os.path.expandvars('$SM_MODEL_DIR')
    save_dir = os.path.join(root_dir, *parts[i+1:-1])
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    return save_dir


def get_experiment_id(checkpoint_id, trial, save_dir, resume):
    chkpt_dir = Path(save_dir) / 'checkpoints'
    if resume and not checkpoint_id and chkpt_dir.exists:
        paths = chkpt_dir.glob('*/last.ckpt')
        checkpoint_id = next(paths).parent.name
    now = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    return checkpoint_id or f'trial-{trial}-{now}'


def import_string(dotted_path):
    """Import a dotted module path.

    And return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Adatped from https://stackoverflow.com/a/34963527/3790116.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as e:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError.with_traceback(ImportError(msg), sys.exc_info()[2])

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        raise ImportError.with_traceback(ImportError(msg), sys.exc_info()[2])
