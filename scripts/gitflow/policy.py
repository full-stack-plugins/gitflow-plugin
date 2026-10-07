"""闭合项目规则与已激活快照；候选定义不得自动覆盖生效规则。"""
import hashlib
import json
from pathlib import Path
import re

from .git import FlowError, report, reason, require_repo, valid_branch
from .storage import atomic_json, locked, read_json, safe_dir

ASSETS = Path(__file__).resolve().parents[2] / 'profiles'
TOP = {'schema_version', 'profile', 'revision', 'roles', 'primary_remote',
       'merge_method', 'commit_message_pattern', 'collaboration'}
ROLE = {'name', 'pattern', 'required', 'allow_commit', 'create_from', 'merge_into'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def validate(value):
    """拒绝未知字段、错误类型、无效角色关系与复杂不受限模式。"""
    if not isinstance(value, dict) or set(value) != TOP or value['schema_version'] != '1.0.0':
        raise FlowError('policy_schema_invalid', '工作流字段或版本不符合 1.0.0 契约。')
    if not isinstance(value['profile'], str) or not re.fullmatch(r'[a-z0-9-]{1,64}', value['profile']):
        raise FlowError('policy_profile_invalid', '工作流标识无效。')
    if type(value['revision']) is not int or value['revision'] < 1:
        raise FlowError('policy_revision_invalid', '规则修订必须为正整数。')
    if value['merge_method'] not in ('merge', 'no-ff', 'squash', 'ff-only'):
        raise FlowError('policy_merge_invalid', '不支持的合并方式。')
    if value['collaboration'] not in ('shared', 'fork'):
        raise FlowError('policy_collaboration_invalid', '协作模式只能是 shared 或 fork。')
    remote = value['primary_remote']
    if not isinstance(remote, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}', remote):
        raise FlowError('policy_remote_invalid', '权威远端必须是单一远端名称。')
    roles = value['roles']
    if not isinstance(roles, dict) or not 1 <= len(roles) <= 32:
        raise FlowError('policy_roles_invalid', '工作流需要 1–32 个分支角色。')
    for key, role in roles.items():
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,31}', key) or not isinstance(role, dict) or set(role) != ROLE:
            raise FlowError('policy_role_invalid', '分支角色字段无效。')
        for flag in ('required', 'allow_commit'):
            if type(role[flag]) is not bool:
                raise FlowError('policy_role_invalid', '角色标志必须是真实布尔值。')
        if (role['name'] is None) == (role['pattern'] is None):
            raise FlowError('policy_role_invalid', '角色需要固定名称或匹配模式之一。')
        if role['required'] and role['name'] is None:
            raise FlowError('policy_role_invalid', '必需角色应有固定名称；临时类型不要求预创建。')
        if role['name'] is not None and (not isinstance(role['name'], str) or len(role['name']) > 240):
            raise FlowError('policy_role_invalid', '固定分支名称无效。')
        check_pattern(role['pattern'])
        for field in ('create_from', 'merge_into'):
            items = role[field]
            if not isinstance(items, list) or any(not isinstance(x, str) or x not in roles for x in items) or len(set(items)) != len(items):
                raise FlowError('policy_relation_invalid', '分支关系必须引用存在且唯一的角色。')
    check_pattern(value['commit_message_pattern'])
    return value


def check_pattern(pattern):
    if pattern is None:
        return
    if not isinstance(pattern, str) or not 1 <= len(pattern) <= 240 or '(?' in pattern or '\\1' in pattern:
        raise FlowError('policy_pattern_invalid', '模式需要受限正则表达式。')
    # 拒绝嵌套量词，避免本地定义耗尽 Hook 预算。
    if re.search(r'\)[+*{?]|\\[1-9]', pattern):
        raise FlowError('policy_pattern_invalid', '不接受嵌套无界量词。')
    # 只接受一个无界单原子重复，避免串行重叠量词组合爆炸。
    atoms = re.sub(r'\[[^\]]*\]', 'X', pattern)
    if '{' in atoms or len(re.findall(r'(?<!\\)[+*]', atoms)) > 1:
        raise FlowError('policy_pattern_invalid', '模式最多含一个单原子无界重复，不支持计数重复。')
    try:
        re.compile(pattern)
    except re.error as exc:
        raise FlowError('policy_pattern_invalid', '正则表达式无效。') from exc


def template(name):
    if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
        raise FlowError('profile_unknown', '工作流模板不存在。')
    path = ASSETS / (name + '.json')
    if not path.is_file():
        raise FlowError('profile_unknown', '工作流模板不存在。')
    return validate(read_json(path))


