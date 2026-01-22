from unittest.mock import MagicMock, patch

from assertpy import assert_that

from aerooffers.page_content_storage import store_page_content


def test_should_store_page_content() -> None:
    # given
    offer_id = "test_offer_id"
    page_content = "<html><body>Test content</body></html>"
    url = "https://test.com/offer"

    with patch(
        "aerooffers.page_content_storage._get_blob_service_client"
    ) as mock_get_client:
        mock_blob_client = MagicMock()
        mock_get_client.return_value.get_blob_client.return_value = mock_blob_client

        # when
        store_page_content(offer_id, page_content, url)

    # then
    mock_get_client.return_value.get_blob_client.assert_called_once_with(
        container="offer-pages", blob=offer_id
    )
    mock_blob_client.upload_blob.assert_called_once()
    call_args = mock_blob_client.upload_blob.call_args
    assert_that(call_args.kwargs["data"]).is_equal_to(page_content)
    assert_that(call_args.kwargs["overwrite"]).is_true()
    assert_that(call_args.kwargs["content_settings"]["content_type"]).is_equal_to(
        "text/html; charset=utf-8"
    )
    assert_that(call_args.kwargs["metadata"]["url"]).is_equal_to(url)
    assert_that(call_args.kwargs["metadata"]).contains_key("stored_at")
