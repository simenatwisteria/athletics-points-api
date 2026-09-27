"""Leser og kontrollerer API-kontrakten ``docs/api/openapi.yaml`` (AP-020).

    python scripts/openapi_check.py [sti]

Prosjektet har ingen YAML-pakke, og kontrakten skal ikke kreve nye avhengigheter. Derfor leser
``load_yaml`` et bevisst lite utsnitt av YAML, som kontrakten holder seg innenfor:

- blokk-mappinger (``nøkkel: verdi``) og blokk-lister (``- verdi``), innrykk med mellomrom
- skalarer: tall, ``true``/``false``/``null``, ren tekst, ``"…"`` (JSON-escaping) eller ``'…'``
- flyt-lister med enkle skalarer (``[a, b]``), tomme ``[]`` og ``{}``
- ``|`` og ``|-`` for tekst over flere linjer
- kommentarer bare på egen linje

Alt annet gir ``YamlSubsetError`` i stedet for en feil tolkning.

``check`` kontrollerer strukturen etter OpenAPI 3.1 (påkrevde felt, operasjoner, svar, at alle
``$ref`` finnes) og at hvert eksempel stemmer med skjemaet sitt. Det er ikke en full validator, men
fanger feilene som betyr noe for kontrakten.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs" / "api" / "openapi.yaml"

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
JSON_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}
PARAM_LOCATIONS = {"query", "path", "header", "cookie"}

_KEY = re.compile(
    r'^(?:"((?:[^"\\]|\\.)*)"|([^\s"\'\[\]{}#&*!|>%@`-][^:#]*?|-[^\s:][^:#]*?)):(?: +(.*))?$'
)
_INT = re.compile(r"^-?\d+$")
_FLOAT = re.compile(r"^-?\d+\.\d+(?:[eE][-+]?\d+)?$|^-?\d+[eE][-+]?\d+$")


class YamlSubsetError(ValueError):
    """Teksten bruker YAML utenfor utsnittet ``load_yaml`` forstår."""


# --- YAML-utsnitt --------------------------------------------------------------------------------


def _scalar(text: str, lineno: int) -> Any:
    if text.startswith('"'):
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise YamlSubsetError(f"linje {lineno}: ugyldig tekst i anførselstegn: {text}") from exc
        if not isinstance(value, str):
            raise YamlSubsetError(f"linje {lineno}: forventet tekst: {text}")
        return value
    if text.startswith("'"):
        if len(text) < 2 or not text.endswith("'"):
            raise YamlSubsetError(f"linje {lineno}: uavsluttet '…': {text}")
        return text[1:-1].replace("''", "'")
    if text == "[]":
        return []
    if text == "{}":
        return {}
    if text.startswith("["):
        if not text.endswith("]"):
            raise YamlSubsetError(f"linje {lineno}: uavsluttet liste: {text}")
        return [_scalar(part.strip(), lineno) for part in text[1:-1].split(",")]
    if text[0] in "{&*!|>%@`" or " #" in text:
        raise YamlSubsetError(f"linje {lineno}: utenfor YAML-utsnittet: {text}")
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~"):
        return None
    if _INT.match(text):
        return int(text)
    if _FLOAT.match(text):
        return float(text)
    if ": " in text:
        raise YamlSubsetError(f"linje {lineno}: tekst med ': ' må stå i anførselstegn: {text}")
    return text


class _Parser:
    def __init__(self, text: str) -> None:
        if "\t" in text:
            raise YamlSubsetError("tabulator er ikke tillatt, bruk mellomrom")
        self.lines = [line.rstrip() for line in text.splitlines()]
        self.i = 0

    def _peek(self) -> tuple[int, str] | None:
        while self.i < len(self.lines):
            stripped = self.lines[self.i].strip()
            if stripped and not stripped.startswith("#"):
                line = self.lines[self.i]
                return len(line) - len(line.lstrip(" ")), stripped
            self.i += 1
        return None

    def parse(self) -> Any:
        head = self._peek()
        if head is None:
            return None
        value = self._block(head[0])
        if self._peek() is not None:
            raise YamlSubsetError(f"linje {self.i + 1}: uventet innrykk")
        return value

    def _block(self, indent: int) -> Any:
        head = self._peek()
        assert head is not None
        if head[1] == "-" or head[1].startswith("- "):
            return self._sequence(indent)
        return self._mapping(indent)

    @staticmethod
    def _is_item(text: str) -> bool:
        return text == "-" or text.startswith("- ")

    def _mapping(self, indent: int) -> dict[str, Any]:
        out: dict[str, Any] = {}
        while (head := self._peek()) is not None and head[0] == indent:
            if self._is_item(head[1]):
                break
            match = _KEY.match(head[1])
            if match is None:
                raise YamlSubsetError(f"linje {self.i + 1}: forventet 'nøkkel: verdi': {head[1]}")
            quoted, plain = match.group(1), match.group(2)
            key = json.loads(f'"{quoted}"') if quoted is not None else plain
            if key in out:
                raise YamlSubsetError(f"linje {self.i + 1}: nøkkelen {key!r} finnes allerede")
            lineno = self.i + 1
            self.i += 1
            out[key] = self._value(match.group(3) or "", indent, lineno)
        head = self._peek()
        if head is not None and head[0] > indent:
            raise YamlSubsetError(f"linje {self.i + 1}: uventet innrykk")
        return out

    def _sequence(self, indent: int) -> list[Any]:
        out: list[Any] = []
        while (head := self._peek()) is not None and head[0] == indent:
            if not self._is_item(head[1]):
                break
            item = head[1][1:].strip()
            lineno = self.i + 1
            if item and _KEY.match(item):
                # «- nøkkel: verdi» er en mapping med innrykk to lenger inn.
                self.lines[self.i] = " " * (indent + 2) + item
                out.append(self._mapping(indent + 2))
            else:
                self.i += 1
                out.append(self._value(item, indent, lineno))
        return out

    def _value(self, text: str, indent: int, lineno: int) -> Any:
        if text in ("|", "|-"):
            return self._literal(indent, keep_newline=text == "|")
        if text:
            return _scalar(text, lineno)
        head = self._peek()
        if head is not None and head[0] > indent:
            return self._block(head[0])
        if head is not None and head[0] == indent and self._is_item(head[1]):
            return self._sequence(indent)
        return None

    def _literal(self, indent: int, *, keep_newline: bool) -> str:
        lines: list[str] = []
        block_indent: int | None = None
        while self.i < len(self.lines):
            line = self.lines[self.i]
            current = len(line) - len(line.lstrip(" "))
            if line.strip() and current <= indent:
                break
            if line.strip() and block_indent is None:
                block_indent = current
            lines.append(line[block_indent or 0 :] if line.strip() else "")
            self.i += 1
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + ("\n" if keep_newline else "")


def load_yaml(text: str) -> Any:
    """Tolker YAML-utsnittet beskrevet øverst i fila."""
    return _Parser(text).parse()


def load_spec(path: Path = SPEC) -> dict[str, Any]:
    spec = load_yaml(path.read_text("utf-8"))
    if not isinstance(spec, dict):
        raise YamlSubsetError(f"{path} er ikke en mapping")
    return spec


# --- OpenAPI-kontroll ----------------------------------------------------------------------------


def resolve(spec: dict[str, Any], ref: str) -> Any:
    """Slår opp en lokal ``$ref`` (``#/components/...``). ``KeyError`` hvis den ikke finnes."""
    if not ref.startswith("#/"):
        raise KeyError(ref)
    node: Any = spec
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def _refs(node: Any, path: str) -> list[tuple[str, str]]:
    if isinstance(node, dict):
        found = [(path, node["$ref"])] if isinstance(node.get("$ref"), str) else []
        for key, value in node.items():
            found += _refs(value, f"{path}/{key}")
        return found
    if isinstance(node, list):
        return [ref for i, value in enumerate(node) for ref in _refs(value, f"{path}/{i}")]
    return []


def _type_ok(value: Any, wanted: str) -> bool:
    match wanted:
        case "object":
            return isinstance(value, dict)
        case "array":
            return isinstance(value, list)
        case "string":
            return isinstance(value, str)
        case "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        case "number":
            return isinstance(value, int | float) and not isinstance(value, bool)
        case "boolean":
            return isinstance(value, bool)
        case "null":
            return value is None
    return False


def validate(spec: dict[str, Any], schema: dict[str, Any], value: Any, path: str) -> list[str]:
    """Kontrollerer ``value`` mot et skjema. Dekker bare nøkkelordene kontrakten bruker."""
    if "$ref" in schema:
        return validate(spec, resolve(spec, schema["$ref"]), value, path)
    errors: list[str] = []
    if "oneOf" in schema:
        matches = [s for s in schema["oneOf"] if not validate(spec, s, value, path)]
        if len(matches) != 1:
            errors.append(f"{path}: passer med {len(matches)} av alternativene i oneOf, ikke 1")
    for sub in schema.get("allOf", []):
        errors += validate(spec, sub, value, path)
    types = schema.get("type")
    if types is not None:
        wanted = types if isinstance(types, list) else [types]
        if not any(_type_ok(value, t) for t in wanted):
            return [*errors, f"{path}: forventet {'/'.join(wanted)}, fikk {value!r}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: forventet {schema['const']!r}, fikk {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} er ikke blant {schema['enum']}")
    if isinstance(value, int | float) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} er under minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} er over maksimum {schema['maximum']}")
    if isinstance(value, dict):
        properties: dict[str, Any] = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}: mangler påkrevd felt {name!r}")
        extra = schema.get("additionalProperties", True)
        for name, item in value.items():
            if name in properties:
                errors += validate(spec, properties[name], item, f"{path}.{name}")
            elif extra is False:
                errors.append(f"{path}: ukjent felt {name!r}")
            elif isinstance(extra, dict):
                errors += validate(spec, extra, item, f"{path}.{name}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: færre enn {schema['minItems']} elementer")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: flere enn {schema['maxItems']} elementer")
        if "items" in schema:
            for i, item in enumerate(value):
                errors += validate(spec, schema["items"], item, f"{path}[{i}]")
    return errors


