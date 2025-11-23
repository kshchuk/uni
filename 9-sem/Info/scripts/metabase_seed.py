"""
Bootstrap Metabase with TechMarket DWH connection, KPI questions, and dashboard.

Prerequisites:
- Running Metabase instance (default http://localhost:3000)
- Metabase admin credentials
- PostgreSQL DWH reachable from Metabase (defaults match docker-compose dwh-db)

Usage:
    export METABASE_URL=http://localhost:3000
    export METABASE_USER=admin@example.com
    export METABASE_PASS=secret
    # Optional overrides for DWH connection (defaults are docker-compose values)
    export DWH_HOST=dwh-db
    export DWH_PORT=5432
    export DWH_NAME=dwh_db
    export DWH_USER=dwh_user
    export DWH_PASS=dwh_pass
    python scripts/metabase_seed.py

The script will:
1) Log in to Metabase and obtain a session
2) Create (or reuse) a PostgreSQL database connection
3) Create Saved Questions for key KPIs
4) Create a dashboard and wire filters (start/end date, region)
"""

from __future__ import annotations

import argparse
import os
import sys
import uuid
import requests
from pathlib import Path


def getenv(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise SystemExit(f"Environment variable {key} is required")
    return value


def load_env_file(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k not in os.environ:
            os.environ[k] = v


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap Metabase with TechMarket DWH, KPI questions, and dashboard."
    )
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Delete existing 'TechMarket KPI Dashboard' before creating a new one.",
    )
    return parser.parse_args()


