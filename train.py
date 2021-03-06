import argparse
import warnings

from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.trainer import Trainer
from pytorch_lightning.loggers import test_tube

import models

warnings.filterwarnings("ignore")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["srcnn", "srgan"], required=True)
    parser.add_argument("--scale_factor", type=int, default=4)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--patch_size", type=int, default=96)
    parser.add_argument("--gpus", type=str, default="0")
    opt = parser.parse_args()

    # load model class
    if opt.model == "srcnn":
        model = models.SRCNNModel
    elif opt.model == "srgan":
        model = models.SRGANModel
    else:
        raise RuntimeError(opt.model)

    # add model specific arguments to original parser
    parser = model.add_model_specific_args(parser)
    opt = parser.parse_args()

    # instantiate experiment
    exp = test_tube.TestTubeLogger(save_dir=f"./logs/{opt.model}")
    exp.experiment.argparse(opt)

    model = model(opt)

    # define callbacks
    checkpoint_callback = ModelCheckpoint(
        filepath=exp.experiment.get_media_path(exp.name, exp.version),
    )

    # instantiate trainer
    trainer = Trainer(
        logger=exp,
        max_nb_epochs=4000,
        row_log_interval=50,
        check_val_every_n_epoch=10,
        checkpoint_callback=checkpoint_callback,
        gpus=[int(i) for i in opt.gpus.split(",")]
        if opt.gpus != "-1"
        else None,
    )

    # start training!
    trainer.fit(model)


if __name__ == "__main__":
    main()
