# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from ggrc import db
from .models import Role


def _find_basic(role_name):
    return db.session.query(Role).filter(Role.name == role_name).first()


# System Roles


def auditor_reader():
    return _find_basic('AuditorReader')


def reader():
    return _find_basic('Reader')


def creator():
    return _find_basic('Creator')


def program_creator():
    return _find_basic('ProgramCreator')


def editor():
    return _find_basic('Editor')


def program_basic_reader():
    return _find_basic('ProgramBasicReader')


# Private Program Roles


def program_owner():
    return _find_basic('ProgramOwner')


def program_editor():
    return _find_basic('ProgramEditor')


def program_reader():
    return _find_basic('ProgramReader')


def auditor_program_reader():
    return _find_basic('AuditorProgramReader')


# Audit Roles


def program_audit_owner():
    return _find_basic('ProgramAuditOwner')


def program_audit_editor():
    return _find_basic('ProgramAuditEditor')


def program_audit_reader():
    return _find_basic('ProgramAuditReader')


def auditor():
    return _find_basic('Auditor')
