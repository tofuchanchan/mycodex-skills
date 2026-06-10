#!/usr/bin/env python3
"""Audit Polish JPK_V7M and VAT-UE XML files.

The script performs deterministic extraction, classification, reconciliation,
and report generation. It intentionally treats configured own EU VAT IDs as the
primary evidence for transfer classifications. Company names are supporting
signals only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable


EU_COUNTRIES = {
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "EL",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
    "PL",
}

EXPECTED_NAMESPACES = {
    "JPK_V7M": "http://crd.gov.pl/wzor/2025/12/19/14090/",
    "VAT_UE": "http://crd.gov.pl/wzor/2021/01/12/10293/",
}


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def namespace_uri(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag[1:].split("}", 1)[0]
    return ""


def clean_text(value: str | None) -> str:
    return (value or "").strip()


def decimal_or_zero(value: Any) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value).replace(",", ".").strip())
    except (InvalidOperation, AttributeError):
        return Decimal("0")


def money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def whole_pln(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def normalize_country(value: str | None) -> str:
    country = clean_text(value).upper()
    return "EL" if country == "GR" else country


def normalize_vat_id(value: str | None, country: str | None = None) -> str:
    raw = clean_text(value).upper()
    normalized = re.sub(r"[^A-Z0-9]", "", raw)
    cc = normalize_country(country)
    if cc and normalized.startswith(cc) and len(normalized) > 2:
        normalized = normalized[2:]
    return normalized


def normalize_name(value: str | None) -> str:
    raw = clean_text(value).upper()
    return re.sub(r"[^A-Z0-9]+", "", raw)


def confidence_label(value: str) -> str:
    return {
        "confirmed": "已确认",
        "assumed": "按规则默认",
        "needs_review": "需人工确认",
    }.get(value, value)


def child_dict(elem: ET.Element) -> dict[str, str]:
    return {local_name(child.tag): clean_text(child.text) for child in list(elem)}


def iter_local(root: ET.Element, name: str) -> Iterable[ET.Element]:
    for elem in root.iter():
        if local_name(elem.tag) == name:
            yield elem


def first_text(root: ET.Element, name: str) -> str:
    for elem in iter_local(root, name):
        return clean_text(elem.text)
    return ""


def attrs_and_text(root: ET.Element, names: set[str]) -> list[str]:
    values: list[str] = []
    for elem in root.iter():
        if local_name(elem.tag) in names:
            values.append(clean_text(elem.text))
            values.extend(clean_text(v) for v in elem.attrib.values())
    return [v for v in values if v]


@dataclass
class Config:
    taxpayer_nip: str = ""
    period: str = ""
    own_vat_ids: dict[str, set[str]] | None = None
    own_company_aliases: list[str] | None = None
    own_vat_gate_status: str = "unknown"
    vat_rate: Decimal = Decimal("0.23")
    rounding_tolerance_pln: Decimal = Decimal("1")

    @property
    def has_non_pl_own_vat_ids(self) -> bool:
        if not self.own_vat_ids:
            return False
        return any(country != "PL" and ids for country, ids in self.own_vat_ids.items())


def load_config(path: Path | None, vat_rate: str, tolerance: str) -> Config:
    cfg = Config(
        own_vat_ids={},
        own_company_aliases=[],
        vat_rate=decimal_or_zero(vat_rate) or Decimal("0.23"),
        rounding_tolerance_pln=decimal_or_zero(tolerance) or Decimal("1"),
    )
    if not path:
        return cfg

    data = json.loads(path.read_text(encoding="utf-8-sig"))
    cfg.taxpayer_nip = clean_text(data.get("taxpayer_nip"))
    cfg.period = clean_text(data.get("period"))
    cfg.vat_rate = decimal_or_zero(data.get("vat_rate", str(cfg.vat_rate))) or cfg.vat_rate
    cfg.rounding_tolerance_pln = decimal_or_zero(
        data.get("rounding_tolerance_pln", str(cfg.rounding_tolerance_pln))
    ) or cfg.rounding_tolerance_pln

    aliases = data.get("own_company_aliases", [])
    if isinstance(aliases, str):
        aliases = [aliases]
    cfg.own_company_aliases = [clean_text(x) for x in aliases if clean_text(x)]

    own_vats: dict[str, set[str]] = defaultdict(set)
    raw_vats = data.get("own_vat_ids", {})
    if isinstance(raw_vats, dict):
        for country, ids in raw_vats.items():
            if isinstance(ids, str):
                ids = [ids]
            for vat_id in ids or []:
                cc = normalize_country(country)
                own_vats[cc].add(normalize_vat_id(vat_id, cc))
    elif isinstance(raw_vats, list):
        for item in raw_vats:
            if not isinstance(item, dict):
                continue
            cc = normalize_country(item.get("country"))
            vat_id = normalize_vat_id(item.get("vat_id") or item.get("vat"), cc)
            if cc and vat_id:
                own_vats[cc].add(vat_id)
            name = clean_text(item.get("name") or item.get("alias"))
            if name:
                cfg.own_company_aliases.append(name)

    cfg.own_vat_ids = dict(own_vats)
    return cfg


def find_xml_files(input_path: Path, explicit_files: list[Path]) -> list[Path]:
    if explicit_files:
        return explicit_files
    if input_path.is_file():
        return [input_path]
    return sorted(input_path.glob("*.xml"))


def parse_xml_file(path: Path) -> tuple[ET.Element | None, str | None]:
    try:
        return ET.parse(path).getroot(), None
    except Exception as exc:  # noqa: BLE001 - report parser errors as findings
        return None, str(exc)


def identify_file(root: ET.Element) -> str:
    root_name = local_name(root.tag)
    form_values = " ".join(attrs_and_text(root, {"KodFormularza", "KodFormularzaDekl"}))
    if root_name == "JPK" or "JPK_V7M" in form_values or "JPK_VAT" in form_values:
        return "JPK_V7M"
    if root_name == "Deklaracja" and ("VAT-UE" in form_values or "VAT-UE" in first_text(root, "KodFormularza")):
        return "VAT_UE"
    return "UNKNOWN"


def get_subject(root: ET.Element) -> dict[str, str]:
    return {
        "nip": first_text(root, "NIP") or first_text(root, "etd:NIP"),
        "name": first_text(root, "PelnaNazwa") or first_text(root, "etd:PelnaNazwa"),
    }


def get_period(root: ET.Element) -> str:
    year = first_text(root, "Rok")
    month = first_text(root, "Miesiac")
    if month:
        month = month.zfill(2)
    return f"{year}-{month}" if year and month else ""


def extract_jpk(root: ET.Element) -> dict[str, Any]:
    sales = [child_dict(e) for e in iter_local(root, "SprzedazWiersz")]
    purchases = [child_dict(e) for e in iter_local(root, "ZakupWiersz")]
    declaration: dict[str, str] = {}
    for decl in iter_local(root, "Deklaracja"):
        for positions in list(decl):
            if local_name(positions.tag) != "PozycjeSzczegolowe":
                continue
            for child in list(positions):
                key = local_name(child.tag)
                if key.startswith("P_"):
                    declaration[key] = clean_text(child.text)
            break
        break

    sales_ctrl = {}
    for elem in iter_local(root, "SprzedazCtrl"):
        sales_ctrl = child_dict(elem)
        break
    purchase_ctrl = {}
    for elem in iter_local(root, "ZakupCtrl"):
        purchase_ctrl = child_dict(elem)
        break

    return {
        "sales": sales,
        "purchases": purchases,
        "declaration": declaration,
        "sales_ctrl": sales_ctrl,
        "purchase_ctrl": purchase_ctrl,
    }


def extract_vat_ue(root: ET.Element) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {"Grupa1": [], "Grupa2": [], "Grupa3": [], "Grupa4": []}
    schema_issues: list[str] = []

    for group_name in groups:
        for elem in iter_local(root, group_name):
            raw = child_dict(elem)
            normalized: dict[str, Any] = {"raw": raw, "group": group_name, "field_issue": False}
            if group_name == "Grupa1":
                normalized.update(
                    {
                        "country": normalize_country(raw.get("P_Da")),
                        "vat_id": normalize_vat_id(raw.get("P_Db"), raw.get("P_Da")),
                        "amount": decimal_or_zero(raw.get("P_Dc")),
                        "triangle": raw.get("P_Dd", ""),
                    }
                )
            elif group_name == "Grupa2":
                if {"P_Na", "P_Nb", "P_Nc"}.issubset(raw):
                    normalized.update(
                        {
                            "country": normalize_country(raw.get("P_Na")),
                            "vat_id": normalize_vat_id(raw.get("P_Nb"), raw.get("P_Na")),
                            "amount": decimal_or_zero(raw.get("P_Nc")),
                            "triangle": raw.get("P_Nd", ""),
                        }
                    )
                elif {"P_Da", "P_Db", "P_Dc"}.issubset(raw):
                    normalized["field_issue"] = True
                    schema_issues.append("Grupa2 uses P_Da/P_Db/P_Dc/P_Dd; official VAT-UE fields are P_Na/P_Nb/P_Nc/P_Nd.")
                    normalized.update(
                        {
                            "country": normalize_country(raw.get("P_Da")),
                            "vat_id": normalize_vat_id(raw.get("P_Db"), raw.get("P_Da")),
                            "amount": decimal_or_zero(raw.get("P_Dc")),
                            "triangle": raw.get("P_Dd", ""),
                        }
                    )
                else:
                    normalized["field_issue"] = True
                    schema_issues.append("Grupa2 is missing official acquisition fields P_Na/P_Nb/P_Nc.")
            elif group_name == "Grupa3":
                normalized.update(
                    {
                        "country": normalize_country(raw.get("P_Ua")),
                        "vat_id": normalize_vat_id(raw.get("P_Ub"), raw.get("P_Ua")),
                        "amount": decimal_or_zero(raw.get("P_Uc")),
                        "triangle": "",
                    }
                )
            else:
                normalized.update(
                    {
                        "country": normalize_country(raw.get("P_Ca")),
                        "vat_id": normalize_vat_id(raw.get("P_Cb"), raw.get("P_Ca")),
                        "amount": Decimal("0"),
                        "triangle": raw.get("P_Cd", ""),
                    }
                )
            groups[group_name].append(normalized)

    return {"groups": groups, "schema_issues": sorted(set(schema_issues))}


def is_eu_non_pl(country: str) -> bool:
    cc = normalize_country(country)
    return cc in EU_COUNTRIES and cc != "PL"


def is_own_vat(country: str, vat_id: str, cfg: Config) -> bool:
    if not cfg.own_vat_ids:
        return False
    cc = normalize_country(country)
    normalized = normalize_vat_id(vat_id, cc)
    return normalized in cfg.own_vat_ids.get(cc, set())


def name_matches_alias(name: str, aliases: list[str]) -> bool:
    normalized = normalize_name(name)
    if not normalized:
        return False
    for alias in aliases:
        norm_alias = normalize_name(alias)
        if len(norm_alias) < 5:
            continue
        if norm_alias in normalized or normalized in norm_alias:
            return True
    return False


def transfer_signal(row: dict[str, str], aliases: list[str]) -> bool:
    name = row.get("NazwaKontrahenta") or row.get("NazwaDostawcy") or ""
    doc = row.get("DowodSprzedazy") or row.get("DowodZakupu") or ""
    return name_matches_alias(name, aliases) or clean_text(doc).upper() in {"BRAK", "WEW"}


def row_common(row: dict[str, str], source: str, tx_type: str, base: Decimal, vat: Decimal, confidence: str, notes: str) -> dict[str, Any]:
    country = normalize_country(row.get("KodKrajuNadaniaTIN"))
    vat_id = row.get("NrKontrahenta") or row.get("NrDostawcy") or ""
    name = row.get("NazwaKontrahenta") or row.get("NazwaDostawcy") or ""
    doc = row.get("DowodSprzedazy") or row.get("DowodZakupu") or ""
    date = row.get("DataSprzedazy") or row.get("DataZakupu") or row.get("DataWystawienia") or ""
    lp = row.get("LpSprzedazy") or row.get("LpZakupu") or ""
    return {
        "type": tx_type,
        "source": source,
        "lp": lp,
        "country": country,
        "vat_id": normalize_vat_id(vat_id, country),
        "vat_id_raw": vat_id,
        "name": name,
        "document": doc,
        "date": date,
        "base_amount": money(base),
        "vat_amount": money(vat),
        "confidence": confidence_label(confidence),
        "notes": notes,
    }


def classify_transactions(jpk: dict[str, Any], cfg: Config, taxpayer_name: str) -> dict[str, list[dict[str, Any]]]:
    aliases = list(cfg.own_company_aliases or [])
    if taxpayer_name:
        aliases.append(taxpayer_name)

    out: dict[str, list[dict[str, Any]]] = {
        "cross_border_b2b_sales": [],
        "cross_border_b2b_purchases": [],
        "transfer_exports": [],
        "transfer_imports": [],
        "possible_transfer_exports": [],
        "possible_transfer_imports": [],
    }

    for row in jpk.get("sales", []):
        country = normalize_country(row.get("KodKrajuNadaniaTIN"))
        vat_id = row.get("NrKontrahenta", "")
        if not is_eu_non_pl(country):
            continue
        if "K_21" in row:
            base = decimal_or_zero(row.get("K_21"))
            if is_own_vat(country, vat_id, cfg):
                out["transfer_exports"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B移仓出口", base, Decimal("0"), "confirmed", "VAT ID matches configured own EU VAT ID.")
                )
            elif transfer_signal(row, aliases):
                out["possible_transfer_exports"].append(
                    row_common(row, "JPK.SprzedazWiersz", "疑似跨境B2B移仓出口", base, Decimal("0"), "needs_review", "Name/document suggests possible transfer, but own VAT ID was not configured or did not match.")
                )
                out["cross_border_b2b_sales"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B销售", base, Decimal("0"), "assumed", "Defaulted to B2B sale because transfer requires configured own VAT ID.")
                )
            else:
                out["cross_border_b2b_sales"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B销售", base, Decimal("0"), "confirmed", "Non-PL EU K_21 row and not configured as own VAT ID.")
                )
        if "K_23" in row or "K_24" in row:
            base = decimal_or_zero(row.get("K_23"))
            vat = decimal_or_zero(row.get("K_24"))
            if is_own_vat(country, vat_id, cfg):
                out["transfer_imports"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B移仓进口", base, vat, "confirmed", "VAT ID matches configured own EU VAT ID.")
                )
            elif transfer_signal(row, aliases):
                out["possible_transfer_imports"].append(
                    row_common(row, "JPK.SprzedazWiersz", "疑似跨境B2B移仓进口", base, vat, "needs_review", "Name/document suggests possible transfer, but own VAT ID was not configured or did not match.")
                )
                out["cross_border_b2b_purchases"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B采购", base, vat, "assumed", "Defaulted to B2B purchase because transfer requires configured own VAT ID.")
                )
            else:
                out["cross_border_b2b_purchases"].append(
                    row_common(row, "JPK.SprzedazWiersz", "跨境B2B采购", base, vat, "confirmed", "Non-PL EU K_23/K_24 row and not configured as own VAT ID.")
                )

    return out


def aggregate_jpk(jpk: dict[str, Any], field: str, id_field: str = "NrKontrahenta") -> dict[tuple[str, str], Decimal]:
    result: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    source = jpk.get("sales", []) if id_field == "NrKontrahenta" else jpk.get("purchases", [])
    for row in source:
        if field not in row:
            continue
        country = normalize_country(row.get("KodKrajuNadaniaTIN"))
        vat_id = normalize_vat_id(row.get(id_field), country)
        if not country or not vat_id:
            continue
        result[(country, vat_id)] += decimal_or_zero(row.get(field))
    return dict(result)


def aggregate_ue(groups: list[dict[str, Any]]) -> dict[tuple[str, str], Decimal]:
    result: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    for row in groups:
        country = normalize_country(row.get("country"))
        vat_id = normalize_vat_id(row.get("vat_id"), country)
        if not country or not vat_id:
            continue
        result[(country, vat_id)] += decimal_or_zero(row.get("amount"))
    return dict(result)


def add_finding(findings: list[dict[str, Any]], severity: str, code: str, title: str, detail: str, recommendation: str = "") -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "title": title,
            "detail": detail,
            "recommendation": recommendation,
        }
    )


def compare_maps(
    left: dict[tuple[str, str], Decimal],
    right: dict[tuple[str, str], Decimal],
    left_name: str,
    right_name: str,
    tolerance: Decimal,
    findings: list[dict[str, Any]],
    issues: list[dict[str, str]],
) -> None:
    all_keys = sorted(set(left) | set(right))
    for key in all_keys:
        left_amount = left.get(key)
        right_amount = right.get(key)
        key_text = f"{key[0]} {key[1]}"
        if left_amount is None:
            if right_amount is not None and abs(right_amount) <= tolerance:
                continue
            detail = f"{right_name} 存在 {key_text}，金额 {money(right_amount or Decimal('0'))}，但 {left_name} 未找到对应记录。"
            add_finding(findings, "P1", "MISSING_IN_JPK", f"{right_name} transaction missing in {left_name}", detail, "Check whether the JPK transaction is missing or the VAT ID differs.")
            issues.append({"severity": "P1", "type": "missing_in_jpk", "key": key_text, "detail": detail})
        elif right_amount is None:
            if abs(left_amount) <= tolerance:
                continue
            detail = f"{left_name} 存在 {key_text}，金额 {money(left_amount)}，但 {right_name} 未找到对应记录。"
            add_finding(findings, "P1", "MISSING_IN_VAT_UE", f"{left_name} transaction missing in {right_name}", detail, "Add the counterpart to VAT-UE or correct country/VAT ID.")
            issues.append({"severity": "P1", "type": "missing_in_vat_ue", "key": key_text, "detail": detail})
        else:
            diff = abs(left_amount - right_amount)
            if diff > tolerance:
                detail = f"{key_text}：{left_name} 金额 {money(left_amount)}，{right_name} 金额 {money(right_amount)}，差异 {money(diff)}。"
                add_finding(findings, "P1", "AMOUNT_MISMATCH", f"{left_name} and {right_name} amount mismatch", detail, "Check rounding, currency conversion, and aggregation basis.")
                issues.append({"severity": "P1", "type": "amount_mismatch", "key": key_text, "detail": detail})


def purchase_map(jpk: dict[str, Any], base_fields: tuple[str, ...], vat_fields: tuple[str, ...]) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    result: dict[tuple[str, str], list[Decimal]] = defaultdict(lambda: [Decimal("0"), Decimal("0")])
    for row in jpk.get("purchases", []):
        country = normalize_country(row.get("KodKrajuNadaniaTIN"))
        vat_id = normalize_vat_id(row.get("NrDostawcy"), country)
        if not country or not vat_id:
            continue
        base = sum(decimal_or_zero(row.get(field)) for field in base_fields)
        vat = sum(decimal_or_zero(row.get(field)) for field in vat_fields)
        if base or vat:
            result[(country, vat_id)][0] += base
            result[(country, vat_id)][1] += vat
    return {key: (value[0], value[1]) for key, value in result.items()}


def sales_wnt_map(jpk: dict[str, Any]) -> dict[tuple[str, str], tuple[Decimal, Decimal]]:
    result: dict[tuple[str, str], list[Decimal]] = defaultdict(lambda: [Decimal("0"), Decimal("0")])
    for row in jpk.get("sales", []):
        if "K_23" not in row and "K_24" not in row:
            continue
        country = normalize_country(row.get("KodKrajuNadaniaTIN"))
        vat_id = normalize_vat_id(row.get("NrKontrahenta"), country)
        if not country or not vat_id:
            continue
        result[(country, vat_id)][0] += decimal_or_zero(row.get("K_23"))
        result[(country, vat_id)][1] += decimal_or_zero(row.get("K_24"))
    return {key: (value[0], value[1]) for key, value in result.items()}


def reconcile_internal_jpk(jpk: dict[str, Any], cfg: Config, findings: list[dict[str, Any]], issues: list[dict[str, str]]) -> None:
    sales_wnt = sales_wnt_map(jpk)
    purchases = purchase_map(jpk, ("K_42", "K_40"), ("K_43", "K_41"))
    all_keys = sorted(set(sales_wnt) | set(purchases))
    vat_tolerance = Decimal("0.05")
    for key in all_keys:
        s_base, s_vat = sales_wnt.get(key, (Decimal("0"), Decimal("0")))
        p_base, p_vat = purchases.get(key, (Decimal("0"), Decimal("0")))
        key_text = f"{key[0]} {key[1]}"
        if key not in purchases:
            detail = f"WNT 销项侧存在 {key_text}，K_23/K_24 为 {money(s_base)}/{money(s_vat)}，但采购抵扣侧未找到对应记录。"
            add_finding(findings, "P1", "WNT_INPUT_MISSING", "WNT output side lacks purchase deduction", detail, "Check whether K_42/K_43 or K_40/K_41 should be created.")
            issues.append({"severity": "P1", "type": "wnt_input_missing", "key": key_text, "detail": detail})
        elif key not in sales_wnt:
            detail = f"采购抵扣侧存在 {key_text}，基础金额/VAT 为 {money(p_base)}/{money(p_vat)}，但 WNT 销项侧未找到对应 K_23/K_24 记录。"
            add_finding(findings, "P1", "WNT_OUTPUT_MISSING", "Purchase deduction lacks WNT output side", detail, "Check whether K_23/K_24 should be created.")
            issues.append({"severity": "P1", "type": "wnt_output_missing", "key": key_text, "detail": detail})
        elif abs(s_base - p_base) > cfg.rounding_tolerance_pln or abs(s_vat - p_vat) > vat_tolerance:
            detail = f"{key_text}：销项侧 K_23/K_24 为 {money(s_base)}/{money(s_vat)}，进项侧 K_40/42 与 K_41/43 为 {money(p_base)}/{money(p_vat)}，两边不一致。"
            add_finding(findings, "P1", "WNT_OUTPUT_INPUT_MISMATCH", "WNT output/input amounts mismatch", detail, "Align the WNT self-assessment and deduction rows.")
            issues.append({"severity": "P1", "type": "wnt_output_input_mismatch", "key": key_text, "detail": detail})

        if s_base:
            expected_vat = (s_base * cfg.vat_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if abs(expected_vat - s_vat) > vat_tolerance:
                detail = f"{key_text}：K_24 为 {money(s_vat)}，但按 K_23 {money(s_base)} × 税率 {cfg.vat_rate} 计算应为 {money(expected_vat)}。"
                add_finding(findings, "P1", "VAT_CALC_MISMATCH", "WNT VAT calculation mismatch", detail, "Check VAT rate and rounding.")
                issues.append({"severity": "P1", "type": "vat_calc_mismatch", "key": key_text, "detail": detail})


def check_declaration_totals(jpk: dict[str, Any], cfg: Config, findings: list[dict[str, Any]], issues: list[dict[str, str]]) -> None:
    declaration = jpk.get("declaration", {})
    totals = {
        "P_21": sum(decimal_or_zero(r.get("K_21")) for r in jpk.get("sales", [])),
        "P_23": sum(decimal_or_zero(r.get("K_23")) for r in jpk.get("sales", [])),
        "P_24": sum(decimal_or_zero(r.get("K_24")) for r in jpk.get("sales", [])),
        "P_42": sum(decimal_or_zero(r.get("K_42")) for r in jpk.get("purchases", [])),
        "P_43": sum(decimal_or_zero(r.get("K_43")) for r in jpk.get("purchases", [])),
    }
    for field, row_total in totals.items():
        if field not in declaration:
            continue
        declared = decimal_or_zero(declaration.get(field))
        if abs(declared - row_total) > cfg.rounding_tolerance_pln:
            detail = f"{field}：申报汇总金额 {money(declared)}，明细行合计 {money(row_total)}，两者不一致。"
            add_finding(findings, "P1", "DECLARATION_TOTAL_MISMATCH", f"{field} declaration total mismatch", detail, "Regenerate declaration summary from detail rows.")
            issues.append({"severity": "P1", "type": "declaration_total_mismatch", "key": field, "detail": detail})


def validate_files(
    files: dict[str, dict[str, Any]],
    jpk_file: dict[str, Any] | None,
    ue_file: dict[str, Any] | None,
    cfg: Config,
    findings: list[dict[str, Any]],
) -> None:
    if not jpk_file:
        add_finding(findings, "P0", "JPK_MISSING", "JPK_V7M file not found", "No XML file was identified as JPK_V7M.", "Provide the main JPK_V7M XML file.")
    if not ue_file:
        add_finding(findings, "P0", "VAT_UE_MISSING", "VAT-UE file not found", "No XML file was identified as VAT-UE.", "Provide the VAT-UE XML file.")

    if jpk_file and ue_file:
        if jpk_file.get("period") and ue_file.get("period") and jpk_file["period"] != ue_file["period"]:
            add_finding(findings, "P1", "PERIOD_MISMATCH", "JPK and VAT-UE periods mismatch", f"JPK period {jpk_file['period']} vs VAT-UE period {ue_file['period']}.", "Use files for the same reporting period.")
        if jpk_file.get("nip") and ue_file.get("nip") and jpk_file["nip"] != ue_file["nip"]:
            add_finding(findings, "P1", "NIP_MISMATCH", "JPK and VAT-UE taxpayer NIP mismatch", f"JPK NIP {jpk_file['nip']} vs VAT-UE NIP {ue_file['nip']}.", "Use files for the same taxpayer.")

    for path_text, meta in files.items():
        if meta.get("parse_error"):
            add_finding(findings, "P0", "XML_PARSE_ERROR", "XML cannot be parsed", f"{path_text}: {meta['parse_error']}", "Fix malformed XML.")
            continue
        name = Path(path_text).name
        nip = meta.get("nip") or cfg.taxpayer_nip
        period = (meta.get("period") or cfg.period).replace("-", "")
        if meta.get("type") == "JPK_V7M" and nip and period:
            if not re.search(rf"PL?{re.escape(nip)}.*{period[:4]}[-_]?{period[4:]}", name, re.I):
                add_finding(findings, "P3", "FILENAME_PATTERN", "JPK filename does not follow recommended taxpayer-period naming", f"Filename `{name}` does not clearly contain NIP {nip} and period {period[:4]}-{period[4:]}.", "Use a consistent filename such as PL{NIP}_YYYY-MM.xml.")
        if meta.get("type") == "VAT_UE" and nip and period:
            if "(UE)" not in name.upper() and "VAT-UE" not in name.upper():
                add_finding(findings, "P3", "VAT_UE_FILENAME_PATTERN", "VAT-UE filename does not clearly mark UE", f"Filename `{name}` does not contain `(UE)` or `VAT-UE`.", "Mark VAT-UE files clearly to avoid uploading the wrong XML.")
        file_type = meta.get("type")
        expected_namespace = EXPECTED_NAMESPACES.get(file_type)
        actual_namespace = meta.get("namespace")
        if expected_namespace and actual_namespace and actual_namespace != expected_namespace:
            add_finding(
                findings,
                "P2",
                "SCHEMA_VERSION_REVIEW",
                "XML namespace differs from the skill's current field reference",
                f"{name}: namespace `{actual_namespace}` differs from supported reference `{expected_namespace}`.",
                "Verify field meanings against the official schema for this XML namespace before finalizing the audit.",
            )


def build_audit(files: list[Path], cfg: Config) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    file_meta: dict[str, dict[str, Any]] = {}
    jpk_file: dict[str, Any] | None = None
    ue_file: dict[str, Any] | None = None
    jpk_data: dict[str, Any] | None = None
    ue_data: dict[str, Any] | None = None

    for path in files:
        root, parse_error = parse_xml_file(path)
        meta: dict[str, Any] = {"path": str(path), "parse_error": parse_error}
        if root is not None:
            file_type = identify_file(root)
            subject = get_subject(root)
            meta.update(
                {
                    "type": file_type,
                    "root": local_name(root.tag),
                    "namespace": namespace_uri(root.tag),
                    "period": get_period(root),
                    "nip": subject.get("nip", ""),
                    "taxpayer_name": subject.get("name", ""),
                }
            )
            if file_type == "JPK_V7M":
                jpk_file = meta
                jpk_data = extract_jpk(root)
            elif file_type == "VAT_UE":
                ue_file = meta
                ue_data = extract_vat_ue(root)
        file_meta[str(path)] = meta

    taxpayer_name = (jpk_file or {}).get("taxpayer_name", "")
    validate_files(file_meta, jpk_file, ue_file, cfg, findings)

    if not cfg.has_non_pl_own_vat_ids:
        add_finding(
            findings,
            "P2",
            "OWN_VAT_CONFIG_EMPTY",
            "No non-PL own EU VAT IDs configured",
            "The user confirmed no non-PL own EU VAT registrations or no such VAT IDs were configured. Transfer classifications are not confirmed without configured own VAT IDs.",
            "If any possible-transfer findings below are real transfers, collect country + VAT ID and rerun with a config file. Company aliases are optional and only help manual review.",
        )

    if ue_data:
        for schema_issue in ue_data.get("schema_issues", []):
            add_finding(findings, "P0", "VAT_UE_SCHEMA_FIELDS", "VAT-UE group uses non-official fields", schema_issue, "Use official VAT-UE Grupa2 fields P_Na/P_Nb/P_Nc/P_Nd.")

    transactions = {
        "cross_border_b2b_sales": [],
        "cross_border_b2b_purchases": [],
        "transfer_exports": [],
        "transfer_imports": [],
        "possible_transfer_exports": [],
        "possible_transfer_imports": [],
    }

    if jpk_data:
        transactions = classify_transactions(jpk_data, cfg, taxpayer_name)

        for tx in transactions["possible_transfer_exports"]:
            add_finding(
                findings,
                "P2",
                "POSSIBLE_TRANSFER_EXPORT",
                "Possible transfer export not confirmed",
                f"{tx['country']} {tx['vat_id_raw']} amount {tx['base_amount']} document {tx['document']} looks like a transfer signal, but own VAT ID was not configured.",
                "Confirm whether this VAT ID belongs to the taxpayer and add it to own_vat_ids if yes.",
            )
        for tx in transactions["possible_transfer_imports"]:
            add_finding(
                findings,
                "P2",
                "POSSIBLE_TRANSFER_IMPORT",
                "Possible transfer import not confirmed",
                f"{tx['country']} {tx['vat_id_raw']} amount {tx['base_amount']} document {tx['document']} looks like a transfer signal, but own VAT ID was not configured.",
                "Confirm whether this VAT ID belongs to the taxpayer and add it to own_vat_ids if yes.",
            )

    reconciliation: dict[str, Any] = {}
    if jpk_data and ue_data:
        k21 = aggregate_jpk(jpk_data, "K_21")
        k23 = aggregate_jpk(jpk_data, "K_23")
        ue_g1 = aggregate_ue(ue_data["groups"]["Grupa1"])
        ue_g2 = aggregate_ue(ue_data["groups"]["Grupa2"])
        reconciliation = {
            "jpk_k21": {f"{k[0]} {k[1]}": money(v) for k, v in k21.items()},
            "jpk_k23": {f"{k[0]} {k[1]}": money(v) for k, v in k23.items()},
            "vat_ue_grupa1": {f"{k[0]} {k[1]}": money(v) for k, v in ue_g1.items()},
            "vat_ue_grupa2": {f"{k[0]} {k[1]}": money(v) for k, v in ue_g2.items()},
        }
        compare_maps(k21, ue_g1, "JPK K_21", "VAT-UE Grupa1", cfg.rounding_tolerance_pln, findings, issues)
        compare_maps(k23, ue_g2, "JPK K_23", "VAT-UE Grupa2", cfg.rounding_tolerance_pln, findings, issues)
        reconcile_internal_jpk(jpk_data, cfg, findings, issues)
        check_declaration_totals(jpk_data, cfg, findings, issues)

    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    findings.sort(key=lambda f: (severity_order.get(f["severity"], 9), f["code"], f["title"]))

    audit = {
        "config": {
            "taxpayer_nip": cfg.taxpayer_nip,
            "period": cfg.period,
            "own_vat_gate_status": cfg.own_vat_gate_status,
            "has_non_pl_own_vat_ids": cfg.has_non_pl_own_vat_ids,
            "own_vat_ids": {k: sorted(v) for k, v in (cfg.own_vat_ids or {}).items()},
            "own_company_aliases": cfg.own_company_aliases or [],
            "vat_rate": str(cfg.vat_rate),
            "rounding_tolerance_pln": str(cfg.rounding_tolerance_pln),
        },
        "files": file_meta,
        "jpk_summary": {
            "sales_rows": len(jpk_data.get("sales", [])) if jpk_data else 0,
            "purchase_rows": len(jpk_data.get("purchases", [])) if jpk_data else 0,
            "declaration": jpk_data.get("declaration", {}) if jpk_data else {},
        },
        "vat_ue_summary": {
            "grupa1_rows": len(ue_data["groups"]["Grupa1"]) if ue_data else 0,
            "grupa2_rows": len(ue_data["groups"]["Grupa2"]) if ue_data else 0,
            "grupa3_rows": len(ue_data["groups"]["Grupa3"]) if ue_data else 0,
            "grupa4_rows": len(ue_data["groups"]["Grupa4"]) if ue_data else 0,
        },
        "transactions": transactions,
        "reconciliation": reconciliation,
        "issues": issues,
        "findings": findings,
    }
    audit["taxpayer"] = taxpayer_summary(audit)
    return audit


def flatten_transactions(audit: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for items in audit.get("transactions", {}).values():
        rows.extend(items)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def severity_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for finding in findings:
        sev = finding.get("severity")
        if sev in counts:
            counts[sev] += 1
    return counts


def taxpayer_summary(audit: dict[str, Any]) -> dict[str, str]:
    files = list(audit.get("files", {}).values())
    jpk_file = next((meta for meta in files if meta.get("type") == "JPK_V7M"), {})
    any_file = jpk_file or (files[0] if files else {})
    cfg = audit.get("config", {})
    nip = clean_text(any_file.get("nip") or cfg.get("taxpayer_nip"))
    period = clean_text(any_file.get("period") or cfg.get("period")) or "UNKNOWN_PERIOD"
    tax_number = f"PL{nip}" if nip and not nip.upper().startswith("PL") else (nip or "UNKNOWN_TAXNO")
    return {
        "nip": nip or "UNKNOWN_TAXNO",
        "polish_tax_number": tax_number,
        "period": period,
        "taxpayer_name": clean_text(any_file.get("taxpayer_name")) or "UNKNOWN_TAXPAYER",
    }


def safe_path_part(value: str) -> str:
    value = clean_text(value) or "UNKNOWN"
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "UNKNOWN"


def create_archive_dir(output_root: Path, audit: dict[str, Any]) -> Path:
    summary = taxpayer_summary(audit)
    today = date.today().strftime("%Y%m%d")
    prefix = "_".join(
        [
            safe_path_part(summary["polish_tax_number"]),
            safe_path_part(summary["period"]),
            today,
        ]
    )
    output_root.mkdir(parents=True, exist_ok=True)
    existing_ids: list[int] = []
    for child in output_root.iterdir():
        if not child.is_dir() or not child.name.startswith(prefix + "_"):
            continue
        suffix = child.name.rsplit("_", 1)[-1]
        if suffix.isdigit():
            existing_ids.append(int(suffix))
    next_id = (max(existing_ids) + 1) if existing_ids else 1
    archive_dir = output_root / f"{prefix}_{next_id:03d}"
    archive_dir.mkdir(parents=False, exist_ok=False)
    return archive_dir


def markdown_table(rows: list[dict[str, Any]], columns: list[tuple[str, str]], max_rows: int = 20) -> str:
    if not rows:
        return "_无_"
    header = "| " + " | ".join(title for title, _ in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows[:max_rows]:
        body.append("| " + " | ".join(str(row.get(key, "")).replace("|", "/") for _, key in columns) + " |")
    if len(rows) > max_rows:
        cells = ["...", f"仅展示前 {max_rows} 条，共 {len(rows)} 条"] + [""] * (len(columns) - 2)
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *body])


def write_report(path: Path, audit: dict[str, Any]) -> None:
    counts = severity_counts(audit.get("findings", []))
    files = list(audit.get("files", {}).values())
    taxpayer = taxpayer_summary(audit)
    lines: list[str] = []
    lines.append("# 波兰 VAT XML 审计报告")
    lines.append("")
    lines.append("## 1. 结论摘要")
    lines.append("")
    passed = counts["P0"] == 0 and counts["P1"] == 0
    lines.append(f"- 波兰税号：{taxpayer['polish_tax_number']}")
    lines.append(f"- 申报周期：{taxpayer['period']}")
    lines.append(f"- 纳税主体：{taxpayer['taxpayer_name']}")
    lines.append(f"- 审计结论：{'通过基础检查' if passed else '存在需要处理的问题'}")
    lines.append(f"- 高危/阻断问题：P0={counts['P0']}，P1={counts['P1']}")
    lines.append(f"- 需人工确认/低风险：P2={counts['P2']}，P3={counts['P3']}")
    lines.append(f"- JPK 行数：销售 {audit['jpk_summary']['sales_rows']}，采购 {audit['jpk_summary']['purchase_rows']}")
    lines.append(f"- VAT-UE 行数：Grupa1 {audit['vat_ue_summary']['grupa1_rows']}，Grupa2 {audit['vat_ue_summary']['grupa2_rows']}，Grupa3 {audit['vat_ue_summary']['grupa3_rows']}，Grupa4 {audit['vat_ue_summary']['grupa4_rows']}")
    lines.append("")
    lines.append("## 2. 文件识别")
    lines.append("")
    lines.append(markdown_table(files, [("文件", "path"), ("类型", "type"), ("期间", "period"), ("NIP", "nip"), ("主体", "taxpayer_name"), ("Namespace", "namespace")], 10))
    lines.append("")
    lines.append("## 3. 自有 VAT 识别前提")
    lines.append("")
    cfg = audit.get("config", {})
    if cfg.get("has_non_pl_own_vat_ids"):
        lines.append("- 用户已提供非 PL 自有欧盟 VAT 号，本次按 VAT 号匹配确认移仓。")
    else:
        lines.append("- 用户已明确确认无非 PL 自有欧盟 VAT 号，本次按“没有其他欧盟 VAT 税号”处理。")
        lines.append("- 公司名相似、单据号为 BRAK/WEW 只作为疑似移仓风险，不作为确认移仓依据。")
    lines.append("")
    lines.append("## 4. 交易提取")
    lines.append("")
    tx = audit.get("transactions", {})
    tx_columns = [
        ("类型", "type"),
        ("来源", "source"),
        ("Lp", "lp"),
        ("国家", "country"),
        ("VAT号", "vat_id_raw"),
        ("名称", "name"),
        ("单据", "document"),
        ("日期", "date"),
        ("基础金额", "base_amount"),
        ("VAT", "vat_amount"),
        ("置信度", "confidence"),
    ]
    sections = [
        ("跨境 B2B 销售", "cross_border_b2b_sales"),
        ("跨境 B2B 采购", "cross_border_b2b_purchases"),
        ("跨境 B2B 移仓出口", "transfer_exports"),
        ("跨境 B2B 移仓进口", "transfer_imports"),
        ("疑似移仓出口", "possible_transfer_exports"),
        ("疑似移仓进口", "possible_transfer_imports"),
    ]
    for title, key in sections:
        lines.append(f"### {title}")
        lines.append("")
        lines.append(markdown_table(tx.get(key, []), tx_columns, 15))
        lines.append("")
    lines.append("## 5. 对账问题")
    lines.append("")
    issue_columns = [("级别", "severity"), ("类型", "type"), ("键", "key"), ("详情", "detail")]
    lines.append(markdown_table(audit.get("issues", []), issue_columns, 50))
    lines.append("")
    lines.append("## 6. 风险点")
    lines.append("")
    finding_columns = [("级别", "severity"), ("代码", "code"), ("问题", "title"), ("详情", "detail"), ("建议", "recommendation")]
    lines.append(markdown_table(audit.get("findings", []), finding_columns, 80))
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8-sig")


def write_outputs(audit: dict[str, Any], output_root: Path) -> Path:
    output_dir = create_archive_dir(output_root, audit)
    audit["output_archive_dir"] = str(output_dir)
    (output_dir / "audit_findings.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(
        output_dir / "extracted_transactions.csv",
        flatten_transactions(audit),
        [
            "type",
            "source",
            "lp",
            "country",
            "vat_id_raw",
            "vat_id",
            "name",
            "document",
            "date",
            "base_amount",
            "vat_amount",
            "confidence",
            "notes",
        ],
    )
    write_csv(
        output_dir / "reconciliation_issues.csv",
        audit.get("issues", []),
        ["severity", "type", "key", "detail"],
    )
    write_report(output_dir / "vat_xml_audit_report.md", audit)
    return output_dir


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Polish JPK_V7M and VAT-UE XML files.")
    parser.add_argument("--input", default=".", help="Folder or XML file path.")
    parser.add_argument("--xml", nargs="*", default=[], help="Explicit XML files. Overrides folder scan when provided.")
    parser.add_argument("--config", help="Optional JSON config with own VAT IDs and company aliases.")
    parser.add_argument(
        "--own-vat-status",
        choices=["provided", "none"],
        help="Required per-run user answer. Use 'provided' only after the user confirms non-PL own EU VAT registrations and provides them in config. Use 'none' only after the user confirms there are no non-PL own EU VAT registrations.",
    )
    parser.add_argument(
        "--assume-no-own-eu-vat",
        action="store_true",
        help="Shortcut for --own-vat-status none. Use only after the current user request explicitly confirms no non-PL own EU VAT registrations.",
    )
    parser.add_argument("--output-dir", default="audit-output", help="Directory for report, CSV, and JSON outputs.")
    parser.add_argument("--vat-rate", default="0.23", help="Default VAT rate for WNT checks.")
    parser.add_argument("--rounding-tolerance-pln", default="1", help="Tolerance for VAT-UE/JPK amount reconciliation.")
    return parser.parse_args(argv)


def resolve_own_vat_gate(args: argparse.Namespace, cfg: Config) -> tuple[bool, str]:
    status = args.own_vat_status
    if args.assume_no_own_eu_vat:
        status = "none"

    if not status:
        return False, (
            "Own EU VAT gate is unresolved for this run. Ask the user in the current request: "
            "'Does the taxpayer have any non-PL EU VAT registrations?' "
            "Do not rely on prior context or config files. If yes, rerun with --own-vat-status provided and a config containing own_vat_ids. "
            "If no, rerun with --own-vat-status none."
        )

    if status == "provided":
        if cfg.has_non_pl_own_vat_ids:
            cfg.own_vat_gate_status = "provided"
            return True, ""
        return False, "Own VAT gate says 'provided', but the config contains no non-PL own VAT IDs. Provide own_vat_ids or use --own-vat-status none only after user confirmation."
    if status == "none":
        if cfg.has_non_pl_own_vat_ids:
            return False, "Own VAT gate says 'none', but the config contains non-PL own VAT IDs. Remove the config or rerun with --own-vat-status provided after user confirmation."
        cfg.own_vat_gate_status = "none"
        return True, ""

    return False, "Unsupported own VAT gate status."


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    input_path = Path(args.input).resolve()
    explicit_files = [Path(x).resolve() for x in args.xml]
    files = find_xml_files(input_path, explicit_files)
    cfg = load_config(Path(args.config).resolve() if args.config else None, args.vat_rate, args.rounding_tolerance_pln)
    gate_ok, gate_error = resolve_own_vat_gate(args, cfg)
    if not gate_ok:
        print(f"ERROR: {gate_error}", file=sys.stderr)
        return 2
    audit = build_audit(files, cfg)
    output_root = Path(args.output_dir).resolve()
    output_dir = write_outputs(audit, output_root)
    counts = severity_counts(audit.get("findings", []))
    print(f"Audit complete: {output_dir}")
    print(f"Findings: P0={counts['P0']} P1={counts['P1']} P2={counts['P2']} P3={counts['P3']}")
    return 1 if counts["P0"] or counts["P1"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
