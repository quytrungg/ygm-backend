import uuid


class S3UUIDPrefixKey:
    """Generate key from prefix and UUID."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, filename: str) -> str:
        """Return prefixed S3 key.

        Example:
            prefix/a13d0a2e-8391-4d95-8dae-fe312f2769a1/file.jpg

        """
        return f"{self.prefix}/{uuid.uuid4()}/{filename.split('/')[-1]}"
