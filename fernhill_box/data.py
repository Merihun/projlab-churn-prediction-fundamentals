"""Fernhill Box's export, from fixed seeds: every copy of the project gets the same bytes.

Fernhill Box is a monthly box of outdoor kit, launched on 1 July 2025. The export holds everything that
happened before 1 October 2026, in five CSV files under data/raw/:

    customers.csv         one row per customer from the CRM (with the CRM's faults, below)
    subscriptions.csv     one row per subscription: plan, box size, price, start, and its state on export day
    boxes.csv             one row per monthly box: shipped or skipped, what it cost, the customer's rating
    app_sessions.csv      one row per session in the Fernhill app (launched 1 April 2026)
    support_tickets.csv   one row per support ticket

Customers behave the way real ones do: each has a hidden satisfaction that drifts from month to month.
Unhappy customers open the app less, skip boxes, give low ratings and cancel more often; monthly plans
cancel more than annual ones, and the first two months are the riskiest. Nothing about a customer decides
for sure whether they cancel, so no model can be perfect.

The faults are planted on purpose (PROJECT.md describes them):

- customers.csv: about 6% of regions written in other ways (" north west", "NORTH WEST", "North West "),
  45 customers exported twice (the second row differs only in how the region is written), ages missing,
  and ages no person has (negative, 0, 130, 999); about 3% of acquisition channels blank.
- subscriptions.csv: plans written in other ways ("monthly ", "MONTHLY"), prices that are negative, 0.00 or
  blank, and three columns written on export day, not before: status, cancelled_on, cancellation_reason.
- support_tickets.csv: most customers who cancel open a "Cancellation" ticket on the day they do.

Standard library only.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = "fernhill-box-v1"
LAUNCH = date(2025, 7, 1)
EXPORT_DATE = date(2026, 10, 1)  # the export holds everything before this day
APP_LAUNCH = date(2026, 4, 1)

FILES = ("customers", "subscriptions", "boxes", "app_sessions", "support_tickets")

REGIONS = ("London", "South East", "South West", "Midlands", "North West", "North East", "Scotland", "Wales",
           "Northern Ireland")
REGION_WEIGHTS = (18, 16, 10, 15, 12, 7, 10, 7, 5)
CHANNELS = {"Organic": 0.0, "Paid social": -0.35, "Referral": 0.35, "Partner": -0.1}
CHANNEL_WEIGHTS = (40, 30, 18, 12)
PLANS = {"Monthly": 0.35, "Quarterly": -0.25, "Annual": -1.0}  # effect on the chance to cancel
PLAN_WEIGHTS = (60, 25, 15)
PLAN_DISCOUNT = {"Monthly": 1.0, "Quarterly": 0.9, "Annual": 0.8}
BOX_SIZES = {"Small": 19.99, "Standard": 29.99, "Large": 44.99}
BOX_WEIGHTS = (30, 50, 20)
REASONS = ("Too expensive", "Not using the kit", "Delivery problems", "Moving abroad", "Other")

DUPLICATED_CUSTOMERS = 45
BAD_AGES = (-1, -7, -34, 0, 0, 3, 130, 199, 999, 999)


def _rng(seed: str, *parts: object) -> random.Random:
    return random.Random(":".join([seed, *map(str, parts)]))


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def _poisson(r: random.Random, lam: float) -> int:
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= r.random()
        if p <= limit:
            return k
        k += 1


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    return date(d.year + month // 12, month % 12 + 1, min(d.day, 28))


def _days_in_month(d: date) -> int:
    return (_add_months(d.replace(day=1), 1) - d.replace(day=1)).days


@dataclass
class Customer:
    customer_id: str
    started_on: date
    age: int
    region: str
    channel: str
    plan: str
    box_size: str
    price: float
    cancelled_on: date | None = None
    reason: str = ""
    boxes: list[tuple[date, str, float, int | None]] = field(default_factory=list)
    sessions: list[tuple[datetime, float]] = field(default_factory=list)
    tickets: list[tuple[date, str]] = field(default_factory=list)


def signups(month_index: int) -> int:
    """How many customers start in the month_index-th month after launch: more every month."""
    return 420 + 30 * month_index


def simulate(seed: str = SEED) -> list[Customer]:
    """Every customer's life until export day, in the order they signed up."""
    customers = []
    month = LAUNCH
    index = 0
    while month < EXPORT_DATE:
        r = _rng(seed, "signups", month)
        days = sorted(r.randrange(_days_in_month(month)) for _ in range(signups(index)))
        for day in days:
            number = len(customers) + 1
            customers.append(_one_customer(seed, f"C{number:05d}", month + timedelta(days=day)))
        month = _add_months(month, 1)
        index += 1
    return customers


