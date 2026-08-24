"""Ordinary-user registration orchestration."""

from __future__ import annotations

from application.accounts import CreateHumanAccountCommand, CreateHumanAccountHandler
from domain.enums import Role

from .command import RegisterUserCommand
from .result import RegisterUserResult


class RegisterUserHandler:
    """Create one active ordinary-user account atomically."""

    __slots__ = ("_create_human_account_handler",)

    def __init__(
        self,
        create_human_account_handler: CreateHumanAccountHandler,
    ) -> None:
        self._create_human_account_handler = create_human_account_handler

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        """Register an ordinary user inside the caller-owned transaction."""
        account = await self._create_human_account_handler.execute(
            CreateHumanAccountCommand(
                username=command.username,
                nickname=command.nickname,
                password=command.password,
                role=Role.USER,
                audit_context=command.audit_context,
            ),
        )
        return RegisterUserResult(
            id=account.id,
            username=account.username,
            nickname=account.nickname,
            role=account.role,
        )