def _check_schema(spec: dict[str, Any], schema: Any, path: str) -> list[str]:
    if not isinstance(schema, dict):
        return [f"{path}: skjema må være en mapping"]
    if "$ref" in schema:
        return []
    errors: list[str] = []
    types = schema.get("type")
    for t in types if isinstance(types, list) else [types] if types else []:
        if t not in JSON_TYPES:
            errors.append(f"{path}: ukjent type {t!r}")
    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in properties:
            errors.append(f"{path}: påkrevd felt {name!r} er ikke beskrevet i properties")
    for name, sub in properties.items():
        errors += _check_schema(spec, sub, f"{path}.{name}")
    for key in ("items",):
        if key in schema:
            errors += _check_schema(spec, schema[key], f"{path}.{key}")
    if isinstance(schema.get("additionalProperties"), dict):
        errors += _check_schema(spec, schema["additionalProperties"], f"{path}.*")
    for key in ("oneOf", "allOf", "anyOf"):
        for i, sub in enumerate(schema.get(key, [])):
            errors += _check_schema(spec, sub, f"{path}.{key}[{i}]")
    return errors


def _check_media(spec: dict[str, Any], media: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    schema = media.get("schema")
    if schema is None:
        return [f"{path}: mangler schema"]
    errors += _check_schema(spec, schema, f"{path}.schema")
    examples = media.get("examples", {})
    if not examples:
        errors.append(f"{path}: mangler eksempler")
    for name, example in examples.items():
        if "value" not in example:
            errors.append(f"{path}.examples.{name}: mangler value")
            continue
        errors += validate(spec, schema, example["value"], f"{path}.examples.{name}")
    return errors


def check(spec: dict[str, Any]) -> list[str]:
    """Alle avvik fra OpenAPI 3.1-strukturen og mellom eksempler og skjema. Tom liste = gyldig."""
    errors: list[str] = []
    if not str(spec.get("openapi", "")).startswith("3.1."):
        errors.append("openapi må være 3.1.x")
    info = spec.get("info", {})
    for name in ("title", "version"):
        if not isinstance(info.get(name), str):
            errors.append(f"info.{name} mangler")
    for path, ref in _refs(spec, "#"):
        try:
            resolve(spec, ref)
        except (KeyError, TypeError):
            errors.append(f"{path}: $ref {ref!r} finnes ikke")
    if errors:
        return errors
    for name, schema in spec.get("components", {}).get("schemas", {}).items():
        errors += _check_schema(spec, schema, f"components.schemas.{name}")
    operation_ids: set[str] = set()
    paths = spec.get("paths", {})
    if not paths:
        errors.append("paths er tom")
    for route, item in paths.items():
        if not route.startswith("/"):
            errors.append(f"{route}: stien må starte med /")
        for method, op in item.items():
            where = f"{method.upper()} {route}"
            if method not in HTTP_METHODS:
                if method not in ("summary", "description", "parameters", "servers"):
                    errors.append(f"{where}: ukjent felt")
                continue
            op_id = op.get("operationId")
            if not op_id or op_id in operation_ids:
                errors.append(f"{where}: operationId mangler eller er brukt før")
            operation_ids.add(op_id)
            for param in op.get("parameters", []):
                param = resolve(spec, param["$ref"]) if "$ref" in param else param
                if param.get("in") not in PARAM_LOCATIONS or "name" not in param:
                    errors.append(f"{where}: parameter mangler name/in")
                if "schema" in param:
                    errors += _check_schema(spec, param["schema"], f"{where} {param.get('name')}")
            body = op.get("requestBody")
            if body is not None:
                body = resolve(spec, body["$ref"]) if "$ref" in body else body
                for mime, media in body.get("content", {}).items():
                    errors += _check_media(spec, media, f"{where} request {mime}")
            responses = op.get("responses")
            if not responses:
                errors.append(f"{where}: mangler responses")
                continue
            for status, response in responses.items():
                if status != "default" and not re.fullmatch(r"[1-5](?:\d\d|XX)", status):
                    errors.append(f"{where}: ugyldig statuskode {status!r}")
                response = resolve(spec, response["$ref"]) if "$ref" in response else response
                if "description" not in response:
                    errors.append(f"{where} {status}: mangler description")
                for mime, media in response.get("content", {}).items():
                    errors += _check_media(spec, media, f"{where} {status} {mime}")
    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else SPEC
    try:
        errors = check(load_spec(path))
    except YamlSubsetError as exc:
        errors = [str(exc)]
    for error in errors:
        print(error)
    print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: "
          f"{'gyldig' if not errors else f'{len(errors)} feil'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