def role_for(policy, name):
    if not isinstance(name, str) or len(name) > 240:
        return None
    matches = [key for key, role in policy['roles'].items()
               if role['name'] == name or (role['pattern'] is not None and re.fullmatch(role['pattern'], name))]
    if len(matches) > 1:
        raise FlowError('branch_role_ambiguous', '分支命中多个角色，请修订规则。')
    return matches[0] if matches else None


def activation_path(facts):
    return safe_dir(facts['common_dir'], 'gitflow') / 'activation.json'


def load(facts):
    path = activation_path(facts)
    if not path.exists():
        raise FlowError('policy_missing', '项目尚无已生效工作流；先接入或确认已有约定。')
    active = read_json(path)
    if not isinstance(active, dict) or set(active) != {'schema_version', 'mode', 'policy', 'sha256'} or active['schema_version'] != '1.0.0' or active['mode'] not in ('shared', 'local'):
        raise FlowError('activation_invalid', '工作流激活记录损坏。')
    policy = validate(active['policy'])
    if digest(policy) != active['sha256']:
        raise FlowError('activation_invalid', '工作流生效快照摘要不一致。')
    if active['mode'] == 'shared':
        candidate = safe_dir(facts['root'], '.gitflow') / 'workflow.json'
        # 某些分支尚未提交共享定义，仍使用公共目录里的已生效约定。
        if candidate.exists() and digest(validate(read_json(candidate))) != active['sha256']:
            raise FlowError('policy_drift', '项目定义已变化但尚未激活；当前动作需先复核规则修订。')
    return policy, active


def explanation(policy):
    lines = ['# 项目 Git 工作流', '', '此说明由 workflow.json 生成；JSON 是规则事实源。', '',
             f"工作流：{policy['profile']}；修订：{policy['revision']}；权威远端：{policy['primary_remote']}", '',
             '| 角色 | 名称/模式 | 长期必需 | 允许提交 | 来源角色 | 合入角色 |', '|---|---|---|---|---|---|']
    for key, role in policy['roles'].items():
        lines.append(f"| {key} | {role['name'] or role['pattern']} | {role['required']} | {role['allow_commit']} | {', '.join(role['create_from'])} | {', '.join(role['merge_into'])} |")
    return '\n'.join(lines) + '\n'


def write_activation(facts, policy, mode):
    for role in policy['roles'].values():
        if role['name'] and not valid_branch(facts['root'], role['name']):
            raise FlowError('policy_branch_name_invalid', '规则含 Git 不接受的固定分支名称。')
    active = {'schema_version': '1.0.0', 'mode': mode, 'policy': policy, 'sha256': digest(policy)}
    atomic_json(activation_path(facts), active)
    return active


def activate(path, apply=False):
    facts = require_repo(path)
    active_file = activation_path(facts)
    old = read_json(active_file) if active_file.exists() else None
    candidate = safe_dir(facts['root'], '.gitflow') / 'workflow.json'
    if candidate.exists():
        policy = validate(read_json(candidate))
        mode = 'shared'
    elif old and old.get('mode') == 'local':
        policy = validate(old['policy'])
        mode = 'local'
    else:
        raise FlowError('policy_candidate_missing', '未找到候选 workflow.json。')
    candidate_sha = digest(policy)
    markdown = safe_dir(facts['root'], '.gitflow/workflow.md') if mode == 'shared' else None
    if old and digest(policy) != old.get('sha256') and policy['revision'] <= old['policy']['revision']:
        # 修订号码由激活动作明确递增，不让候选旧号码偷换身份。
        policy['revision'] = old['policy']['revision'] + 1
    result = report('policy.activate', 'applied' if apply else 'preview', profile=policy['profile'],
                    revision=policy['revision'], policy_sha256=digest(policy))
    if apply:
        with locked(facts['common_dir']):
            current_old = read_json(active_file) if active_file.exists() else None
            if current_old != old or (mode == 'shared' and digest(validate(read_json(candidate))) != candidate_sha):
                raise FlowError('policy_changed', '候选或激活身份已变化，请重新预览。')
            if mode == 'shared':
                atomic_json(candidate, policy)
                if not markdown.exists() or old and markdown.read_text(encoding='utf-8') == explanation(old['policy']):
                    markdown.write_text(explanation(policy), encoding='utf-8')
                else:
                    result['markdown_preserved'] = True
            write_activation(facts, policy, mode)
    return result
