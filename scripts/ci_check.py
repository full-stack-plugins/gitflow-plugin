#!/usr/bin/env python3
"""GitHub Action 入口：只解析事件和 Git 对象，不执行被检项目内容。"""
import argparse
import html
import json
import os
from pathlib import Path
from gitflow.ci import check
from gitflow.git import FlowError, reason, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True)
    parser.add_argument('--event', required=True)
    parser.add_argument('--message-mode', choices=['commits', 'squash'], default='commits')
    parser.add_argument('--output', required=True)
    parser.add_argument('--summary', required=True)
    args = parser.parse_args()
    try:
        event = Path(args.event)
        if event.is_symlink() or event.stat().st_size > 2 * 1024 * 1024:
            raise FlowError('ci_event_invalid', '事件文件超限或是链接。')
        data = json.loads(event.read_text())
        pr = data.get('pull_request')
        if not isinstance(pr, dict):
            raise FlowError('ci_event_invalid', '此 Action 需要 pull_request 事件及明确 base/head。')
        title, body = pr.get('title', ''), pr.get('body') or ''
        if not isinstance(title, str) or not isinstance(body, str):
            raise FlowError('ci_event_invalid', 'PR 标题或正文类型无效。')
        message = title + ('\n\n' + body if body else '')
        result = check(args.repo, pr['base']['sha'], pr['head']['sha'], pr['head']['ref'], pr['base']['ref'], args.message_mode, message if args.message_mode == 'squash' else None)
    except FlowError as exc:
        result = report('check', exc.decision, [reason(exc.code, exc.message)])
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
        result = report('check', 'unverified', [reason('ci_input_invalid', '事件、元数据或报告输入无法验证。')])
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    # JSON 置于 HTML pre 中并完整转义，不让提交消息改变报告结构。
    with Path(args.summary).open('a') as stream:
        stream.write('\n## GitFlow: ' + result['decision'] + '\n\n<details><summary>检查明细</summary><pre>' + html.escape(json.dumps(result, ensure_ascii=False, indent=2)) + '</pre></details>\n')
    if os.environ.get('GITHUB_OUTPUT'):
        with Path(os.environ['GITHUB_OUTPUT']).open('a') as stream:
            stream.write('decision=' + result['decision'] + '\n')
    print(json.dumps({'decision': result['decision'], 'report': args.output}, ensure_ascii=False))
    return {'allow': 0, 'deny': 1, 'unverified': 3}.get(result['decision'], 4)


if __name__ == '__main__':
    raise SystemExit(main())
