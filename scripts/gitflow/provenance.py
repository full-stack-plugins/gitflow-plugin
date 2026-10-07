"""创建来源记录的结构与当前规则身份验证。"""
import re
from .git import FlowError, oid, run, valid_branch
from .policy import role_for
from .storage import read_json
from .layout import state_file


def well_formed(value):
    return (isinstance(value,dict) and set(value)=={'source','oid','role','policy_sha256'}
            and all(isinstance(x,str) for x in value.values())
            and bool(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',value['oid']))
            and bool(re.fullmatch(r'[0-9a-f]{64}',value['policy_sha256'])))


def read_origins(facts, strict=True):
    path=state_file(facts, 'origins.json')
    items=read_json(path) if path.exists() else {}
    if not isinstance(items,dict):raise FlowError('origins_invalid','来源记录必须是分支映射，变更前恢复可信结构。')
    if strict and any(not isinstance(k,str) or not valid_branch(facts['root'],k) or not well_formed(v) for k,v in items.items()):
        raise FlowError('origins_invalid','来源记录字段损坏，不能在写操作后才发现。')
    return state_file(facts, 'origins.json', reading=False),items


def trusted(facts,policy,active,name,value):
    if not well_formed(value) or value['policy_sha256']!=active['sha256'] or value['role']!=role_for(policy,name):return False
    if not valid_branch(facts['root'],value['source']):return False
    sr=role_for(policy,value['source'])
    if sr not in policy['roles'][value['role']]['create_from']:return False
    if oid(facts['root'],value['oid'])!=value['oid'] or facts['shallow']:return False
    return run(facts['root'],'merge-base','--is-ancestor',value['oid'],'refs/heads/'+name,check=False).returncode==0
