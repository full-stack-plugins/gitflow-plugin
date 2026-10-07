"""观察式日志恢复：只在 Git 实际结果能证明目标完成时确认，不重放命令。"""
from .git import FlowError, oid, report, require_repo, run, text
from .policy import load, role_for
from .provenance import read_origins
from .layout import state_file
from .storage import atomic_json, locked, read_json, safe_dir


def resume(path,operation_id=None,apply=False):
    facts=require_repo(path);policy,active=load(facts)
    file=state_file(facts, 'journal.json')
    journal=read_json(file) if file.exists() else {'entries':[]}
    if not operation_id:
        return report('recovery.resume',facts=facts,journal=journal,
                      next_actions=[{'action':'select_operation_id','message':'不重放命令；选择操作 ID 以核验实际完成状态。'}])
    if apply and (facts['dirty'] or facts['operation_states']):raise FlowError('recovery_state_pending','先处理未提交修改或中断状态，再确认完成。')
    def verify():
        records=[e for e in journal.get('entries',[]) if isinstance(e,dict) and e.get('id')==operation_id]
        if len(records)!=1:raise FlowError('operation_id_unknown','操作 ID 不属于当前工作树日志。')
        entry=records[0]
        if entry.get('policy_sha256')!=active['sha256']:raise FlowError('policy_changed','原操作规则修订不同，需要人工复核，不能自动确认。')
        commands=entry.get('commands');steps=entry.get('steps')
        if not isinstance(commands,list) or not isinstance(steps,list) or not commands:raise FlowError('operation_proof_missing','日志缺少可核验执行计划。')
        _,origins=read_origins(facts)
        for index,command in enumerate(commands):
            if not isinstance(command,list) or not command:raise FlowError('operation_proof_missing','日志命令结构无效。')
            step=steps[index] if index<len(steps) and isinstance(steps[index],dict) else {}
            if command[0]=='switch':continue
            if command[0]=='merge' and command[-1].startswith('refs/heads/'):
                source=step.get('source_oid');target=step.get('before',{}).get('branch')
                if not source or not target or run(path,'merge-base','--is-ancestor',source,'refs/heads/'+target,check=False).returncode!=0:
                    raise FlowError('operation_not_proven','目标尚不能证明包含原来源提交。')
            elif command[0]=='branch' and len(command)==3 and command[1] not in ('-d','-m'):
                record=origins.get(command[1])
                if not record or oid(path,'refs/heads/'+command[1])!=record['oid'] or record['policy_sha256']!=active['sha256']:
                    raise FlowError('operation_not_proven','新分支及来源记录未能证明创建完成。')
            elif command[0]=='cherry-pick' and len(command)==2:
                commit=command[1];target=step.get('before',{}).get('branch')
                if not target:raise FlowError('operation_proof_missing','迁移目标缺失。')
                contained=run(path,'merge-base','--is-ancestor',commit,'refs/heads/'+target,check=False).returncode==0
                equivalent=text(path,'cherry','refs/heads/'+target,commit,commit+'^')
                if not contained and not equivalent.startswith('- '):raise FlowError('operation_not_proven','目标尚不能证明包含原提交或等价补丁。')
            elif command[0]=='push' and len(command)==4 and command[1]=='--no-follow-tags' and ':' in command[3]:
                source,target=command[3].split(':',1)
                before=entry.get('before',{}).get('ref_oids',{})
                expected=before.get(source.removeprefix('refs/heads/'))
                observed=text(path,'ls-remote',command[2],target).split()
                if not expected or not observed or observed[0]!=expected:raise FlowError('operation_not_proven','实际远端引用尚不能证明原推送完成。')
            else:raise FlowError('operation_proof_unsupported','此命令的完成证明需要明确人工恢复方案，不能自动确认或重放。')
        if commands[-1][0]=='switch' and facts['branch']!=commands[-1][1]:raise FlowError('return_branch_pending','原计划末尾返回分支尚未完成。')
        return entry
    result=report('recovery.resume','applied' if apply else 'preview',operation_id=operation_id,replayed=False)
    if apply:
        with locked(facts):
            file=state_file(facts, 'journal.json')
            journal=read_json(file);entry=verify()
            entry['status']='complete';entry['resolution']='observed_complete';entry['after']=require_repo(path)
            atomic_json(file,journal)
    else:verify()
    return result
