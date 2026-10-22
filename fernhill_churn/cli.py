"""python -m fernhill_churn explore | train    (step 8 adds: score --month YYYY-MM)"""

import argparse
import re
from pathlib import Path


def month(text: str) -> str:
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", text):
        raise argparse.ArgumentTypeError(f"{text!r} is not a month like 2026-10")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m fernhill_churn")
    commands = parser.add_subparsers(dest="command", required=True)

    explore = commands.add_parser("explore", help="step 2: save the three charts in reports/figures/")
    explore.add_argument("--data", type=Path, default=Path("data/raw"))
    explore.add_argument("--out", type=Path, default=Path("reports/figures"))

    train = commands.add_parser("train", help="step 7: fit the chosen model, choose the threshold, write reports/")
    train.add_argument("--data", type=Path, default=Path("data/raw"))
    train.add_argument("--root", type=Path, default=Path("."))

    # Step 8: add the "score" command here: --month (type=month, required), --data, --model and --out.

    args = parser.parse_args(argv)
    if args.command == "explore":
        from fernhill_churn.explore import save_charts
        from fernhill_churn.frame import CUTOFF, load_raw

        for path in save_charts(load_raw(args.data), CUTOFF, args.out):
            print(f"wrote {path}")
    elif args.command == "train":
        from fernhill_churn.frame import CUTOFF
        from fernhill_churn.train import train as run_training

        metrics = run_training(args.data, CUTOFF, args.root)
        print(f"{metrics['model']}: ROC AUC {metrics['roc_auc']:.3f} on {metrics['test_rows']} test customers")
        print(f"threshold {metrics['threshold']:.2f}: {metrics['offers']} offers "
              f"({metrics['offer_share']:.1%} of the test customers), expected profit £{metrics['expected_profit']:,.2f}")
        written = ["reports/metrics.json", "reports/profit_by_threshold.csv", "reports/figures",
                   "reports/permutation_importance.csv", "models/churn_model.joblib"]
        print("wrote " + ", ".join(name for name in written if (args.root / name).exists()))
    return 0
