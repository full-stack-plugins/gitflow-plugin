"""固定摘要组织快照：只在显式导入时获取，不在检查时联网。"""
import copy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.error import URLError

from .git import FlowError, report, require_repo
from .rules import validate_rules
from .storage import locked, safe_dir

LIMIT = 256 * 1024


def document(raw):
    """有界 JSON，拒绝重复字段与非标准常量。"""
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate field')
            value[key] = item
        return value
    def constant(value):
        raise ValueError(value)
    if len(raw) > LIMIT:
        raise FlowError('organization_invalid', '规则文件超过 256 KiB。')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise FlowError('organization_invalid', '规则 JSON 损坏或含重复字段。') from exc


def validate_baseline(value):
    if not isinstance(value, dict) or set(value) != {'schema_version', 'rules', 'locked_rules'} or value['schema_version'] != '1.0.0':
        raise FlowError('organization_invalid', '组织基线字段或版本无效。')
    validate_rules(value['rules'])
    locked_rules = value['locked_rules']
    if not isinstance(locked_rules, list) or any(not isinstance(k, str) or k not in value['rules'] for k in locked_rules) or len(set(locked_rules)) != len(locked_rules):
        raise FlowError('organization_invalid', '锁定规则必须引用基线中的唯一规则。')
    return value


def validate_pointer(pointer):
    if pointer is None:
        return
    if not isinstance(pointer, dict) or set(pointer) != {'path', 'sha256'} or not isinstance(pointer['path'], str) or not re.fullmatch(r'\.gitflow/baselines/[a-z][a-z0-9-]{0,63}\.json', pointer['path']) or not isinstance(pointer['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', pointer['sha256']):
        raise FlowError('organization_reference_invalid', '组织基线需受限 .gitflow/baselines 路径与固定 SHA-256。')


def read_local(root, relative):
    path = safe_dir(root, relative)
    if not path.is_file() or path.stat().st_size > LIMIT:
        raise FlowError('organization_missing', '固定组织基线缺失或超过预算。')
    return path.read_bytes()


def resolve(policy, root=None, reader=None):
    """解析一次组织继承，返回独立有效规则，不改写项目定义。"""
    result = copy.deepcopy(policy)
    pointer = policy.get('extends')
    if pointer is None:
        return result
    validate_pointer(pointer)
    raw = reader(pointer['path']) if reader else read_local(root, pointer['path'])
    if hashlib.sha256(raw).hexdigest() != pointer['sha256']:
        raise FlowError('organization_digest_mismatch', '组织基线摘要变化，不能静默降级或更新。')
    baseline = validate_baseline(document(raw))
    for ident in baseline['locked_rules']:
        if ident in policy['rules'] and policy['rules'][ident] != baseline['rules'][ident]:
            raise FlowError('organization_rule_locked', ident + ' 已由组织锁定，项目不能覆盖。')
    result['rules'] = {**baseline['rules'], **policy['rules']}
    return result


def valid_https(url):
    parts = urlsplit(url)
    if parts.scheme != 'https' or not parts.hostname or parts.username is not None or parts.password is not None or parts.fragment:
        raise FlowError('organization_source_invalid', '网络来源必须是无凭据的 HTTPS URL。')


class SecureRedirect(HTTPRedirectHandler):
    """拒绝组织资源重定向降级或夹带 URL 凭据。"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        valid_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def import_baseline(path, source, name, sha256, apply=False):
    facts = require_repo(path)
    if not isinstance(source, str) or not source or len(source) > 4096 or not isinstance(name, str) or not re.fullmatch('[a-z][a-z0-9-]{0,63}', name) or not isinstance(sha256, str) or not re.fullmatch('[0-9a-f]{64}', sha256):
        raise FlowError('organization_import_invalid', '导入需要来源、受限名称和预期 SHA-256。')
    remote = bool(urlsplit(source).scheme)
    if remote:
        valid_https(source)
    relative = '.gitflow/baselines/' + name + '.json'
    target = safe_dir(facts['root'], relative)
    result = report('organization.import', 'applied' if apply else 'preview', source=source, target=relative, sha256=sha256, activated=False)
    if not apply:
        return result
    try:
        if remote:
            with build_opener(SecureRedirect()).open(Request(source, headers={'User-Agent': 'GitFlow-Policy-Import'}), timeout=15) as response:
                raw = response.read(LIMIT + 1)
        else:
            file = Path(source).expanduser().resolve()
            if not file.is_file() or file.stat().st_size > LIMIT:
                raise FlowError('organization_source_invalid', '本地组织文件不存在或超过预算。')
            raw = file.read_bytes()
    except (OSError, URLError) as exc:
        raise FlowError('organization_unavailable', '组织来源不可达；未修改生效规则。') from exc
    if len(raw) > LIMIT or hashlib.sha256(raw).hexdigest() != sha256:
        raise FlowError('organization_digest_mismatch', '导入文件超出预算或不匹配预期摘要。')
    validate_baseline(document(raw))
    with locked(facts):
        target = safe_dir(facts['root'], relative)
        if target.exists():
            if target.read_bytes() != raw:
                raise FlowError('organization_existing', '已有不同组织快照，使用新的名称，不能覆盖。')
            result['unchanged'] = True
        else:
            # 用排他创建避免覆盖；持锁完成文件持久化，失败保留明确错误。
            import os
            import tempfile
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix='.import-', dir=target.parent)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(raw); stream.flush(); os.fsync(stream.fileno())
                os.link(temporary, target)
            finally:
                Path(temporary).unlink(missing_ok=True)
    return result
