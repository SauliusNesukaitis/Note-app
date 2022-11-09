"""Add password_hash col to user

Revision ID: 607cb296d986
Revises: 
Create Date: 2022-11-09 18:22:56.709448

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '607cb296d986'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.drop_column('users', 'password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.VARCHAR(length=128), nullable=True))
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###
