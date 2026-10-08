"""确定性的元数据规则：闭合配置、逐条结果与不产生副作用的修正建议。"""
import re
from .git import FlowError


CATALOG = {
    'GF001': {'name': 'commit.conventional', 'scope': 'message', 'defaults': {'types': ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert'], 'allow_merge': True}},
    'GF002': {'name': 'commit.subject_length', 'scope': 'message', 'defaults': {'min_length': 1, 'max_length': 72}},
    'GF101': {'name': 'author.name', 'scope': 'author', 'defaults': {'pattern': r'[^\r\n<>]+'}},
    'GF102': {'name': 'author.email', 'scope': 'author', 'defaults': {'pattern': r'[^\s@]+@[^\s@]+'}},
    'GF103': {'name': 'commit.signoff', 'scope': 'message', 'defaults': {}},
    'GF104': {'name': 'commit.ai_disclosure', 'scope': 'message', 'defaults': {'mode': 'ignore'}},
    'GF401': {'name': 'tag.format', 'scope': 'tag', 'defaults': {'pattern': r'v[0-9]+\.[0-9]+\.[0-9]+'}},
}
AI = re.compile(r'\b(claude|cursor|copilot|chatgpt|codex|gemini|windsurf|aider|devin)\b|anthropic[.]com', re.I)


def validate_rules(value):
    """只接受已知规则及有界参数；off 不能掩盖配置错误。"""
    if not isinstance(value, dict) or set(value) - set(CATALOG):
        raise FlowError('rule_config_invalid', '存在未知规则或规则配置不是对象。')
    for ident, config in value.items():
        if not isinstance(config, dict) or set(config) - {'severity', 'options'} or config.get('severity') not in ('off', 'warn', 'error'):
            raise FlowError('rule_config_invalid', ident + ' 严重级别或字段无效。')
        options = config.get('options', {})
        defaults = CATALOG[ident]['defaults']
        if not isinstance(options, dict) or set(options) - set(defaults):
            raise FlowError('rule_config_invalid', ident + ' 存在未知参数。')
        opts = {**defaults, **options}
        if ident == 'GF001':
            if type(opts['allow_merge']) is not bool or not isinstance(opts['types'], list) or not 1 <= len(opts['types']) <= 32 or any(not isinstance(x, str) or not re.fullmatch('[a-z][a-z0-9-]{0,31}', x) for x in opts['types']) or len(set(opts['types'])) != len(opts['types']):
                raise FlowError('rule_config_invalid', 'GF001 提交类型或 merge 选项无效。')
        elif ident == 'GF002':
            if any(type(opts[k]) is not int for k in ('min_length', 'max_length')) or not 1 <= opts['min_length'] <= opts['max_length'] <= 4096:
                raise FlowError('rule_config_invalid', 'GF002 标题长度范围无效。')
        elif ident == 'GF104':
            if opts['mode'] not in ('ignore', 'forbid', 'disclose'):
                raise FlowError('rule_config_invalid', 'GF104 AI 声明模式无效。')
        elif 'pattern' in options:
            # 与旧自定义表达式相同：有界模式，避免多重无界回溯。
            from .policy import check_pattern
            pattern = opts['pattern']
            if not isinstance(pattern, str):
                raise FlowError('rule_config_invalid', ident + ' 表达式必须是字符串。')
            check_pattern(pattern)
    return value


def trailer_values(message):
    """读取尾部 trailer 段；正文里的同名文字不充当声明。"""
    block = message.rstrip().rsplit('\n\n', 1)[-1]
    pairs = []
    for line in block.splitlines():
        match = re.fullmatch(r'([A-Za-z][A-Za-z-]*):\s*(\S.*)', line)
        if not match:
            return []
        pairs.append((match[1].lower(), match[2]))
    return pairs


def evaluate(policy, context, scopes=('message', 'author')):
    """返回全部规则的状态；不适用和未配置规则明确 skipped。"""
    configured = policy.get('rules', {})
    validate_rules(configured)
    output = []
    for ident, definition in CATALOG.items():
        config = configured.get(ident, {'severity': 'off'})
        severity = config['severity']
        options = {**definition['defaults'], **config.get('options', {})}
        item = {'rule_id': ident, 'name': definition['name'], 'severity': severity, 'status': 'skipped',
                'actual': None, 'expected': options, 'message': '未启用或不适用于此检查。', 'suggestion': None, 'fix': None}
        output.append(item)
        if severity == 'off' or definition['scope'] not in scopes:
            continue
        required = {'message': ['message'], 'author': ['author_name' if ident == 'GF101' else 'author_email'], 'tag': ['tags']}[definition['scope']]
        if ident == 'GF103':
            required += ['author_name', 'author_email']
        if any(context.get(k) is None for k in required):
            item.update(status='unverified', message='缺少检查所需元数据。', suggestion='补充明确提交身份或候选消息后重新检查。')
            continue
        message = context.get('message', '')
        if not isinstance(message, str) or len(message) > 4096 or any(not isinstance(context[k], str) or len(context[k]) > 4096 for k in required if k != 'tags'):
            item.update(status='unverified', message='元数据类型或长度超出预算。')
            continue
        passed, fix, suggestion = True, None, None
        if definition['scope'] == 'message':
            item['actual'] = message
            subject = message.splitlines()[0] if message.splitlines() else ''
            trailers = trailer_values(message)
            if ident == 'GF001':
                match = re.fullmatch(r'([A-Za-z][A-Za-z0-9-]*)(\([^\r\n()]+\))?(!)?: (\S.*)', subject)
                merge = options['allow_merge'] and subject.startswith('Merge ')
                passed = merge or bool(match and match[1] in options['types'])
                suggestion = '使用 type(scope)!: 描述；类型取自允许列表。'
                if not passed and match and match[1].lower() in options['types']:
                    fix = match[1].lower() + message[len(match[1]):]
            elif ident == 'GF002':
                passed = options['min_length'] <= len(subject) <= options['max_length']
                suggestion = '保留标题核心意图，将详细说明移到正文；不自动截断语义。'
            elif ident == 'GF103':
                identity = f"{context['author_name']} <{context['author_email']}>"
                passed = ('signed-off-by', identity) in trailers
                suggestion = '由真实作者确认后添加 Signed-off-by；此项不验证密码学签名。'
            elif ident == 'GF104':
                attribution = any(AI.search(value) for key, value in trailers if key in ('assisted-by', 'co-authored-by', 'co-developed-by', 'signed-off-by')) or any(AI.search(line) and re.search(r'generated (?:with|by)|assisted (?:with|by)', line, re.I) for line in message.splitlines())
                if options['mode'] == 'forbid':
                    passed = not attribution
                elif options['mode'] == 'disclose':
                    passed = any(key == 'assisted-by' for key, _ in trailers) and not any(key in ('co-authored-by', 'co-developed-by', 'signed-off-by') and AI.search(value) for key, value in trailers)
                suggestion = '按项目约定声明工具辅助；不要把工具作为真实作者或签署人。'
        elif definition['scope'] == 'author':
            actual = context[required[0]]
            item['actual'] = actual
            passed = re.fullmatch(options['pattern'], actual) is not None
            suggestion = '核实真实作者身份及项目约定，不自动伪造或更换身份。'
        else:
            tags = context['tags']
            if not isinstance(tags, list) or len(tags) > 256 or any(not isinstance(t, str) or len(t) > 240 for t in tags):
                item.update(status='unverified', message='标签类型或数量超出预算。')
                continue
            item['actual'] = tags
            if not tags:
                item['message'] = '此提交没有标签。'
                continue
            passed = all(re.fullmatch(options['pattern'], tag) for tag in tags)
            suggestion = '发布前按项目规则选择标签名；不自动移动已发布标签。'
        item.update(status='pass' if passed else 'fail', message='符合规则。' if passed else ident + ' 不符合项目规则。',
                    suggestion=None if passed else suggestion, fix=fix)
    return output


def decision(checks):
    if any(x['status'] == 'unverified' for x in checks):
        return 'unverified'
    return 'deny' if any(x['status'] == 'fail' and x['severity'] == 'error' for x in checks) else 'allow'


def reasons(checks):
    return [{'code': c['rule_id'], 'message': c['message'], 'suggestion': c['suggestion'], 'fix': c['fix']}
            for c in checks if c['status'] == 'unverified' or (c['status'] == 'fail' and c['severity'] == 'error')]
