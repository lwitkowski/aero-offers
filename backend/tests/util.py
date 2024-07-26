from scrapy.http import HtmlResponse, Request
import os


def fake_response_from_file(file_name, url=None, encoding='utf8'):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    :param encoding:
    :param encoding:
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url, encoding=encoding)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name

    file_handle = open(file_path, 'r', encoding=encoding)
    file_content = file_handle.read()
    file_handle.close()

    response = HtmlResponse(url=url,
                            request=request,
                            encoding=encoding,
                            body=file_content)
    response.meta["aircraft_type"] = ""
    return response