def _one_customer(seed: str, customer_id: str, started_on: date) -> Customer:
    r = _rng(seed, "customer", customer_id)
    channel = r.choices(list(CHANNELS), CHANNEL_WEIGHTS)[0]
    plan = r.choices(list(PLANS), PLAN_WEIGHTS)[0]
    box_size = r.choices(list(BOX_SIZES), BOX_WEIGHTS)[0]
    age = max(18, min(84, round(r.gauss(41, 12))))
    c = Customer(
        customer_id=customer_id, started_on=started_on, age=age,
        region=r.choices(REGIONS, REGION_WEIGHTS)[0], channel=channel, plan=plan, box_size=box_size,
        price=round(BOX_SIZES[box_size] * PLAN_DISCOUNT[plan], 2),
    )
    base = r.gauss(0, 1) + CHANNELS[channel] + 0.01 * (age - 41)
    mood = base + r.gauss(0, 0.5)
    cycle = 0
    while True:
        start = _add_months(started_on, cycle) if cycle else started_on
        end = _add_months(started_on, cycle + 1)
        if start >= EXPORT_DATE:
            break
        mood = 0.75 * mood + 0.25 * base + r.gauss(0, 0.45)
        if r.random() < 0.05:  # a delivery goes wrong: the customer is less happy, and tells support
            mood -= 1.3
            c.tickets.append((start + timedelta(days=r.randint(2, 9)), "Delivery"))
        if r.random() < _sigmoid(-2.4 - 1.2 * mood):
            c.boxes.append((start, "skipped", 0.0, None))
        else:
            extra = round(r.uniform(5, 25), 2) if r.random() < 0.18 * (1 + max(mood, -1)) else 0.0
            rating = max(1, min(5, round(3.5 + 0.9 * mood + r.gauss(0, 0.7)))) if r.random() < 0.5 else None
            c.boxes.append((start, "shipped", round(c.price + extra, 2), rating))
        length = (end - start).days
        for _ in range(_poisson(r, min(30.0, 3.2 * math.exp(0.5 * mood)))):
            moment = datetime(start.year, start.month, start.day) + timedelta(seconds=r.randrange(length * 86400))
            if moment.date() >= APP_LAUNCH:
                c.sessions.append((moment, round(math.exp(r.gauss(1.9 + 0.15 * mood, 0.6)), 1)))
        if r.random() < 0.03:
            c.tickets.append((start + timedelta(days=r.randrange(length)), "Billing"))
        if r.random() < 0.04 + (0.06 if mood < -1 else 0.0):
            c.tickets.append((start + timedelta(days=r.randrange(length)), "Product"))
        risk = -1.7 - 1.45 * mood + PLANS[plan] + (0.45 if cycle < 2 else 0.0) + 0.02 * (c.price - 30)
        if r.random() < _sigmoid(risk):
            cancelled_on = start + timedelta(days=r.randint(1, length - 1))
            if cancelled_on < EXPORT_DATE:
                c.cancelled_on = cancelled_on
                if c.price > 35 and r.random() < 0.5:
                    c.reason = "Too expensive"
                elif any(kind == "Delivery" for _, kind in c.tickets[-2:]) and r.random() < 0.6:
                    c.reason = "Delivery problems"
                else:
                    c.reason = r.choices(REASONS, (25, 35, 10, 8, 22))[0]
                if r.random() < 0.7:
                    c.tickets.append((cancelled_on, "Cancellation"))
                c.sessions = [s for s in c.sessions if s[0].date() < cancelled_on]
                c.tickets = [t for t in c.tickets if t[0] <= cancelled_on]
                break
        cycle += 1
    c.sessions = [s for s in c.sessions if s[0].date() < EXPORT_DATE]
    c.tickets = [t for t in c.tickets if t[0] < EXPORT_DATE]
    return c


