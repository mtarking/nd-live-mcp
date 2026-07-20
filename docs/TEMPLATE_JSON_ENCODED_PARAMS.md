# ND Config Templates — Parameters That Require JSON Encoding

## Summary

Some Nexus Dashboard (`/api/v1/manage/configTemplates`) template parameters must be passed to
the API as a **JSON-encoded string** rather than a bare scalar value. This is not arbitrary —
it is driven entirely by the parameter's **type**. Scalar parameters (`string`, `integer`,
`enum`, ...) are passed inline; **composite** parameters (structures and arrays) carry a
nested object/list value and therefore must be serialized.

The worked example below is the `ip_acl` template, whose `ACES` parameter triggers this
behavior.

## Worked example: `ip_acl`

- **templateType:** `policy`
- **templateSubType:** `device`
- **contentType:** `pythonCli`
- **description:** Template to configure an IPv4 Access-list (ACL)

### The parameter in question is `ACES` (not "ACS")

In the template DSL (`##template variables` block) the parameter is declared as an **array of a
struct**:

```c
@(IsMandatory=true, DisplayName="Access List Items")
struct ITEM {
  enum   ACTION            { validValues=permit,deny,remark; defaultValue=permit; };
  long   SEQUENCE_NUMBER   { min=1; max=4294967295; };
  enum   PROTOCOL          { validValues=icmp,ip,tcp,udp,eigrp,ospf,pim,igmp,custom; ... };
  integer CUSTOM_PROTOCOL  { min=0; max=255; };
  string SRC_IP            { regularExpr=...; };
  ... many more nested fields ...
} ACES[];          // <-- the [] makes ACES an ARRAY of the ITEM struct
```

The `struct { ... } ACES[];` construct is what makes `ACES` composite. The template's Python
body confirms it expects a serialized structure and then deserializes it:

```python
aces, acl_name = normalize_param()
ace_list = ast.literal_eval(aces)      # parses the encoded structure
for item in ace_list.get("ACES"):      # iterates the array of ACE objects
    ...
```

The other two parameters in the same template are plain scalars and are passed inline:

- `ACL_NAME` → `parameterType: string`
- `SERIAL_NUMBER` → `parameterType: string` (internal)

## The reliable signal — `parameterType`

The ND API exposes structured parameter metadata for every template at
`GET /api/v1/manage/configTemplates/{name}` under the `parameters` array. Each parameter object
looks like this:

```jsonc
// scalar — passed inline
{ "name": "ACL_NAME", "parameterType": "string", "structureParameters": {} }

// composite — MUST be JSON-encoded
{
  "name": "ACES",
  "parameterType": "structureArray",
  "structureParameters": { "ACTION": {...}, "SEQUENCE_NUMBER": {...}, ... }
}
```

**A parameter requires JSON encoding when it is a composite type.** Detect it with any of these
(the script uses all of them for safety):

| Condition | Meaning |
| --- | --- |
| `parameterType` contains `structure` (e.g. `structure`, `structureArray`) | struct / array-of-struct |
| `parameterType` ends with `[]` or contains `array` | array-valued parameter |
| `structureParameters` is a non-empty object | nested fields present ⇒ composite |

Everything else (`string`, `integer`, `long`, `boolean`, `enum`, `ipV4Address`, ...) is a
scalar and is passed as a bare value.

## Do NOT key off the parameter name

`ACES`/`ITEM` are specific to `ip_acl`. The name means nothing — always classify by
`parameterType` / `structureParameters`.

## Enumerating every affected template

Use [`scripts/find_json_encoded_params.py`](../scripts/find_json_encoded_params.py). It:

1. lists all templates (`/configTemplates`),
2. fetches each one's detail,
3. flags every parameter whose type is composite, and
4. prints (and optionally writes) a report of `template -> [composite params]`.

Run it (reuses the same `ND_*` env vars as the `nd-live` MCP server):

```bash
cd nd-live-mcp
ND_HOST="https://<nd>" ND_USERNAME="admin" ND_PASSWORD="****" ND_VERIFY_TLS="false" \
  .venv/bin/python scripts/find_json_encoded_params.py --output-md scripts/json_encoded_params_report.md
```
