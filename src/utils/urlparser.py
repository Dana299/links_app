from urllib.parse import parse_qsl, urlparse

from src.schemes.web_resources import ResourceBaseSchema


def parse_url(url: str) -> ResourceBaseSchema:
    """Exctracts protocol, domain, domain zone, path and query params from a given url."""
    parsed_url = urlparse(url)

    # TODO: add scheme for resource withoud UUID

    domain = parsed_url.netloc
    domain_zone = domain.split(".")[-1]
    path = parsed_url.path
    protocol = parsed_url.scheme
    query_params = parse_qsl(parsed_url.query)

    return ResourceBaseSchema(
        protocol=protocol,
        domain=domain,
        domain_zone=domain_zone,
        url_path=path,
        query_params=query_params,
    )
