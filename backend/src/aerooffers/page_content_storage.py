import os
from datetime import datetime, UTC

from azure.storage.blob import BlobServiceClient, ContentSettings

from aerooffers.my_logging import logging

logger = logging.getLogger("page_content_storage")

_blob_service_client: BlobServiceClient | None = None
_container_name = "offer-pages"


def _get_blob_service_client() -> BlobServiceClient:
    global _blob_service_client
    if _blob_service_client is not None:
        return _blob_service_client

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING environment variable is required"
        )

    _blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    logger.info("BlobServiceClient initialized successfully")
    return _blob_service_client


def store_page_content(offer_id: str, page_content: str, url: str) -> None:
    try:
        blob_client = _get_blob_service_client().get_blob_client(
            container=_container_name, blob=offer_id
        )

        blob_client.upload_blob(
            data=page_content,
            overwrite=True,
            content_settings=ContentSettings(content_type="text/html; charset=utf-8"),
            metadata={
                "url": url,
                "stored_at": datetime.now(UTC).isoformat(),
            },
        )
        logger.debug(f"Stored page_content for offer_id: {offer_id}")
    except Exception as e:
        logger.error(f"Could not upload page content for offer {offer_id}", e)
