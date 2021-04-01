import os
import pathlib
from copy import deepcopy

import comet_ml  # pylint: disable=unused-import
import ptvsd
import pytorch_lightning as pl
import typer
import wandb
from pytorch_lightning.loggers import CometLogger, WandbLogger
from rivernet.datasets import RDataset
from rivernet.systems import System
from rivernet.utils.parsing import yaml_to_params
from torch.utils.data import DataLoader

app = typer.Typer()


@app.command()
def train(config_path: str, overrides: str = '', debug: bool = False):
    """Train a model."""
    if debug:
        ptvsd.enable_attach(address=('0.0.0.0', 5678))
        ptvsd.wait_for_attach()

    params = yaml_to_params(config_path, overrides)
    config_dir = os.path.dirname(config_path)
    # serialization_dir = os.path.join(config_dir, 'serialization')

    wandb_opts = params.pop('wandb').as_dict()
    wandb_logger = WandbLogger(save_dir=config_dir,
                               mode='online',
                               config=deepcopy(params.as_dict()),
                               **wandb_opts)
    code_artifact = wandb.Artifact('rivernet', type='code')
    code_artifact.add_dir('rivernet')
    wandb_logger.experiment.log_artifact(code_artifact)

    train_params = params['train_data_loader']
    train_loader = DataLoader(RDataset.from_params(train_params.pop('dataset')),
                              **train_params.as_dict())

    valid_params = params['valid_data_loader']
    valid_loader = DataLoader(RDataset.from_params(valid_params.pop('dataset')),
                              **valid_params.as_dict())

    # comet_logger = CometLogger(
    #     api_key=os.environ.get('COMET_API_KEY'),
    #     workspace=os.environ.get('COMET_WORKSPACE'),
    #     save_dir=serialization_dir,
    #     log_code=False,
    #     **params.pop('comet').as_dict(),
    # )

    # Assume the script is run from project root directory
    # comet_logger.experiment.log_code(config_path)
    # for path in pathlib.Path('rivernet').rglob('*.py'):
    #     comet_logger.experiment.log_code(path)

    system = System.from_params(params['system'])

    trainer = pl.Trainer(logger=wandb_logger,
                         **params.pop('trainer').as_dict())
    trainer.fit(system, train_loader, valid_loader)

    # result = trainer.test(ts_ode, test_loader)


@app.command()
def test(config_path: str, overrides: str = '', debug: bool = False):
    """Test a model."""
    print('test')


if __name__ == "__main__":
    app()
