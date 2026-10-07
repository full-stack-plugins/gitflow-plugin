"""真实临时仓库验证命令执行、副作用与可恢复日志。"""
import json
from pathlib import Path
from test_core import GitTestCase

class OperationTests(GitTestCase):
    def ready(self):
        self.repository()
        self.activate(mode='local')
        self.git('branch', 'develop')

    def test_create_preview_and_recorded_origin(self):
        self.ready()
        self.cli('branch', self.path, '--operation', 'create', '--name', 'feature/123-login', '--source', 'develop')
        self.assertNotIn('feature/123-login', self.git('branch', '--format=%(refname:short)'))
        self.cli('branch', self.path, '--operation', 'create', '--name', 'feature/123-login', '--source', 'develop', '--apply')
        self.assertEqual(self.git('branch', '--show-current'), 'main')
        audit=self.cli('audit', self.path)
        self.assertFalse(any(r['code']=='branch_origin_unknown' for r in audit['observations']))

    def test_wrong_base_and_invalid_name_are_rejected(self):
        self.ready()
        self.cli('branch', self.path, '--operation', 'create', '--name', 'feature/login', '--source', 'main', '--apply', code=1)
        self.cli('branch', self.path, '--operation', 'create', '--name', '@{-1}', '--source', 'develop', '--apply', code=1)

    def test_dirty_switch_refused_without_losing_changes(self):
        self.ready()
        (self.path/'app.txt').write_text('dirty\n')
        self.cli('branch', self.path, '--operation', 'switch', '--name', 'develop', '--apply', code=3)
        self.assertEqual((self.path/'app.txt').read_text(),'dirty\n')
        self.assertEqual(self.git('branch','--show-current'),'main')

    def test_reconcile_only_creates_missing_long_term_branch(self):
        self.repository(); self.activate(mode='local')
        self.cli('branch',self.path,'--operation','reconcile','--apply')
        self.assertEqual(set(self.git('branch','--format=%(refname:short)').splitlines()),{'main','develop'})

    def test_delete_rejects_protected_or_unmerged_branch(self):
        self.ready()
        self.cli('branch',self.path,'--operation','delete','--name','develop','--apply',code=1)
        self.git('switch','-c','feature/new','develop')
        (self.path/'new.txt').write_text('new');self.git('add','.');self.git('commit','-m','new')
        self.git('switch','main')
        self.cli('branch',self.path,'--operation','delete','--name','feature/new','--target','develop','--apply',code=1)

    def test_rename_validates_and_preserves_commit(self):
        self.ready();self.git('branch','feature/old','develop')
        before=self.git('rev-parse','feature/old')
        self.cli('branch',self.path,'--operation','rename','--source','feature/old','--name','feature/new','--apply')
        self.assertEqual(self.git('rev-parse','feature/new'),before)

    def test_sync_push_fetch_pull_real_bare_remote(self):
        self.ready()
        remote=self.path.parent/'remote.git'
        self.git('init','--bare',str(remote))
        self.git('remote','add','origin',str(remote))
        self.cli('sync',self.path,'--operation','push','--remote','origin','--target','main','--apply')
        self.assertEqual(self.git('ls-remote','origin','refs/heads/main').split()[0],self.git('rev-parse','main'))
        self.cli('sync',self.path,'--operation','fetch','--remote','origin','--apply')
        self.cli('sync',self.path,'--operation','pull','--remote','origin','--target','main','--apply')

    def test_merge_and_rebase_execute_allowed_directions(self):
        self.ready();self.git('switch','-c','feature/new','develop')
        (self.path/'new.txt').write_text('new');self.git('add','.');self.git('commit','-m','new')
        self.cli('sync',self.path,'--operation','rebase','--target','develop','--apply')
        source=self.git('rev-parse','HEAD')
        self.git('switch','develop')
        self.cli('sync',self.path,'--operation','merge','--source','feature/new','--apply')
        self.assertEqual(self.git('merge-base','HEAD',source),source)

    def test_release_finish_integrates_both_targets_and_is_idempotent(self):
        self.ready()
        self.cli('release',self.path,'--operation','start','--name','release/1.0.0','--source','develop','--apply')
        self.git('switch','release/1.0.0');(self.path/'release.txt').write_text('release')
        self.git('add','.');self.git('commit','-m','release')
        source=self.git('rev-parse','HEAD')
        self.cli('release',self.path,'--operation','finish','--name','release/1.0.0','--apply')
        for target in ('main','develop'):
            self.assertEqual(self.git('merge-base',source,target),source)
        before=self.git('rev-parse','main');self.cli('release',self.path,'--operation','finish','--name','release/1.0.0','--apply')
        self.assertEqual(self.git('rev-parse','main'),before)
        self.assertEqual(self.git('branch','--show-current'),'release/1.0.0')

    def test_recovery_preserves_original_commit_and_requires_target(self):
        self.ready();self.git('switch','-c','feature/wrong','develop')
        (self.path/'fix.txt').write_text('fix');self.git('add','.');self.git('commit','-m','fix')
        before=self.git('rev-parse','HEAD');self.git('branch','feature/right','develop')
        self.cli('recovery',self.path,'--operation','move-commit','--target','feature/right','--commit',before,'--apply')
        self.assertEqual(self.git('rev-parse','feature/wrong'),before)
        self.assertTrue((self.path/'fix.txt').exists())

    def test_recovery_moves_dirty_changes_without_stash_drop(self):
        self.ready();self.git('branch','feature/right','develop');(self.path/'app.txt').write_text('dirty')
        self.cli('recovery',self.path,'--operation','move-changes','--target','feature/right','--apply')
        self.assertEqual(self.git('branch','--show-current'),'feature/right')
        self.assertEqual((self.path/'app.txt').read_text(),'dirty')

    def test_journal_has_before_after_and_recovery_diagnoses(self):
        self.ready();r=self.cli('branch',self.path,'--operation','create','--name','feature/log','--source','develop','--apply')
        journal=Path(self.git('rev-parse','--absolute-git-dir'))/'gitflow'/'journal.json'
        entries=json.loads(journal.read_text())['entries']
        self.assertEqual(entries[-1]['id'],r['operation_id'])
        self.assertEqual(entries[-1]['status'],'complete')
        self.assertIn('head',entries[-1]['before']);self.assertIn('head',entries[-1]['after'])
        self.cli('recovery',self.path,'--operation','diagnose')
