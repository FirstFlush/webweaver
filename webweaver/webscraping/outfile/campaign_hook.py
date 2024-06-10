import importlib.util
import logging
import pandas as pd
from pathlib import Path
import types

from webweaver.exceptions import OutFileHookModuleError, OutFileHookInvalidReturn
from webweaver.webscraping.campaigns.models import ScrapeJob


logger = logging.getLogger('scraping')


class CampaignHook:

    def __init__(self, hook_file:Path, scrape_job_id:int, dataframes:dict[str, pd.DataFrame]):
        self.hook_file = hook_file
        self.scrape_job_id = scrape_job_id
        self.dataframes = dataframes


    async def run_hook(self):
        """Load a python module from the hook file and import+call its outfile_hook() function."""
        hook_module = self.load_campaign_hook_module()
        try:
            dataframes = await self.call_campaign_hook(hook_module)
        except Exception as e:
            logger.error(OutFileHookModuleError(f"OutFileHookModuleError(JobID {self.scrape_job_id}): {e.__class__.__name__} {e}"))
            raise OutFileHookModuleError(e)
        if self.is_valid_dataframes_dict(dataframes):
            self.dataframes = dataframes
        else:
            msg = f"OutFileHookInvalidReturn: {self.hook_file}"
            logger.error(OutFileHookInvalidReturn(msg))
            raise OutFileHookInvalidReturn


    async def call_campaign_hook(self, outfile_hook_module:types.ModuleType) -> dict[str, pd.DataFrame]:
        """Hook to check if any custom post-processing is
        required before saving the data to an outfile.
        """
        try:
            dataframes = await outfile_hook_module.outfile_hook(self.dataframes)
        except Exception as e:
            raise e
        return dataframes


    @staticmethod
    async def campaign_hook_file(scrape_job:ScrapeJob) -> Path | None:
        """Returns the full path of the campaign hook file, 
        if indeed it exists.
        """
        dir_path:Path = f"{await scrape_job.module_dir_path()}"
        hook_file_path = dir_path / Path('outfile_hook.py')
        if hook_file_path.exists():
            return hook_file_path
        else:
            return None


    def load_campaign_hook_module(self) -> types.ModuleType:
        """Loads the campaign hook file as a Python module"""
        spec = importlib.util.spec_from_file_location("outfile_hook", self.hook_file)
        outfile_hook_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(outfile_hook_module)
        return outfile_hook_module


    def is_valid_dataframes_dict(self, dataframes:dict[str, pd.DataFrame]) -> bool:
        """After a campaign's outfile hook is called, this function validates
        the data to make sure it is still of the correct type: dict[str, pd.DataFrame].
        """
        if not isinstance(dataframes, dict):
            return False
        return all(isinstance(key, str) and isinstance(value, pd.DataFrame) for key, value in dataframes.items())
