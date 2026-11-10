"""python -m etsy_intelligence {validate,evaluate,quick-check,compare,update}."""
import argparse
import json
from pathlib import Path
from .engine import validate, evaluate, quick_check, compare, update_record


def main():
    parser = argparse.ArgumentParser(description='Offline Phase 1 research prototype')
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('validate', 'evaluate', 'quick-check'):
        cmd = sub.add_parser(command)
        cmd.add_argument('record', type=Path)
        if command != 'validate':
            cmd.add_argument('--output', type=Path, required=True)
    cmd = sub.add_parser('compare')
    cmd.add_argument('records', nargs='+', type=Path)
    cmd.add_argument('--output', type=Path, required=True)
    cmd = sub.add_parser('update')
    cmd.add_argument('record', type=Path)
    cmd.add_argument('evidence', type=Path, help='JSON array of new evidence records')
    cmd.add_argument('--as-of', required=True)
    cmd.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'compare':
            result = compare([json.loads(p.read_text()) for p in args.records])
        else:
            record = json.loads(args.record.read_text())
            if args.command == 'validate':
                validate(record)
                print('Valid research record (structure and references; not factual verification).')
                return
            if args.command == 'evaluate':
                result = json.dumps(evaluate(record), ensure_ascii=False, indent=2) + '\n'
            elif args.command == 'update':
                result = json.dumps(update_record(record, json.loads(args.evidence.read_text()), args.as_of), ensure_ascii=False, indent=2) + '\n'
            else:
                result = quick_check(record)
        # Exclusive creation keeps previous research versions and reports intact.
        with args.output.open('x') as output:
            output.write(result)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
