# nd-native-templates-to-nac

Tooling and artifacts for turning **Nexus Dashboard (ND) native config templates**
into an explicit **Network as Code (NaC-ND)** data model.

Many ND config templates accept **JSON-encoded** parameters — values that are
really a struct or an array of structs, but are passed to the API as a single
encoded string (e.g. the `ACES` parameter of the `ip_acl` template). Those opaque
blobs are hard to author and review by hand. This repo:

1. **detects** which templates have such composite parameters,
2. **models** them as an explicit, structured Yamale schema aligned to
   `nac-nd/schemas/schema.yaml`, and
3. documents the methodology and design decisions.

The data is sourced **read-only** from a live ND (`GET /api/v1/manage/configTemplates`),
ND v4.2.1.

---

## What's here

| File | What it is |
| --- | --- |
| `json_encoded_params_report.md` / `.json` | Full scan: **all** templates that expose a composite (JSON-encoded) parameter. |
| `json_encoded_params_policy_device.md` / `.json` | The subset in scope: **39** templates with `templateType=POLICY`, `templateSubType=DEVICE`. |
| `policy_device_nested.json` | Intermediate dump of the nested field structure for the 39 templates. |
| `policy_device_templates.proposal.yaml` | **The deliverable** — the NaC-ND (Yamale) data-model proposal: 39 template maps + struct include definitions. |
| `policy_device_templates.proposal.md` | Design & implementation notes for the proposal (why each modeling choice was made). |

### Toolchain (scripts)

| Script | Role |
| --- | --- |
| `find_json_encoded_params.py` | Enumerates the template library and flags composite parameters. Produces the report `.md`/`.json`. |
| `gen_policy_device_model.py` | Generates the Yamale proposal from live ND (API metadata + DSL fallback). |
| `nd_template_dsl.py` | Minimal parser for the ND template `content` DSL. Recovers nested struct fields the API metadata does not expand. |

---

## How a parameter is classified

A parameter is treated as **JSON-encoded** (and therefore modeled) when its
`parameterType` is a structure or a JSON array:

| `parameterType` | Meaning | Modeled as |
| --- | --- | --- |
| `structureArray` | JSON array of objects | `list(include('<map>_<param>'))` |
| `struct` | JSON object | `include('<map>_<param>')` |
| `string[]`, `ipAddress[]` | JSON array of scalars | `list(str())` |

String-*syntax* composites (`ipAddressList`, `integerRange`, `interfaceRange`) are
a single formatted string on the wire, so they are modeled as scalar `str()`.

Full type-mapping, naming (`snake_case`), `required` semantics, and enum handling
are documented in `policy_device_templates.proposal.md`.

### Nested structs: API depth limit + DSL fallback

The ND API metadata (`parameters[].structureParameters`) only expands **one** level
of `structureArray` nesting. Deeper structs (e.g.
`route_map_enhanced.entries[].ruleEntries[]`, the `sgm` group/policy sub-lists)
come back with no fields. `nd_template_dsl.py` recovers those from the template's
raw `content` DSL. The parser is validated against a case the API *does* expose
(`ip_acl.ACES`) — its field set matches the API exactly.

---

## Regenerate

The generators read a live ND, read-only, via `ND_*` environment variables.

```bash
# 1) Scan the whole template library for composite params:
ND_HOST=https://<nd-host> ND_DOMAIN=<domain> ND_USERNAME=<user> ND_PASSWORD=<pass> \
ND_VERIFY_TLS=false \
  python find_json_encoded_params.py --output-md json_encoded_params_report.md \
                                     --output-json json_encoded_params_report.json

# 2) Generate the NaC-ND proposal for the 39 policy/device templates:
ND_HOST=https://<nd-host> ND_DOMAIN=<domain> ND_USERNAME=<user> ND_PASSWORD=<pass> \
ND_VERIFY_TLS=false \
  python gen_policy_device_model.py

# 3) Validate the generated schema with Yamale:
python -m pip install yamale
python -c "import yamale; yamale.make_schema('policy_device_templates.proposal.yaml'); print('YAMALE_SCHEMA_OK')"
```

> The scripts reuse the read-only `nd` client from the `nd-live-mcp` project. Set
> `PYTHONPATH` to that project (or run them from within it) so `import nd` resolves.

Current output: **39** template maps + **50** struct include definitions; schema
loads clean (`YAMALE_SCHEMA_OK`).

---

## Scope & status

- **Proposal only.** The generated schema is a review artifact — it is **not**
  wired into `nac-nd/schemas/schema.yaml`.
- **In scope:** `POLICY` / `DEVICE` templates with composite parameters.
- **Out of scope:** other template types (profile / fabric / report), regex/format
  tightening on ip/interface/mac fields (kept as conservative `str()`), and
  value-conditional validation (belongs in `nac-validate`, not Yamale).

---

## Security

ND access is **read-only** (`GET` only). Credentials are supplied via environment
variables — do not commit them. `ND_VERIFY_TLS=false` is for lab use; enable TLS
verification against production controllers.
