"""组织快照的信任、导入授权及只读诊断边界。"""
import hashlib
import json
from test_policy_rules import RuleCase


class OrganizationPolicyTests(RuleCase):
    def baseline(self, locked=True):
        value = {'schema_version': '1.0.0', 'rules': {'GF001': {'severity': 'error'}}, 'locked_rules': ['GF001'] if locked else []}
        raw = (json.dumps(value) + '\n').encode()
        source = self.path.parent / 'organization.json'
        source.write_bytes(raw)
        return source, hashlib.sha256(raw).hexdigest()

    def test_import_preview_and_apply_do_not_activate(self):
        self.configured({})
        source, digest = self.baseline()
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', digest)
        destination = self.path / '.gitflow/baselines/team.json'
        self.assertFalse(destination.exists())
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', digest, '--apply')
        self.assertEqual(destination.read_bytes(), source.read_bytes())
        self.check('bad message')  # import alone must not activate a rule

    def test_https_preview_does_not_connect(self):
        self.repository()
        self.cli('organization', self.path, '--source', 'https://127.0.0.1:1/unreachable', '--name', 'team', '--sha256', 'a'*64)
        self.assertFalse((self.path / '.gitflow').exists())

    def test_digest_and_existing_file_are_preserved(self):
        self.configured({})
        source, digest = self.baseline()
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', '0'*64, '--apply', code=3)
        self.assertFalse((self.path / '.gitflow/baselines/team.json').exists())
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', digest, '--apply')
        old = (self.path / '.gitflow/baselines/team.json').read_bytes()
        source.write_text('{"schema_version":"1.0.0","rules":{},"locked_rules":[]}')
        new_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', new_digest, '--apply', code=3)
        self.assertEqual((self.path / '.gitflow/baselines/team.json').read_bytes(), old)

    def test_locked_rule_and_tampered_baseline_cannot_weaken_policy(self):
        self.configured({})
        source, digest = self.baseline()
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', digest, '--apply')
        file = self.path / '.gitflow/workflow.json'
        policy = json.loads(file.read_text())
        policy['extends'] = {'path': '.gitflow/baselines/team.json', 'sha256': digest}
        file.write_text(json.dumps(policy))
        self.cli('policy', self.path, '--apply')
        self.check('bad message', code=1)
        r = self.cli('policy', self.path, '--operation', 'describe')
        self.assertEqual(r['rules']['GF001']['source'], 'organization')
        policy = json.loads(file.read_text())
        policy['rules'] = {'GF001': {'severity': 'off'}}
        file.write_text(json.dumps(policy))
        self.cli('policy', self.path, '--apply', code=3)
        policy['rules'] = {}; file.write_text(json.dumps(policy))
        (self.path / '.gitflow/baselines/team.json').write_text('{}')
        self.check('feat: valid', code=3)

    def test_doctor_is_readonly_and_does_not_claim_host_enforcement(self):
        self.configured({})
        before = self.git('status', '--porcelain')
        r = self.cli('doctor', self.path)
        self.assertEqual(r['integrations']['native_hooks']['status'], 'missing')
        self.assertEqual(r['integrations']['host_mcp']['status'], 'unverified')
        self.assertEqual(r['integrations']['server_protection']['status'], 'unverified')
        self.assertEqual(self.git('status', '--porcelain'), before)

    def test_missing_shared_definition_cannot_hide_missing_baseline(self):
        self.configured({})
        source, digest = self.baseline()
        self.cli('organization', self.path, '--source', source, '--name', 'team', '--sha256', digest, '--apply')
        file = self.path / '.gitflow/workflow.json'
        policy = json.loads(file.read_text());policy['extends'] = {'path': '.gitflow/baselines/team.json', 'sha256': digest}
        file.write_text(json.dumps(policy));self.cli('policy', self.path, '--apply')
        file.unlink();(self.path / '.gitflow/baselines/team.json').unlink()
        self.check('feat: candidate', code=3)

    def test_local_mode_keeps_resolved_snapshot_offline(self):
        self.repository()
        from test_core import ROOT
        source, digest = self.baseline()
        folder = self.path / '.gitflow/baselines';folder.mkdir(parents=True)
        (folder / 'team.json').write_bytes(source.read_bytes())
        policy = json.loads((ROOT / 'profiles/github-flow.json').read_text())
        policy.update(schema_version='2.0.0', rules={}, extends={'path': '.gitflow/baselines/team.json', 'sha256': digest})
        file = self.path / '.gitflow/workflow.json';file.write_text(json.dumps(policy))
        self.cli('init', self.path, '--mode', 'local', '--apply')
        file.unlink();(folder / 'team.json').unlink()
        self.git('switch', '-c', 'feature/local')
        self.check('bad message', code=1)
        self.check('feat: offline')
        r = self.cli('policy', self.path, '--operation', 'describe')
        self.assertEqual(r['rules']['GF001']['source'], 'snapshot')
