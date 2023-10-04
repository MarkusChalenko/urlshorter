"""01_initial-db

Revision ID: 3a55dd762dd4
Revises: 
Create Date: 2023-10-04 15:50:08.796791

"""
from typing import Sequence, Union

import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a55dd762dd4'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklisted_client',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('host', sqlalchemy_utils.types.ip_address.IPAddressType(length=50), nullable=True),
    sa.Column('until', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blacklisted_client_until'), 'blacklisted_client', ['until'], unique=False)
    op.create_table('shorted_url',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=1000), nullable=False),
    sa.Column('original', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('original'),
    sa.UniqueConstraint('value')
    )
    op.create_index(op.f('ix_shorted_url_created_at'), 'shorted_url', ['created_at'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=1000), nullable=False),
    sa.Column('password', sa.String(length=1000), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_created_at'), 'user', ['created_at'], unique=False)
    op.create_table('shorted_url_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('host', sa.String(length=100), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('user_agent', sa.String(length=1000), nullable=False),
    sa.Column('url_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['url_id'], ['shorted_url.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shorted_url_info_created_at'), 'shorted_url_info', ['created_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_shorted_url_info_created_at'), table_name='shorted_url_info')
    op.drop_table('shorted_url_info')
    op.drop_index(op.f('ix_user_created_at'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_shorted_url_created_at'), table_name='shorted_url')
    op.drop_table('shorted_url')
    op.drop_index(op.f('ix_blacklisted_client_until'), table_name='blacklisted_client')
    op.drop_table('blacklisted_client')
    # ### end Alembic commands ###