import torch
from openprompt.utils.logging import logger

def model_to_device(model, config):
    r"""
    model: the model to be wrapped
    config: the environment subconfig.
    """
    import os
    if "CUDA_VISIBLE_DEVICES" not in os.environ and config.cuda_visible_devices is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = ",".join([str(i) for i in config.cuda_visible_devices])

    if config.model_parallel:
        if not hasattr(model, "parallelize"):
            raise RuntimeError("The model doesn't has parallelize method.")
        if config.device_map is None:
            model.parallelize()
        else:
            model.parallelize(config.device_map)
        logger.info(
            f"Using model parallel, spread across device map: {model.device_map}"
        )
        return model
    if config.num_gpus>1:
        local_rank_device = f"cuda:{config.local_rank}"
        model = model.to(local_rank_device)
        model = torch.nn.parallel.DataParallel(model, output_device=local_rank_device)
        logger.info("Using DataParallel")
    elif config.num_gpus>0:
        model = model.cuda()
        logger.info("Using cuda of single gpu")
    else:
        logger.info("Using cpu")
    return model