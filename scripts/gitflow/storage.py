"""受管 JSON 读写：路径边界、原子替换与跨进程互斥。"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile

from .git import FlowError


def read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 256 * 1024:
        raise FlowError('state_file_invalid', '配置或状态不是受限普通文件。')
    try:
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ValueError('duplicate key')
                result[key] = value
            return result
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)
    except (OSError, ValueError, UnicodeError) as exc:
        raise FlowError('state_json_invalid', '配置或状态 JSON 损坏。') from exc


def safe_dir(base, relative):
    base = Path(base).resolve()
    target = base / relative
    if not target.resolve().is_relative_to(base):
        raise FlowError('state_path_escape', '受管路径越出仓库或 Git 目录。')
    current = base
    for piece in Path(relative).parts:
        current = current / piece
        if current.is_symlink():
            raise FlowError('state_symlink', '受管目录不能通过符号链接写入。')
    return target


def atomic_json(path, value):
    path = Path(path)
    if path.is_symlink():
        raise FlowError('state_symlink', '不能替换符号链接状态文件。')
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()
    fd, name = tempfile.mkstemp(prefix='.write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextmanager
def locked(base):
    """只在显式变更时创建锁，不让只读查询写入。"""
    try:
        import fcntl
    except ImportError as exc:
        raise FlowError('platform_unsupported', '写操作当前需要 POSIX 文件锁。') from exc
    directory = safe_dir(base, 'gitflow')
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / 'state.lock'
    if lock.is_symlink():
        raise FlowError('state_symlink', '锁文件不能是符号链接。')
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise FlowError('operation_busy', '另一 GitFlow 操作占用此仓库，请稍后复核。') from exc
        yield
    finally:
        os.close(fd)