class MetabaseClient:
    def __init__(self, base_url: str, user: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        resp = self.session.post(
            f"{self.base_url}/api/session",
            json={"username": user, "password": password},
            timeout=30,
        )
        if resp.status_code != 200:
            raise SystemExit(f"Failed to login to Metabase: {resp.text}")
        token = resp.json().get("id")
        self.session.headers.update({"X-Metabase-Session": token})

    def _get(self, path: str):
        resp = self.session.get(f"{self.base_url}{path}", timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: dict):
        resp = self.session.post(f"{self.base_url}{path}", json=payload, timeout=30)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise SystemExit(f"POST {path} failed: {resp.status_code} {resp.text}") from e
        return resp.json()

    def _put(self, path: str, payload: dict):
        resp = self.session.put(f"{self.base_url}{path}", json=payload, timeout=30)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise SystemExit(f"PUT {path} failed: {resp.status_code} {resp.text}") from e
        return resp.json()

    def find_database(self, name: str) -> int | None:
        payload = self._get("/api/database")
        # Metabase may return list or dict with "data"
        if isinstance(payload, dict) and "data" in payload:
            items = payload["data"]
        elif isinstance(payload, list):
            items = payload
        else:
            raise SystemExit(f"Unexpected response from /api/database: {payload}")

        for db in items:
            if isinstance(db, dict) and db.get("name") == name:
                return db.get("id")
        return None

    def list_dashboards(self) -> list[dict]:
        payload = self._get("/api/dashboard")
        return payload if isinstance(payload, list) else payload.get("data", [])

    def delete_dashboard(self, dashboard_id: int) -> None:
        self.session.delete(f"{self.base_url}/api/dashboard/{dashboard_id}", timeout=30).raise_for_status()

    def list_cards(self) -> list[dict]:
        payload = self._get("/api/card")
        return payload if isinstance(payload, list) else payload.get("data", [])

    def delete_card(self, card_id: int) -> None:
        self.session.delete(f"{self.base_url}/api/card/{card_id}", timeout=30).raise_for_status()

    def create_database(
        self,
        name: str,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
    ) -> int:
        payload = {
            "name": name,
            "engine": "postgres",
            "details": {
                "host": host,
                "port": port,
                "dbname": dbname,
                "user": user,
                "password": password,
                "ssl": False,
            },
            "is_on_demand": False,
        }
        db = self._post("/api/database", payload)
        return db.get("id")

    def create_card(self, name: str, dataset_query: dict, display: str = "table") -> int:
        payload = {
            "name": name,
            "dataset_query": dataset_query,
            "display": display,
            "visualization_settings": {},
        }
        card = self._post("/api/card", payload)
        return card.get("id")

    def create_dashboard(self, name: str, description: str = "") -> int:
        dashboard = self._post(
            "/api/dashboard",
            {"name": name, "description": description},
        )
        return dashboard.get("id")

    def update_dashboard_parameters(self, dashboard_id: int, parameters: list[dict]):
        self._put(f"/api/dashboard/{dashboard_id}", {"parameters": parameters})

    def add_card_to_dashboard(
        self,
        dashboard_id: int,
        cards_payload: list[dict],
    ):
        """Deprecated endpoint for adding cards no longer exists; use PUT /api/dashboard/:id/cards."""
        payload = {"cards": cards_payload, "tabs": []}
        self._put(f"/api/dashboard/{dashboard_id}/cards", payload)


def template_tags():
    return {
        "start_date": {
            "name": "start_date",
            "display-name": "Start Date",
            "type": "date",
        },
        "end_date": {
            "name": "end_date",
            "display-name": "End Date",
            "type": "date",
        },
        "region": {
            "name": "region",
            "display-name": "Region",
            "type": "text",
        },
    }


def build_questions(db_id: int):
    tags = template_tags()
    return [
        {
            "name": "Revenue by Month",
            "display": "line",
            "query": """
SELECT
  d.year,
  d.month,
  to_char(d.date, 'Mon') AS month_name,
  SUM(f.revenue)          AS revenue,
  SUM(f.discount_amount)  AS discount,
  SUM(f.margin)           AS margin
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
LEFT JOIN dim_region r ON f.region_key = r.region_key
WHERE 1=1
[[AND d.date >= {{start_date}}]]
[[AND d.date <= {{end_date}}]]
[[AND r.name = {{region}}]]
GROUP BY d.year, d.month, to_char(d.date, 'Mon')
ORDER BY d.year, d.month;
            """.strip(),
            "tags": tags,
        },
        {
            "name": "Orders by Region",
            "display": "bar",
            "query": """
SELECT
  r.name AS region_name,
  COUNT(DISTINCT f.order_id) AS orders_count,
  SUM(f.revenue)             AS revenue
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
WHERE 1=1
[[AND f.date_key >= (SELECT MIN(date_key) FROM dim_date WHERE date >= {{start_date}})]]
[[AND f.date_key <= (SELECT MAX(date_key) FROM dim_date WHERE date <= {{end_date}})]]
[[AND r.name = {{region}}]]
GROUP BY r.name
ORDER BY orders_count DESC;
            """.strip(),
            "tags": tags,
        },
        {
            "name": "Average Order Value",
            "display": "scalar",
            "query": """
SELECT
  SUM(f.revenue) / NULLIF(COUNT(DISTINCT f.order_id), 0) AS avg_order_value
FROM fact_sales f
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE 1=1
[[AND d.date >= {{start_date}}]]
[[AND d.date <= {{end_date}}]]
[[AND r.name = {{region}}]];
            """.strip(),
            "tags": tags,
        },
        {
            "name": "Margin Percentage",
            "display": "scalar",
            "query": """
SELECT
  (SUM(f.margin) / NULLIF(SUM(f.revenue), 0))::numeric(12,4) AS margin_pct
FROM fact_sales f
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE 1=1
[[AND d.date >= {{start_date}}]]
[[AND d.date <= {{end_date}}]]
[[AND r.name = {{region}}]];
            """.strip(),
            "tags": tags,
        },
        {
            "name": "Top Products by Revenue",
            "display": "bar",
            "query": """
SELECT
  p.name AS product_name,
  SUM(f.revenue) AS revenue,
  SUM(f.quantity) AS qty,
  SUM(f.margin) AS margin
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
LEFT JOIN dim_region r ON f.region_key = r.region_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE 1=1
[[AND d.date >= {{start_date}}]]
[[AND d.date <= {{end_date}}]]
[[AND r.name = {{region}}]]
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;
            """.strip(),
            "tags": tags,
        },
    ]


def make_dataset_query(db_id: int, sql: str, tags: dict) -> dict:
    return {
        "type": "native",
        "native": {"query": sql, "template-tags": tags},
        "database": db_id,
        "parameters": [],
    }


def main() -> int:
    # Try to load .env if present
    load_env_file()
    args = parse_args()

    base_url = getenv("METABASE_URL", "http://localhost:3000")
    user = getenv("METABASE_USER")
    password = getenv("METABASE_PASS")
    purge = args.clear or os.getenv("METABASE_PURGE_DASHBOARDS", "false").lower() == "true"

    dwh_host = getenv("DWH_HOST", "dwh-db")
    dwh_port = int(getenv("DWH_PORT", "5432"))
    dwh_name = getenv("DWH_NAME", "dwh_db")
    dwh_user = getenv("DWH_USER", "dwh_user")
    dwh_pass = getenv("DWH_PASS", "dwh_pass")

    client = MetabaseClient(base_url, user, password)

    db_name = "TechMarket DWH"
    db_id = client.find_database(db_name)
    if db_id:
        print(f"Found existing Metabase database '{db_name}' (id={db_id})")
    else:
        print(f"Creating Metabase database '{db_name}'...")
        db_id = client.create_database(
            db_name, dwh_host, dwh_port, dwh_name, dwh_user, dwh_pass
        )
        print(f"Created database id={db_id}")

    dashboard_name = "TechMarket KPI Dashboard"
    if purge:
        dashboards = client.list_dashboards()
        to_delete = [d for d in dashboards if d.get("name") == dashboard_name]
        for d in to_delete:
            did = d.get("id")
            print(f"Deleting old dashboard '{dashboard_name}' (id={did})")
            client.delete_dashboard(did)

        # Видалимо і старі картки з тими самими іменами, щоб не накопичувались дублі
        existing_cards = client.list_cards()
        target_names = {q["name"] for q in build_questions(db_id)}
        to_delete_cards = [c for c in existing_cards if c.get("name") in target_names]
        for c in to_delete_cards:
            cid = c.get("id")
            cname = c.get("name")
            print(f"Deleting old card '{cname}' (id={cid})")
            client.delete_card(cid)

    # Create questions
    question_ids: dict[str, int] = {}
    for q in build_questions(db_id):
        dataset_query = make_dataset_query(db_id, q["query"], q["tags"])
        card_id = client.create_card(q["name"], dataset_query, display=q["display"])
        question_ids[q["name"]] = card_id
        print(f"Created card '{q['name']}' (id={card_id})")

    # Create dashboard
    dashboard_id = client.create_dashboard(
        dashboard_name,
        "Key metrics: revenue trend, orders by region, AOV, margin %, top products.",
    )
    print(f"Created dashboard id={dashboard_id}")

    # Dashboard parameters
    params = [
        {"name": "Start Date", "slug": "start_date", "id": str(uuid.uuid4()), "type": "date/single"},
        {"name": "End Date", "slug": "end_date", "id": str(uuid.uuid4()), "type": "date/single"},
        {"name": "Region", "slug": "region", "id": str(uuid.uuid4()), "type": "string/="},
    ]
    client.update_dashboard_parameters(dashboard_id, params)

    # Helper to map dashboard params to template tags
    def mappings_for(card_id: int, tags: dict) -> list[dict]:
        param_lookup = {p["slug"]: p["id"] for p in params}
        mappings = []
        if "start_date" in tags:
            mappings.append(
                {
                    "parameter_id": param_lookup["start_date"],
                    "card_id": card_id,
                    "target": ["variable", ["template-tag", "start_date"]],
                }
            )
        if "end_date" in tags:
            mappings.append(
                {
                    "parameter_id": param_lookup["end_date"],
                    "card_id": card_id,
                    "target": ["variable", ["template-tag", "end_date"]],
                }
            )
        if "region" in tags:
            mappings.append(
                {
                    "parameter_id": param_lookup["region"],
                    "card_id": card_id,
                    "target": ["variable", ["template-tag", "region"]],
                }
            )
        return mappings

    # Layout (col, row, sizeX, sizeY)
    layout = {
        "Revenue by Month": (0, 0, 12, 6),
        "Orders by Region": (0, 6, 6, 6),
        "Average Order Value": (6, 6, 3, 3),
        "Margin Percentage": (9, 6, 3, 3),
        "Top Products by Revenue": (0, 12, 12, 6),
    }

    cards_payload = []
    next_id = -1
    for q in build_questions(db_id):
        card_id = question_ids[q["name"]]
        col, row, sx, sy = layout[q["name"]]
        cards_payload.append(
            {
                "id": next_id,
                "card_id": card_id,
                "dashboard_id": dashboard_id,
                "row": row,
                "col": col,
                "size_x": sx,
                "size_y": sy,
                "parameter_mappings": mappings_for(card_id, q["tags"]),
                "visualization_settings": {},
                "series": [],
            }
        )
        next_id -= 1
    client.add_card_to_dashboard(dashboard_id, cards_payload)
    print(f"Added {len(cards_payload)} cards to dashboard")

    print("Metabase bootstrap completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
