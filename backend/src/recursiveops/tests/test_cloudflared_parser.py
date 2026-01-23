from recursiveops.integrations.cloudflared import build_health_targets, parse_cloudflared_yaml


def test_parse_cloudflared_ingress() -> None:
    config = """
tunnel: example
credentials-file: /etc/cloudflared/creds.json
ingress:
  - hostname: app.example.com
    service: http://localhost:3000
  - hostname: "*.example.com"
    service: http://localhost:8080
  - service: http_status:404
"""
    routes = parse_cloudflared_yaml(config)
    assert len(routes) == 3

    assert routes[0].hostname == "app.example.com"
    assert routes[0].service == "http://localhost:3000"

    assert routes[1].hostname == "*.example.com"
    assert routes[1].service == "http://localhost:8080"

    assert routes[2].hostname is None
    assert routes[2].service == "http_status:404"


def test_build_health_targets_skips_wildcards() -> None:
    routes = parse_cloudflared_yaml(
        """
ingress:
  - hostname: app.example.com
    service: http://localhost:3000
  - hostname: "*.example.com"
    service: http://localhost:8080
  - service: http_status:404
"""
    )
    targets = build_health_targets(routes, scheme="https")
    assert targets == [
        {
            "hostname": "app.example.com",
            "service": "http://localhost:3000",
            "url": "https://app.example.com",
        }
    ]
