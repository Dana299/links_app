from urllib.parse import parse_qsl, urlparse

from src.schemes.web_resources import ResourceNoUUIDSchema


def parse_url(url: str) -> ResourceNoUUIDSchema:
    """Exctracts protocol, domain, domain zone, path and query params from a given url."""
    parsed_url = urlparse(url)

    domain = parsed_url.netloc
    domain_zone = domain.split(".")[-1]
    path = parsed_url.path
    protocol = parsed_url.scheme
    query_params = parse_qsl(parsed_url.query)

    return ResourceNoUUIDSchema(
        full_url=url,
        protocol=protocol,
        domain=domain,
        domain_zone=domain_zone,
        url_path=path,
        query_params=query_params,
    )
