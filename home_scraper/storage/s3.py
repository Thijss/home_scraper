import io
from functools import cached_property
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from home_scraper.config import settings
from home_scraper.scraping.model import Home


class S3:

    @cached_property
    def bucket(self):
        resource = boto3.resource(
            "s3",
            aws_access_key_id=settings.storage.aws.iam_access_key_id,
            aws_secret_access_key=settings.storage.aws.iam_secret_access_key,
        )
        return resource.Bucket(settings.storage.aws.bucket_name)

    def download_to_file(self, s3_path: Path, local_path: Path) -> Path:
        """
        Download a file from S3.

        Args:
            s3_path: path to file on S3
            local_path: path to file relative from repo's root directory
        """
        local_dir = local_path.parent
        local_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.bucket.download_file(str(s3_path), str(local_path))
        except ClientError as error:
            if error.response["Error"]["Code"] == "404":
                raise FileNotFoundError from error
            raise error
        return local_path

    def download_to_memory(self, s3_path: Path) -> io.BytesIO:
        """
        Download a file from S3.

        Args:
            s3_path: path to file on S3
        """

        data_stream = io.BytesIO()

        try:
            self.bucket.download_fileobj(
                str(s3_path),
                data_stream)
        except ClientError as error:
            if error.response["Error"]["Code"] == "404":
                raise FileNotFoundError from error
            raise error
        data_stream.seek(0)
        return data_stream

    def upload_from_memory(self, s3_path: str | Path, buffer: io.BytesIO):
        """
        Upload a file to S3.

        Args:
            s3_path: path to file on S3
            buffer: bytes object
        """
        buffer.seek(0)
        self.bucket.upload_fileobj(buffer, str(s3_path))


def download_homes_from_s3(file_name: str) -> set[Home]:
    try:
        data_stream = S3().download_to_memory(s3_path=file_name)
    except FileNotFoundError:
        return set()
    homes = {Home.parse_raw(data) for data in data_stream.readlines()}
    return homes


def upload_homes_to_s3(s3_path: str, homes: set[Home]):
    buffer = io.BytesIO()

    json_strings = [home.json() for home in homes]

    buffer.writelines([str.encode(json + "\n") for json in json_strings])
    S3().upload_from_memory(s3_path=s3_path, buffer=buffer)
