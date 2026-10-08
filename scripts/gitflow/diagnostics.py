"""只读解释有效规则与实际可观察的接线状态。"""
import re
from .git import FlowError, VERSION, discover, reason, report, require_repo, text
from .layout import state_dir, wrapper
from .policy import load
from .rules import CATALOG
from .storage import read_json, safe_dir


def describe(path):
    facts = require_repo(path)
    policy, active = load(facts)
    candidate = safe_dir(facts['root'], '.gitflow/workflow.json')
    definition = read_json(candidate) if active['mode'] == 'shared' and candidate.exists() else None
    entries = {}
    for ident, item in CATALOG.items():
        config = policy.get('rules', {}).get(ident, {'severity': 'off'})
        source = 'default'
        if ident in policy.get('rules', {}):
            source = 'snapshot' if definition is None else ('project' if ident in definition.get('rules', {}) else 'organization')
        entries[ident] = {'name': item['name'], 'scope': item['scope'], 'severity': config['severity'],
                          'options': {**item['defaults'], **config.get('options', {})}, 'source': source}
    return report('policy.describe', revision=policy['revision'], policy_sha256=active['sha256'],
                  mode=active['mode'], organization=policy.get('extends'), rules=entries,
                  workflow_guards='branch role, creation base, merge direction and repository identity remain enforced')


def doctor(path):
    facts = discover(path)
    if facts['git_state'] == 'absent':
        return report('doctor', git_state='absent', automatic_activation=False,
                      next_actions=[{'action': 'init', 'message': '仅显式接入才初始化 Git。'}])
    problems = []
    try:
        policy = describe(path)
    except FlowError as exc:
        policy = {'status': 'unverified', 'code': exc.code}
        problems.append(reason(exc.code, exc.message))
    override = text(facts['root'], 'config', '--get', 'core.hooksPath', check=False)
    runtime = state_dir(facts) / 'native-runtime'
    hook_dir = safe_dir(facts['common_dir'], 'hooks')
    observed = {}
    for kind in ('commit-msg', 'pre-push'):
        file = hook_dir / kind
        if override:
            observed[kind] = 'external_manager'
        elif not file.exists():
            observed[kind] = 'missing'
        elif file.is_symlink() or file.stat().st_size > 8192 or file.read_text() != wrapper(runtime, kind):
            observed[kind] = 'unverified'
        else:
            observed[kind] = 'configured'
    runtime_version = None
    version_file = runtime / 'scripts/gitflow/git.py'
    if version_file.is_file() and not version_file.is_symlink() and version_file.stat().st_size < 256 * 1024:
        match = re.search(r"^VERSION = ['\"]([^'\"]+)['\"]", version_file.read_text(), re.M)
        runtime_version = match[1] if match else None
    status = 'configured' if all(v == 'configured' for v in observed.values()) else ('missing' if all(v == 'missing' for v in observed.values()) else 'unverified')
    if status == 'configured' and runtime_version != VERSION:
        status = 'outdated'
    workflows = safe_dir(facts['root'], '.github/workflows')
    candidates = []
    if workflows.is_dir():
        for file in sorted(workflows.iterdir()):
            if file.suffix in ('.yml', '.yaml') and not file.is_symlink() and file.is_file() and file.stat().st_size < 65536 and 'full-stack-plugins/gitflow-plugin' in file.read_text():
                candidates.append(file.name)
    integrations = {'native_hooks': {'status': status, 'entries': observed, 'runtime_version': runtime_version},
                    'ci': {'status': 'configured_unverified' if candidates else 'missing', 'files': candidates},
                    'host_mcp': {'status': 'unverified'}, 'server_protection': {'status': 'unverified'}}
    return report('doctor', 'unverified' if problems else 'allow', problems, policy=policy, integrations=integrations,
                  next_actions=[{'action': 'integration.review', 'message': 'missing 时使用 hooks 预览并显式安装；已有管理器或旧运行时须审查接线。CI 使用发布 Action，required check 由管理员配置；宿主须实际调用验证。'}])