def _messy(r: random.Random, text: str) -> str:
    """The same text, written the way a person or an old system sometimes writes it."""
    return r.choice((text.lower(), text.upper(), f"{text} ", f" {text.lower()}", f"{text}  "))


def tables(seed: str = SEED) -> dict[str, tuple[list[str], list[list[str]]]]:
    """Each file's header and rows, exactly as written."""
    people = simulate(seed)
    r = _rng(seed, "faults")
    ids = [c.customer_id for c in people]
    twice = set(r.sample(ids, DUPLICATED_CUSTOMERS))
    bad_age = dict(zip(r.sample(ids, 40), BAD_AGES * 4))
    no_age = set(r.sample(ids, round(len(ids) * 0.06)))
    no_channel = set(r.sample(ids, round(len(ids) * 0.03)))
    messy_region = set(r.sample(ids, round(len(ids) * 0.06)))
    messy_plan = set(r.sample(ids, round(len(ids) * 0.07)))
    bad_price = dict(zip(r.sample(ids, 30), ["-" + "{:.2f}"] * 14 + ["0.00"] * 9 + [""] * 7))

    customers, later = [], []
    for c in people:
        age = "" if c.customer_id in no_age else str(bad_age.get(c.customer_id, c.age))
        region = _messy(r, c.region) if c.customer_id in messy_region else c.region
        channel = "" if c.customer_id in no_channel else c.channel
        row = [c.customer_id, c.started_on.isoformat(), age, region, channel]
        customers.append(row)
        if c.customer_id in twice:
            later.append([c.customer_id, c.started_on.isoformat(), age, _messy(r, c.region), channel])
    for row in later:  # the CRM exported them again, further down the file
        customers.insert(r.randrange(customers.index(next(x for x in customers if x[0] == row[0])) + 1,
                                     len(customers) + 1), row)

    subscriptions = []
    for number, c in enumerate(people, start=1):
        price = bad_price.get(c.customer_id, "{:.2f}")
        price = price.format(c.price)
        plan = _messy(r, c.plan) if c.customer_id in messy_plan else c.plan
        subscriptions.append([
            f"S{number:05d}", c.customer_id, plan, c.box_size, price, c.started_on.isoformat(),
            "cancelled" if c.cancelled_on else "active",
            c.cancelled_on.isoformat() if c.cancelled_on else "", c.reason,
        ])

    boxes = sorted(
        (when, c.customer_id, status, amount, rating) for c in people for when, status, amount, rating in c.boxes
    )
    sessions = sorted((moment, c.customer_id, minutes) for c in people for moment, minutes in c.sessions)
    tickets = sorted((when, c.customer_id, kind) for c in people for when, kind in c.tickets)
    return {
        "customers": (["customer_id", "created_on", "age", "region", "acquisition_channel"], customers),
        "subscriptions": (
            ["subscription_id", "customer_id", "plan", "box_size", "price_gbp", "started_on", "status",
             "cancelled_on", "cancellation_reason"],
            subscriptions,
        ),
        "boxes": (
            ["box_id", "customer_id", "scheduled_on", "status", "amount_gbp", "rating"],
            [[f"B{n:06d}", cid, when.isoformat(), status, f"{amount:.2f}", "" if rating is None else str(rating)]
             for n, (when, cid, status, amount, rating) in enumerate(boxes, start=1)],
        ),
        "app_sessions": (
            ["session_id", "customer_id", "started_at", "minutes"],
            [[f"A{n:07d}", cid, moment.isoformat(), f"{minutes:.1f}"]
             for n, (moment, cid, minutes) in enumerate(sessions, start=1)],
        ),
        "support_tickets": (
            ["ticket_id", "customer_id", "opened_on", "category"],
            [[f"T{n:06d}", cid, when.isoformat(), kind] for n, (when, cid, kind) in enumerate(tickets, start=1)],
        ),
    }


def generate(root: Path, seed: str = SEED) -> dict[str, int]:
    """Write data/raw/*.csv under root (again); returns each file's number of rows."""
    folder = Path(root) / "data" / "raw"
    folder.mkdir(parents=True, exist_ok=True)
    counts = {}
    for name, (header, rows) in tables(seed).items():
        with open(folder / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
        counts[name] = len(rows)
    return counts
