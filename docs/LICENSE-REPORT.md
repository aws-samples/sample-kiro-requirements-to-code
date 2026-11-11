# Third-Party License Report

Generated 2026-11-06 with [pip-licenses](https://github.com/raimon49/pip-licenses) 5.x
against a clean Python 3.12.12 virtualenv per example, installing only the **runtime**
dependency set (no dev/test extras). Versions are what the declared ranges resolved to
on that date; re-run the command at the bottom before relying on exact versions.

**Result:** every runtime dependency in both examples is under a permissive licence
(MIT, BSD, Apache-2.0, PSF-2.0, MIT-0, or MPL-2.0 for `certifi` only). No GPL, LGPL,
AGPL, SSPL, or unknown licences were found.

---

## Example 1: TaskFlow (FastAPI / PyJWT / Cognito)

Source of truth: `examples/example-1-saas-platform/pyproject.toml` `[project].dependencies`.

| Licence | Count |
|---|---|
| MIT / MIT License | 10 |
| BSD-3-Clause / BSD License | 6 |
| Apache-2.0 | 1 |
| Apache-2.0 OR BSD-3-Clause | 1 |
| MIT-0 | 1 |
| PSF-2.0 | 1 |
| MPL-2.0 | 1 |

| Name | Version | Licence | URL |
|---|---|---|---|
| fastapi | 0.162.3 | MIT | https://github.com/fastapi/fastapi |
| starlette | 1.10.0 | BSD-3-Clause | https://github.com/Kludex/starlette |
| PyJWT | 2.15.1 | MIT | https://github.com/jpadilla/pyjwt |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| pydantic | 2.14.3 | MIT | https://github.com/pydantic/pydantic |
| pydantic_core | 2.50.4 | MIT | https://github.com/pydantic |
| pydantic-settings | 2.16.2 | MIT | https://github.com/pydantic/pydantic-settings |
| httpx | 0.28.1 | BSD License | https://github.com/encode/httpx |
| httpcore | 1.0.9 | BSD-3-Clause | https://www.encode.io/httpcore/ |
| h11 | 0.16.0 | MIT License | https://github.com/python-hyper/h11 |
| anyio | 4.16.0 | MIT | https://anyio.readthedocs.io/en/stable/versionhistory.html |
| idna | 3.20 | BSD-3-Clause | https://github.com/kjd/idna |
| certifi | 2026.10.23 | MPL-2.0 | https://github.com/certifi/python-certifi |
| cffi | 2.1.1 | MIT-0 | https://cffi.readthedocs.io/en/latest/whatsnew.html |
| pycparser | 3.12 | BSD-3-Clause | https://github.com/eliben/pycparser |
| python-dotenv | 1.2.4 | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| annotated-doc | 0.0.5 | MIT | https://github.com/fastapi/annotated-doc |
| annotated-types | 0.8.0 | MIT | https://github.com/annotated-types/annotated-types |
| typing-inspection | 0.4.5 | MIT | https://github.com/pydantic/typing-inspection |
| typing_extensions | 4.16.0 | PSF-2.0 | https://github.com/python/typing_extensions |
| opentelemetry-api | 1.45.2 | Apache-2.0 | https://github.com/open-telemetry/opentelemetry-python/tree/main/opentelemetry-api |

Note on `certifi` (MPL-2.0): a transitive dependency of `httpx`. MPL-2.0 is a
file-level copyleft; it obliges you to publish modifications to `certifi`'s own
files, not to your application. Using it unmodified carries no disclosure obligation.

## Example 2: StreamProcess (Lambda / Powertools)

Source of truth: `examples/example-2-data-pipeline/src/functions/ingest/requirements.txt`
(exact pins: `aws-lambda-powertools[tracer]==3.34.0`, `pydantic==2.13.4`, `uuid7==0.1.0`).

| Licence | Count |
|---|---|
| MIT / MIT License | 8 |
| Apache-2.0 / Apache Software License | 2 |
| Apache Software License; BSD License (dual) | 1 |
| BSD-2-Clause | 1 |
| MIT; MIT-0 (dual) | 1 |
| PSF-2.0 | 1 |

| Name | Version | Licence | URL |
|---|---|---|---|
| aws_lambda_powertools | 3.34.0 | MIT; MIT-0 | https://github.com/aws-powertools/powertools-lambda-python |
| aws-xray-sdk | 2.16.0 | Apache Software License | https://github.com/aws/aws-xray-sdk-python |
| botocore | 1.43.127 | Apache-2.0 | https://github.com/boto/botocore |
| pydantic | 2.13.4 | MIT | https://github.com/pydantic/pydantic |
| pydantic_core | 2.46.4 | MIT | https://github.com/pydantic |
| uuid7 | 0.1.0 | MIT License | https://github.com/stevesimmons/uuid7 |
| urllib3 | 2.8.0 | MIT | https://github.com/urllib3/urllib3/blob/main/CHANGES.rst |
| jmespath | 1.1.0 | MIT License | https://github.com/jmespath/jmespath.py |
| python-dateutil | 2.9.0.post0 | Apache Software License; BSD License | https://github.com/dateutil/dateutil |
| six | 1.17.0 | MIT License | https://github.com/benjaminp/six |
| wrapt | 2.5.2 | BSD-2-Clause | https://github.com/GrahamDumpleton/wrapt |
| annotated-types | 0.8.0 | MIT | https://github.com/annotated-types/annotated-types |
| typing-inspection | 0.4.5 | MIT | https://github.com/pydantic/typing-inspection |
| typing_extensions | 4.16.0 | PSF-2.0 | https://github.com/python/typing_extensions |

`boto3` is not listed because the Lambda runtime provides it; `botocore` appears only
because `aws-xray-sdk` declares it.

---

## Scope and caveats

- **Runtime only.** Dev/test tooling (pytest, ruff, mypy, pytest-asyncio, and the
  `cryptography` dev pin in example-1) is excluded; it never ships.
- **Python only.** Terraform providers (`hashicorp/aws`, MPL-2.0), GitHub Actions, and
  MCP servers (`@modelcontextprotocol/server-github` MIT, `@tiberriver256/mcp-server-azure-devops`
  MIT, `awslabs.aws-documentation-mcp-server` Apache-2.0) are not in this report.
- **Point in time.** Example-1 uses version ranges, so the resolved set drifts.
  Example-2 is exactly pinned and will not drift until `requirements.txt` changes.
- Licence strings are whatever each package declares in its metadata; pip-licenses
  does not normalise `"MIT"` vs `"MIT License"`, hence the paired rows above.

## Regenerate

```bash
PY=python3.12   # must match requires-python
# Example 1
uv venv -p $PY /tmp/lic-e1 && uv pip install -p /tmp/lic-e1/bin/python examples/example-1-saas-platform pip-licenses
/tmp/lic-e1/bin/pip-licenses --python /tmp/lic-e1/bin/python --format=markdown --with-urls --order=license \
  --ignore-packages pip-licenses prettytable wcwidth taskflow-auth
# Example 2
uv venv -p $PY /tmp/lic-e2 && uv pip install -p /tmp/lic-e2/bin/python -r examples/example-2-data-pipeline/src/functions/ingest/requirements.txt pip-licenses
/tmp/lic-e2/bin/pip-licenses --python /tmp/lic-e2/bin/python --format=markdown --with-urls --order=license \
  --ignore-packages pip-licenses prettytable wcwidth
```

Add `--fail-on 'GPL;AGPL;LGPL;SSPL'` to either command to turn this into a CI gate.
