"""new_activity_logic

Revision ID: bef9d1e7c356
Revises: e7250acb6b7c
Create Date: 2024-08-23 20:37:08.421868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bef9d1e7c356'
down_revision: Union[str, None] = 'e7250acb6b7c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Создаем временный столбец для хранения названий активностей
    op.add_column('tg_user_activity', sa.Column('activity_name_temp', sa.String(), nullable=True))

    # Выполняем запрос для копирования данных из таблицы activity в новый столбец activity_name_temp
    op.execute('''
        UPDATE tg_user_activity
        SET activity_name_temp = (
            SELECT name FROM activity
            WHERE activity.id = tg_user_activity.activity_id
        )
    ''')

    # Удаляем столбец activity_id и constraint
    op.drop_constraint('tg_user_activity_activity_id_fkey', 'tg_user_activity', type_='foreignkey')
    op.drop_column('tg_user_activity', 'activity_id')

    # Переименовываем временный столбец в activity_name и делаем его not nullable
    op.alter_column('tg_user_activity', 'activity_name_temp', new_column_name='activity_name', nullable=False)

    # Удаляем таблицу activity, так как она больше не нужна
    op.drop_table('activity')
    # ### end Alembic commands ###


def downgrade() -> None:
    # Восстанавливаем таблицу activity
    activity_table = op.create_table('activity',
                                     sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                                     sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                                     sa.PrimaryKeyConstraint('id', name='activity_pkey')
                                     )

    # Вставляем записи с указанными ID
    op.bulk_insert(activity_table, [
        {'id': 100000, 'name': 'go to menu'},
        {'id': 110000, 'name': 'go to speaking'},
        {'id': 111000, 'name': 'start speaking'},
        {'id': 112000, 'name': 'end speaking'},
        {'id': 120000, 'name': 'go to writing'},
        {'id': 121000, 'name': 'start writing'},
        {'id': 122000, 'name': 'end writing'},
        {'id': 130000, 'name': 'go to balance'},
        {'id': 140000, 'name': 'go to pricing'},
        {'id': 141000, 'name': 'buy points'},
        {'id': 142000, 'name': 'spent point'},
        {'id': 150000, 'name': 'response generated'},
        {'id': 180000, 'name': 'use gpt request'},
        {'id': 190000, 'name': 'use voice request'},
    ])

    # Добавляем столбец activity_id обратно в tg_user_activity, но пока nullable
    op.add_column('tg_user_activity', sa.Column('activity_id', sa.INTEGER(), nullable=True))

    # Восстанавливаем данные в столбце activity_id на основе значений из activity_name
    op.execute('''
        UPDATE tg_user_activity
        SET activity_id = (
            SELECT id FROM activity
            WHERE activity.name = tg_user_activity.activity_name
        )
    ''')

    # Делаем столбец activity_id NOT NULL после обновления всех данных
    op.alter_column('tg_user_activity', 'activity_id', nullable=False)

    # Восстанавливаем foreign key constraint
    op.create_foreign_key('tg_user_activity_activity_id_fkey', 'tg_user_activity', 'activity', ['activity_id'], ['id'])

    # Удаляем столбец activity_name
    op.drop_column('tg_user_activity', 'activity_name')
