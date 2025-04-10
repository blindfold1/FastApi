"""yooo

Revision ID: 239f534d1bde
Revises: df8820553b25
Create Date: 2025-04-04 10:42:58.047000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "239f534d1bde"
down_revision = "df8820553b25"
branch_labels = None
depends_on = None


def upgrade():
    # Добавляем таблицу tracker
    op.create_table(
        "tracker",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("calories", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("carbs", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("fats", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("proteins", sa.Float(), nullable=False, server_default="0.0"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tracker_date"), "tracker", ["date"], unique=False)
    op.create_index(op.f("ix_tracker_id"), "tracker", ["id"], unique=False)
    op.create_index(op.f("ix_tracker_user_id"), "tracker", ["user_id"], unique=False)

    # Изменяем типы столбцов в таблице foods
    op.alter_column("foods", "calories", existing_type=sa.INTEGER(), type_=sa.Float())
    op.alter_column("foods", "carbs", existing_type=sa.INTEGER(), type_=sa.Float())
    op.alter_column("foods", "fats", existing_type=sa.INTEGER(), type_=sa.Float())
    op.alter_column("foods", "proteins", existing_type=sa.INTEGER(), type_=sa.Float())
    op.create_index(op.f("ix_foods_user_id"), "foods", ["user_id"], unique=False)

    # Добавляем столбец scope в таблицу users
    # Шаг 1: Добавляем столбец без ограничения NOT NULL
    op.add_column("users", sa.Column("scope", sa.String(length=255), nullable=True))
    # Шаг 2: Заполняем существующие записи значением по умолчанию
    op.execute("UPDATE users SET scope = 'user' WHERE scope IS NULL")
    # Шаг 3: Добавляем ограничение NOT NULL
    op.alter_column("users", "scope", nullable=False)


def downgrade():
    # Удаляем изменения в обратном порядке
    op.drop_column("users", "scope")
    op.drop_index(op.f("ix_foods_user_id"), table_name="foods")
    op.alter_column("foods", "proteins", existing_type=sa.Float(), type_=sa.INTEGER())
    op.alter_column("foods", "fats", existing_type=sa.Float(), type_=sa.INTEGER())
    op.alter_column("foods", "carbs", existing_type=sa.Float(), type_=sa.INTEGER())
    op.alter_column("foods", "calories", existing_type=sa.Float(), type_=sa.INTEGER())
    op.drop_index(op.f("ix_tracker_user_id"), table_name="tracker")
    op.drop_index(op.f("ix_tracker_id"), table_name="tracker")
    op.drop_index(op.f("ix_tracker_date"), table_name="tracker")
    op.drop_table("tracker")
