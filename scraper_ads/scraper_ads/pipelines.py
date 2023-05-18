# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperAdsPipeline:
    def process_item(self, item, spider):
        return item


# Create a custom parquet pipeline
import pyarrow as pa
import pyarrow.parquet as pq

class ParquetExportPipeline:
    def __init__(self):
        self.items = []
        self.batch_size = 1280
        self.batch_id = 1

    def process_item(self, item, spider):
        self.items.append(item)
        if len(self.items) >= self.batch_size:
            self.write_items()
        return item

    def close_spider(self, spider):
        if self.items:
            self.write_items()

    def write_items(self):
        table = pa.Table.from_pydict(self.items)
        file_name = f'../data/data_raw/parquet_scrape/scrapy_batch_{self.batch_id}.parquet'
        pq.write_table(table, file_name, compression='gzip')
        self.items = []
        self.batch_id += 1
