from functools import cached_property
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from home_scraper.config import settings


class S3:
    @cached_property
    def bucket(self):
        s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=settings.storage.aws.iam_access_key_id,
            aws_secret_access_key=settings.storage.aws.iam_secret_access_key,
        )
        return s3_resource.Bucket(settings.storage.aws.bucket_name)

    def download_file(self, s3_path: Path, local_path: Path):
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

    def upload_file(self, s3_path: str | Path, local_path: Path):
        """
        Upload a file to S3.

        Args:
            s3_path: path to file on S3
            local_path: path to file relative from repo's root directory
        """
        self.bucket.upload_file(str(local_path), str(s3_path))
