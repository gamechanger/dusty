import os
import pwd

def demote_to_user(user_name):
    def _demote():
        pw_record = pwd.getpwnam(user_name)
        user_gid = pw_record.pw_gid
        user_uid = pw_record.pw_uid
        os.setgid(user_gid)
        os.setuid(user_uid)
    return _demote
