# from dataclasses import dataclass
import logging
import pandas as pd
from pathlib import Path
from dataclasses import dataclass

from webweaver.exceptions import OutFileFormatNotFound, OutFileHookModuleError, OutFileHookInvalidReturn
from webweaver.common.enums import FileFormatEnum
from webweaver.webscraping.outfile.campaign_hook import CampaignHook
from webweaver.webscraping.campaigns.models import ScrapeJob
from webweaver.webscraping.models import ScrapeModel


logger = logging.getLogger('scraping')


class OutFileData:

    def __init__(self, scrape_job:ScrapeJob, file_format:FileFormatEnum):
        self.scrape_job = scrape_job
        self.time_scraped = self.scrape_job.date_scraped.strftime("%Y-%m-%d_%H:%M:%S")
        self.scrape_tables = ScrapeModel.__subclasses__()
        self.dataframes:dict[str, pd.DataFrame] = None
        self.file_format = file_format


    async def build(self):
        """Populate the dataframes attribute with the data scraped 
        by the scrape job and drop any duplicates.
        """
        tables_data = await self._build_tables_data()
        self.dataframes = self._build_dataframes(tables_data)
        for _, df in self.dataframes.items():
            df.drop_duplicates(inplace=True)
        hook_file = await CampaignHook.campaign_hook_file(self.scrape_job)

        if hook_file:
            campaign_hook = CampaignHook(hook_file, self.scrape_job.id, self.dataframes)
            try:
                await campaign_hook.run_hook()
            except (OutFileHookModuleError, OutFileHookInvalidReturn):
                pass
            else:
                self.dataframes = campaign_hook.dataframes


    async def _build_tables_data(self) -> dict[str, list[ScrapeModel]]:
        """Build the dictionary of tables in order to construct our dataframes.
        Removes the scrape_job_id_id value.
        """
        return await self.scrape_job.scraped_data(
            ScrapeModel.__subclasses__(), 
            remove_job_id=True
        )


    def _build_dataframes(self, tables_data:dict[str, list[ScrapeModel]]
            ) -> dict[str, pd.DataFrame]:
        """Convert the tables_data from a dictionary of 
        str:ModelInstance to a dictionary of str:DataFrame
        """
        d = {}
        for table_name, table_data in tables_data.items():
            d[table_name] = pd.DataFrame(table_data)
        return d


@dataclass
class FormatInfo:
    extension: str
    save_function: callable
    multi_tabbed: bool = False


class OutFile:
    """Class for creating outfiles to send to customer"""
    def __init__(self, outfile_data:OutFileData):
        self.outfile_data = outfile_data
        self.FILE_FORMAT_MAP = {
            FileFormatEnum.JSON: FormatInfo("json", self.to_json),
            FileFormatEnum.CSV: FormatInfo("csv", self.to_csv),
            FileFormatEnum.EXCEL: FormatInfo("xlsx", self.to_excel, True),
            FileFormatEnum.GOOGLE_SHEETS: FormatInfo(".xlsx", self.to_google_sheets, True),
            FileFormatEnum.SQL: FormatInfo("dump", self.to_sql_dump, True),
            FileFormatEnum.SQLITE: FormatInfo("sqlite", self.to_sqlite, True),
            FileFormatEnum.FEATHER: FormatInfo("feather", self.to_feather),
            FileFormatEnum.PARQUET: FormatInfo("parquet", self.to_parquet),
            FileFormatEnum.XML: FormatInfo("xml", self.to_xml),
        }
        try:
            self.format_info = self._get_format_mapping(outfile_data.file_format)
        except OutFileFormatNotFound as e:
            chosen_format = self.outfile_data.file_format.value
            job_id = self.outfile_data.scrape_job.id
            logger.error(f"{e.__class__.__name__}: Could not find chosen outfile format {chosen_format} for job #{job_id}")


    def _get_format_mapping(self, file_format:FileFormatEnum) -> FormatInfo:
        """Retrieves the mapping of file_format to extension and callable."""
        try:
            return self.FILE_FORMAT_MAP[file_format]
        except KeyError:
            raise OutFileFormatNotFound


    async def save(self):
        "Save the data to a file, calling the function in File"
        self.dir = await self.dir_path()
        self.format_info.save_function()


    def to_csv(self):
        for table_name, df in self.outfile_data.dataframes.items():
            df.to_csv(self.dir/self.file_name(table_name), index=False)


    def to_google_sheets(self):
        ...

    def to_sqlite(self):
        ...

    def to_sql_dump(self):
        ...

    def to_feather(self):
        for table_name, df in self.outfile_data.dataframes.items():
            df.to_feather(self.dir/self.file_name(table_name))

    def to_parquet(self):
        for table_name, df in self.outfile_data.dataframes.items():
            df.to_parquet(self.dir/self.file_name(table_name))


    def to_json(self):
        for table_name, df in self.outfile_data.dataframes.items():
            df.to_json(self.dir/self.file_name(table_name), orient="records")
        return

    def to_excel(self):
        full_path = self.dir/self.file_name(table_name)
        with pd.ExcelWriter(full_path) as writer:
            for table_name, df in self.outfile_data.dataframes.items():
                df.to_excel(writer, sheet_name=table_name, index=False)
        return

    def to_xml(self):
        for table_name, df in self.outfile_data.dataframes.items():
            df.to_xml(self.dir/self.file_name(table_name), index=False)    

    def to_google_docs(self):
        ...


    async def dir_path(self) -> Path:
        """Return the campaign module directory to save in."""
        return await self.outfile_data.scrape_job.module_scraped_data_path()


    def file_name(self, table_name:str=None) -> Path:
        """Retrieves the campaign directory for this outfile"""
        time_scraped = self.outfile_data.time_scraped
        extension = self.format_info.extension
        if self.format_info.multi_tabbed:
            return Path(f"scraped_data__{time_scraped}.{extension}")
        else:
            return Path(f"scraped_data__{table_name}_{time_scraped}.{extension}")
        
    # async def _full_path(self, table_name:str=None) -> Path:
    #     """Returns the full Path object of the directory to save in (depending on the Campaign), and the
    #     file name to save as.
    #     """
    #     dir_path = await self.dir_path()
    #     return dir_path/self.file_name(table_name)
        

# FILE_FORMAT_MAP = {
#     FileFormatEnum.JSON: FormatInfo(".json", OutFile.to_json),
#     FileFormatEnum.CSV: FormatInfo(".csv", OutFile.to_csv),
#     FileFormatEnum.EXCEL: FormatInfo(".xlsx", self.to_excel, True),
#     FileFormatEnum.GOOGLE_SHEETS: FormatInfo(".xlsx", self.to_google_sheets, True),
#     FileFormatEnum.SQL: FormatInfo("dump", "to_sql_dump"),
# }

